"""Run the vectorbt backtest for the manual MACD crossover strategy."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

try:
    import vectorbt as vbt
except ModuleNotFoundError as exc:
    print("Missing dependency: vectorbt")
    print("Install vectorbt dependencies with: pip install -r requirements-vectorbt.txt")
    raise exc

from common.config import (
    DATA_PATH,
    INITIAL_CASH,
    SYMBOL,
    TIMEFRAME,
    TRADE_SIZE_UNITS,
    VECTORBT_EQUITY_PATH,
    VECTORBT_RESULTS_PATH,
    VECTORBT_TRADES_PATH,
)
from common.data_loader import load_ohlcv_csv
from common.macd import manual_macd
from common.metrics import (
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_total_return,
)
from common.signals import generate_macd_cross_signals, shift_signals_to_next_bar


EXPECTED_COLUMNS = "timestamp, open, high, low, close, volume"
FEES = 0.0
SLIPPAGE = 0.0
FREQ = "1h"
PERIODS_PER_YEAR = 24 * 365
REAL_CSV_MODE = "REAL_CSV"
SMOKE_TEST_MODE = "SMOKE_TEST_ONLY_NOT_FINAL"


def _make_synthetic_ohlcv() -> pd.DataFrame:
    """Create deterministic H1 OHLCV data for smoke-test wiring only."""
    np.random.seed(42)
    rows = 300
    timestamp = pd.date_range("2024-01-01 00:00:00", periods=rows, freq="h")
    trend = np.linspace(0.0, 0.018, rows)
    noise = np.random.normal(0.0, 0.0015, rows)
    close = 1.10 + trend + np.cumsum(noise * 0.15)
    open_ = np.r_[close[0], close[:-1]] + np.random.normal(0.0, 0.00025, rows)
    high = np.maximum(open_, close) + np.abs(np.random.normal(0.00045, 0.00015, rows))
    low = np.minimum(open_, close) - np.abs(np.random.normal(0.00045, 0.00015, rows))
    volume = np.random.randint(80, 180, rows)

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _load_data() -> tuple[pd.DataFrame, str, str]:
    data_path = PROJECT_ROOT / DATA_PATH
    if data_path.exists():
        data = load_ohlcv_csv(data_path)
        return data, REAL_CSV_MODE, "Real CSV data loaded from configured path."

    print("Real EURUSD H1 CSV is missing.")
    print(f"Expected path: {DATA_PATH}")
    print(f"Expected columns: {EXPECTED_COLUMNS}")
    print("Running a small synthetic smoke-test dataset only to validate code wiring.")

    return (
        _make_synthetic_ohlcv(),
        SMOKE_TEST_MODE,
        "Synthetic smoke-test wiring validation only; not final results.",
    )


def _prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    prepared = data.copy()
    prepared["timestamp"] = pd.to_datetime(prepared["timestamp"])
    prepared = prepared.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    prepared = prepared.set_index("timestamp")
    return prepared[["open", "high", "low", "close", "volume"]].astype(float)


def _extract_trades(portfolio: vbt.Portfolio) -> tuple[int, pd.DataFrame]:
    try:
        closed_trades = portfolio.trades.closed
        trades = closed_trades.records_readable.copy()
        return int(closed_trades.count()), trades
    except Exception:
        pass

    try:
        trades = portfolio.trades.records_readable.copy()
        return int(portfolio.trades.count()), trades
    except Exception:
        return 0, pd.DataFrame()


def _save_outputs(
    results: pd.DataFrame,
    trades: pd.DataFrame,
    equity_curve: pd.Series,
) -> None:
    results_path = PROJECT_ROOT / VECTORBT_RESULTS_PATH
    trades_path = PROJECT_ROOT / VECTORBT_TRADES_PATH
    equity_path = PROJECT_ROOT / VECTORBT_EQUITY_PATH

    results_path.parent.mkdir(parents=True, exist_ok=True)
    trades_path.parent.mkdir(parents=True, exist_ok=True)
    equity_path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(results_path, index=False)
    trades.to_csv(trades_path, index=False)
    equity_curve.rename("equity").to_csv(equity_path, index_label="timestamp")


def main() -> None:
    raw_data, data_mode, notes = _load_data()
    data = _prepare_data(raw_data)

    macd = manual_macd(data["close"])
    raw_signals = generate_macd_cross_signals(macd["macd"], macd["signal"])
    shifted_signals = shift_signals_to_next_bar(
        raw_signals["entries"],
        raw_signals["exits"],
    )

    execution_price = data["open"]
    entries = shifted_signals["entries"].reindex(execution_price.index).fillna(False).astype(bool)
    exits = shifted_signals["exits"].reindex(execution_price.index).fillna(False).astype(bool)

    portfolio = vbt.Portfolio.from_signals(
        close=execution_price,
        entries=entries,
        exits=exits,
        init_cash=INITIAL_CASH,
        size=TRADE_SIZE_UNITS,
        size_type="amount",
        fees=FEES,
        slippage=SLIPPAGE,
        freq=FREQ,
        direction="longonly",
        accumulate=False,
    )

    equity_curve = portfolio.value()
    valid_equity = equity_curve.dropna()
    start_value = float(valid_equity.iloc[0])
    end_value = float(valid_equity.iloc[-1])
    total_return = calculate_total_return(equity_curve)
    sharpe_ratio = calculate_sharpe_ratio(equity_curve.pct_change(), PERIODS_PER_YEAR)
    max_drawdown = calculate_max_drawdown(equity_curve)
    number_of_trades, trades = _extract_trades(portfolio)

    results = pd.DataFrame(
        [
            {
                "framework": "vectorbt",
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "start_date": data.index.min(),
                "end_date": data.index.max(),
                "data_mode": data_mode,
                "initial_cash": INITIAL_CASH,
                "trade_size_units": TRADE_SIZE_UNITS,
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "number_of_trades": number_of_trades,
                "start_value": start_value,
                "end_value": end_value,
                "fees": FEES,
                "slippage": SLIPPAGE,
                "notes": notes,
            }
        ]
    )

    _save_outputs(results, trades, equity_curve)

    print("VECTORBT BACKTEST COMPLETE")
    print(f"Data mode: {data_mode}")
    print(f"Rows: {len(data)}")
    print(f"Date range: {data.index.min()} to {data.index.max()}")
    print(f"Entries: {int(entries.sum())}")
    print(f"Exits: {int(exits.sum())}")
    print(f"Total Return: {total_return:.6f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.6f}")
    print(f"Max Drawdown: {max_drawdown:.6f}")
    print(f"Number of Trades: {number_of_trades}")
    print(f"Results saved to: {VECTORBT_RESULTS_PATH}")
    print(f"Trades saved to: {VECTORBT_TRADES_PATH}")
    print(f"Equity curve saved to: {VECTORBT_EQUITY_PATH}")

    if data_mode == SMOKE_TEST_MODE:
        print(
            "WARNING: This was a synthetic smoke test only. Do not use these numbers in the final README."
        )
        print(
            "Place real EURUSD H1 data at data/processed/EURUSD_H1_2024_clean.csv before final backtesting."
        )


if __name__ == "__main__":
    main()
