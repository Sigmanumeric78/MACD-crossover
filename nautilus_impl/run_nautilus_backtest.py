"""Run the Nautilus Trader backtest for the manual MACD crossover strategy."""

from __future__ import annotations

import math
import sys
import traceback
from decimal import Decimal
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import (
    DATA_PATH,
    FAST_EMA_PERIOD,
    INITIAL_CASH,
    NAUTILUS_EQUITY_PATH,
    NAUTILUS_RESULTS_PATH,
    NAUTILUS_TRADES_PATH,
    SIGNAL_EMA_PERIOD,
    SLOW_EMA_PERIOD,
    SYMBOL,
    TIMEFRAME,
    TRADE_SIZE_UNITS,
)
from common.data_loader import load_ohlcv_csv
from common.metrics import calculate_max_drawdown, calculate_sharpe_ratio, calculate_total_return
from nautilus_impl.macd_strategy import ManualMACDCrossoverConfig
from nautilus_impl.macd_strategy import ManualMACDCrossoverStrategy

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.common.config import LoggingConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import AggregationSource
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Currency
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


DATA_MODE = "REAL_CSV"
VENUE_NAME = "SIM"
PERIODS_PER_YEAR = 24 * 365
NOTES = (
    "Nautilus event-driven backtest using completed H1 bar events. "
    "Equity curve is reconstructed from closed position PnL because a full "
    "bar-level account equity series was not exposed by the low-level report API."
)


def _write_status(message: str, details: str) -> None:
    path = PROJECT_ROOT / "nautilus_impl/nautilus_status.md"
    path.write_text(
        "# Nautilus Backtest Status\n\n"
        "Nautilus execution was blocked.\n\n"
        f"## Error\n\n{message}\n\n"
        f"## Details\n\n```text\n{details}\n```\n",
        encoding="utf-8",
    )


def _load_data() -> pd.DataFrame:
    path = PROJECT_ROOT / DATA_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Real processed CSV is missing at {DATA_PATH}. Complete Phase 2.6 first.",
        )

    data = load_ohlcv_csv(path)
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True).dt.tz_localize(None)
    return data


def _timestamp_ns(timestamp: pd.Timestamp) -> int:
    return int(pd.Timestamp(timestamp).tz_localize("UTC").value)


def _make_instrument(instrument_id: InstrumentId) -> CurrencyPair:
    usd = Currency.from_str("USD")
    eur = Currency.from_str("EUR")
    return CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol("EURUSD"),
        base_currency=eur,
        quote_currency=usd,
        price_precision=5,
        size_precision=0,
        price_increment=Price.from_str("0.00001"),
        size_increment=Quantity.from_int(1),
        min_quantity=Quantity.from_int(1),
        margin_init=Decimal("0"),
        margin_maint=Decimal("0"),
        maker_fee=Decimal("0"),
        taker_fee=Decimal("0"),
        ts_event=0,
        ts_init=0,
    )


def _make_bars(data: pd.DataFrame, bar_type: BarType, instrument: CurrencyPair) -> list[Bar]:
    bars = []
    for row in data.itertuples(index=False):
        ts_ns = _timestamp_ns(row.timestamp)
        bars.append(
            Bar(
                bar_type=bar_type,
                open=instrument.make_price(row.open),
                high=instrument.make_price(row.high),
                low=instrument.make_price(row.low),
                close=instrument.make_price(row.close),
                volume=Quantity.from_int(int(row.volume)),
                ts_event=ts_ns,
                ts_init=ts_ns,
            ),
        )
    return bars


def _safe_report(callable_report):
    try:
        return callable_report()
    except Exception:
        return pd.DataFrame()


def _positions_to_equity(
    positions_report: pd.DataFrame,
    start_timestamp: pd.Timestamp | None = None,
) -> pd.Series:
    if start_timestamp is None:
        initial_index = [0]
    else:
        initial_index = [pd.Timestamp(start_timestamp)]

    if positions_report.empty:
        return pd.Series([INITIAL_CASH], index=initial_index, dtype=float, name="equity")

    pnl_column = None
    for candidate in ["realized_pnl", "Realized PnL", "PnL", "pnl"]:
        if candidate in positions_report.columns:
            pnl_column = candidate
            break

    time_column = None
    for candidate in ["ts_closed", "closing_order_filled_ts", "Close Time", "closed_time"]:
        if candidate in positions_report.columns:
            time_column = candidate
            break

    if pnl_column is None:
        return pd.Series([INITIAL_CASH], index=initial_index, dtype=float, name="equity")

    pnl = pd.to_numeric(
        positions_report[pnl_column].astype(str).str.replace(" USD", "", regex=False),
        errors="coerce",
    ).fillna(0.0)
    equity = INITIAL_CASH + pnl.cumsum()

    if time_column is not None:
        index = pd.to_datetime(positions_report[time_column], errors="coerce")
        if index.notna().all():
            initial = pd.Series([INITIAL_CASH], index=initial_index, name="equity")
            closed_trade_equity = pd.Series(equity.to_numpy(), index=index, name="equity")
            return pd.concat([initial, closed_trade_equity])

    initial = pd.Series([INITIAL_CASH], name="equity")
    closed_trade_equity = pd.Series(equity.to_numpy(), name="equity")
    return pd.concat([initial, closed_trade_equity], ignore_index=True)


def _extract_end_value(
    result,
    positions_report: pd.DataFrame,
    start_timestamp: pd.Timestamp | None = None,
) -> float:
    try:
        balance = result.summary.get("account.SIM.balance.USD.total")
        if balance:
            return float(str(balance).replace(" USD", ""))
    except Exception:
        pass

    equity = _positions_to_equity(positions_report, start_timestamp)
    return float(equity.iloc[-1])


def _save_outputs(results: pd.DataFrame, trades: pd.DataFrame, equity_curve: pd.Series) -> None:
    results_path = PROJECT_ROOT / NAUTILUS_RESULTS_PATH
    trades_path = PROJECT_ROOT / NAUTILUS_TRADES_PATH
    equity_path = PROJECT_ROOT / NAUTILUS_EQUITY_PATH

    results_path.parent.mkdir(parents=True, exist_ok=True)
    trades_path.parent.mkdir(parents=True, exist_ok=True)
    equity_path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(results_path, index=False)
    trades.to_csv(trades_path, index=False)
    equity_curve.rename("equity").to_csv(equity_path, index_label="timestamp")


def run_backtest() -> None:
    data = _load_data()

    venue = Venue(VENUE_NAME)
    instrument_id = InstrumentId(Symbol("EURUSD"), venue)
    instrument = _make_instrument(instrument_id)
    bar_type = BarType(
        instrument_id,
        BarSpecification(1, BarAggregation.HOUR, PriceType.LAST),
        AggregationSource.EXTERNAL,
    )
    bars = _make_bars(data, bar_type, instrument)

    strategy = ManualMACDCrossoverStrategy(
        ManualMACDCrossoverConfig(
            instrument_id=instrument_id,
            bar_type=bar_type,
            trade_size=Decimal(str(TRADE_SIZE_UNITS)),
            fast_period=FAST_EMA_PERIOD,
            slow_period=SLOW_EMA_PERIOD,
            signal_period=SIGNAL_EMA_PERIOD,
        ),
    )

    usd = Currency.from_str("USD")
    engine = BacktestEngine(BacktestEngineConfig(logging=LoggingConfig(log_level="ERROR")))
    try:
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.MARGIN,
            starting_balances=[Money(INITIAL_CASH, usd)],
            base_currency=usd,
            default_leverage=Decimal("1"),
            bar_execution=True,
            trade_execution=False,
        )
        engine.add_instrument(instrument)
        engine.add_strategy(strategy)
        engine.add_data(bars)
        engine.run()

        result = engine.get_result()
        positions_report = _safe_report(engine.trader.generate_positions_report)
        fills_report = _safe_report(engine.trader.generate_order_fills_report)
        account_report = _safe_report(lambda: engine.trader.generate_account_report(venue=venue))

        trades = positions_report if not positions_report.empty else fills_report
        equity_curve = _positions_to_equity(positions_report, data["timestamp"].min())
        start_value = float(INITIAL_CASH)
        end_value = _extract_end_value(result, positions_report, data["timestamp"].min())
        total_return = float(end_value / start_value - 1.0)

        sharpe_ratio = math.nan
        max_drawdown = math.nan
        if len(equity_curve.dropna()) >= 2:
            try:
                total_return = calculate_total_return(equity_curve)
                sharpe_ratio = calculate_sharpe_ratio(equity_curve.pct_change(), PERIODS_PER_YEAR)
                max_drawdown = calculate_max_drawdown(equity_curve)
            except Exception:
                pass

        number_of_trades = int(len(positions_report)) if not positions_report.empty else int(strategy.entries)
        results = pd.DataFrame(
            [
                {
                    "framework": "nautilus_trader",
                    "symbol": SYMBOL,
                    "timeframe": TIMEFRAME,
                    "start_date": data["timestamp"].min(),
                    "end_date": data["timestamp"].max(),
                    "data_mode": DATA_MODE,
                    "initial_cash": INITIAL_CASH,
                    "trade_size_units": TRADE_SIZE_UNITS,
                    "total_return": total_return,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown,
                    "number_of_trades": number_of_trades,
                    "start_value": start_value,
                    "end_value": end_value,
                    "fees": 0.0,
                    "slippage": 0.0,
                    "bars_processed": strategy.bars_seen,
                    "entries": strategy.entries,
                    "exits": strategy.exits,
                    "notes": NOTES,
                }
            ]
        )

        _save_outputs(results, trades, equity_curve)

        print("NAUTILUS BACKTEST COMPLETE")
        print(f"Data mode: {DATA_MODE}")
        print(f"Rows: {len(data)}")
        print(f"Date range: {data['timestamp'].min()} to {data['timestamp'].max()}")
        print(f"Bars processed: {strategy.bars_seen}")
        print(f"Entries: {strategy.entries}")
        print(f"Exits: {strategy.exits}")
        print(f"Total Return: {total_return:.6f}")
        print(f"Sharpe Ratio: {sharpe_ratio:.6f}" if not math.isnan(sharpe_ratio) else "Sharpe Ratio: NaN")
        print(f"Max Drawdown: {max_drawdown:.6f}" if not math.isnan(max_drawdown) else "Max Drawdown: NaN")
        print(f"Number of Trades: {number_of_trades}")
        print(f"Results saved to: {NAUTILUS_RESULTS_PATH}")
        print(f"Trades saved to: {NAUTILUS_TRADES_PATH}")
        print(f"Equity curve saved to: {NAUTILUS_EQUITY_PATH}")
        print(f"Notes: {NOTES}")

        if account_report.empty:
            print("Account report: unavailable or empty")
    finally:
        engine.dispose()


def main() -> int:
    try:
        run_backtest()
        return 0
    except Exception as exc:
        details = traceback.format_exc()
        _write_status(type(exc).__name__ + ": " + str(exc), details)
        print("NAUTILUS BACKTEST FAILED")
        print(type(exc).__name__ + ":", exc)
        print("Status saved to: nautilus_impl/nautilus_status.md")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
