"""Nautilus Trader strategy for the manual MACD crossover system."""

from __future__ import annotations

from decimal import Decimal

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class ManualMACDCrossoverConfig(StrategyConfig, frozen=True):
    """Configuration for the manual MACD crossover strategy."""

    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9


class _ManualEma:
    """Incremental EMA using the project SMA seed rule."""

    def __init__(self, period: int) -> None:
        if not isinstance(period, int) or period <= 0:
            raise ValueError("EMA period must be a positive integer.")

        self.period = period
        self.alpha = 2.0 / (period + 1.0)
        self._seed_values: list[float] = []
        self.value: float | None = None

    def update(self, value: float | None) -> float | None:
        if value is None:
            return None

        numeric_value = float(value)
        if self.value is None:
            self._seed_values.append(numeric_value)
            if len(self._seed_values) < self.period:
                return None
            self.value = sum(self._seed_values[: self.period]) / self.period
            return self.value

        self.value = self.alpha * numeric_value + (1.0 - self.alpha) * self.value
        return self.value

    def reset(self) -> None:
        self._seed_values = []
        self.value = None


class ManualMACDCrossoverStrategy(Strategy):
    """Long-only manual MACD crossover strategy for Nautilus Trader."""

    def __init__(self, config: ManualMACDCrossoverConfig) -> None:
        super().__init__(config)

        self.instrument: Instrument | None = None
        self.fast_ema = _ManualEma(config.fast_period)
        self.slow_ema = _ManualEma(config.slow_period)
        self.signal_ema = _ManualEma(config.signal_period)

        self.bars_seen = 0
        self.entries = 0
        self.exits = 0
        self.last_macd: float | None = None
        self.last_signal: float | None = None
        self.position_open = False

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.config.instrument_id}")
            self.stop()
            return

        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        self.bars_seen += 1

        close = bar.close.as_double()
        fast = self.fast_ema.update(close)
        slow = self.slow_ema.update(close)
        if fast is None or slow is None:
            return

        macd = fast - slow
        signal = self.signal_ema.update(macd)
        if signal is None:
            return

        if self.last_macd is not None and self.last_signal is not None:
            crossed_above = self.last_macd <= self.last_signal and macd > signal
            crossed_below = self.last_macd >= self.last_signal and macd < signal

            if crossed_above and not self.position_open:
                self._submit_market(OrderSide.BUY)
                self.position_open = True
                self.entries += 1
            elif crossed_below and self.position_open:
                self._submit_market(OrderSide.SELL)
                self.position_open = False
                self.exits += 1

        self.last_macd = macd
        self.last_signal = signal

    def _submit_market(self, side: OrderSide) -> None:
        if self.instrument is None:
            return

        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def on_stop(self) -> None:
        self.cancel_all_orders(self.config.instrument_id)
        self.unsubscribe_bars(self.config.bar_type)

    def on_reset(self) -> None:
        self.fast_ema.reset()
        self.slow_ema.reset()
        self.signal_ema.reset()
        self.bars_seen = 0
        self.entries = 0
        self.exits = 0
        self.last_macd = None
        self.last_signal = None
        self.position_open = False
