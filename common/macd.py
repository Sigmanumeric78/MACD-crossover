"""Manual MACD calculation utilities."""

import numpy as np
import pandas as pd

from .config import FAST_EMA_PERIOD, SIGNAL_EMA_PERIOD, SLOW_EMA_PERIOD


def _as_numeric_series(values):
    """Return values as a float Series while preserving an existing index."""
    if isinstance(values, pd.Series):
        series = values.copy()
    else:
        series = pd.Series(values)
    return pd.to_numeric(series, errors="coerce").astype(float)


def _validate_period(period, name="period"):
    if isinstance(period, bool) or not isinstance(period, int) or period <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def manual_ema(values, period):
    """Calculate an EMA manually without built-in EMA indicator functions.

    Built-in EMA indicator functions, pandas `.ewm()`, TA-Lib, pandas-ta,
    vectorbt indicators, Nautilus indicators, and other indicator libraries are
    not allowed for this project.

    The EMA uses SMA seeding: the first EMA value is the simple average of the
    first `period` non-NaN values, values before that seed are NaN, and later
    values use `EMA[t] = alpha * value[t] + (1 - alpha) * EMA[t-1]` with
    `alpha = 2 / (period + 1)`.

    If `values` is a pandas Series, the returned Series preserves its index.
    Otherwise, a default integer index is used.
    """
    _validate_period(period)
    series = _as_numeric_series(values)
    ema = pd.Series(np.nan, index=series.index, dtype=float)

    valid_values = series.dropna()
    if len(valid_values) < period:
        return ema

    alpha = 2.0 / (period + 1.0)
    seed_index = valid_values.index[period - 1]
    previous_ema = float(valid_values.iloc[:period].mean())
    ema.loc[seed_index] = previous_ema

    seed_position = series.index.get_loc(seed_index)
    if isinstance(seed_position, slice) or not np.isscalar(seed_position):
        raise ValueError("EMA input index must not contain duplicate labels.")

    for position in range(int(seed_position) + 1, len(series)):
        current_value = series.iloc[position]
        if pd.isna(current_value):
            continue
        previous_ema = alpha * float(current_value) + (1.0 - alpha) * previous_ema
        ema.iloc[position] = previous_ema

    return ema


def manual_macd(
    close,
    fast_period=FAST_EMA_PERIOD,
    slow_period=SLOW_EMA_PERIOD,
    signal_period=SIGNAL_EMA_PERIOD,
):
    """Calculate MACD and signal lines manually.

    Built-in MACD or EMA indicator functions are not allowed. This function
    uses `manual_ema` for the fast EMA, slow EMA, and signal EMA so all
    framework implementations can share the same indicator semantics.

    The signal EMA is calculated only on valid MACD values and then reindexed
    to the original close index.

    Returns a DataFrame with `fast_ema`, `slow_ema`, `macd`, `signal`, and
    `histogram` columns.
    """
    close_series = _as_numeric_series(close)

    fast_ema = manual_ema(close_series, fast_period)
    slow_ema = manual_ema(close_series, slow_period)
    macd_line = fast_ema - slow_ema

    valid_macd = macd_line.dropna()
    signal = manual_ema(valid_macd, signal_period).reindex(close_series.index)
    histogram = macd_line - signal

    return pd.DataFrame(
        {
            "fast_ema": fast_ema,
            "slow_ema": slow_ema,
            "macd": macd_line,
            "signal": signal,
            "histogram": histogram,
        },
        index=close_series.index,
    )
