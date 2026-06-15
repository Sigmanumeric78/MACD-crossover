"""Shared utilities for the MACD backtesting comparison project."""

from .data_loader import load_ohlcv_csv, validate_ohlcv_columns
from .macd import manual_ema, manual_macd
from .metrics import (
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_total_return,
)
from .signals import generate_macd_cross_signals, shift_signals_to_next_bar

__all__ = [
    "manual_ema",
    "manual_macd",
    "load_ohlcv_csv",
    "validate_ohlcv_columns",
    "generate_macd_cross_signals",
    "shift_signals_to_next_bar",
    "calculate_total_return",
    "calculate_sharpe_ratio",
    "calculate_max_drawdown",
]
