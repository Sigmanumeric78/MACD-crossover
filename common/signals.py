"""Signal generation helpers for the MACD crossover strategy."""

import pandas as pd


def _as_series(values, name):
    if isinstance(values, pd.Series):
        return values.copy()
    return pd.Series(values, name=name)


def _paired_series(left, right, left_name, right_name):
    left_series = pd.to_numeric(_as_series(left, left_name), errors="coerce")
    right_series = pd.to_numeric(_as_series(right, right_name), errors="coerce")

    if len(left_series) != len(right_series):
        raise ValueError(f"`{left_name}` and `{right_name}` must have the same length.")

    if not left_series.index.equals(right_series.index):
        right_series = pd.Series(right_series.to_numpy(), index=left_series.index, name=right_name)

    return left_series, right_series


def generate_macd_cross_signals(macd_line, signal_line):
    """Generate long entry and flat exit signals from MACD crossovers.

    Entry is true when previous MACD is less than or equal to previous signal
    and current MACD is greater than current signal. Exit is true when previous
    MACD is greater than or equal to previous signal and current MACD is less
    than current signal. NaN comparisons resolve to false.
    """
    macd_series, signal_series = _paired_series(
        macd_line,
        signal_line,
        "macd_line",
        "signal_line",
    )

    previous_macd = macd_series.shift(1)
    previous_signal = signal_series.shift(1)

    entries = ((previous_macd <= previous_signal) & (macd_series > signal_series)).fillna(False)
    exits = ((previous_macd >= previous_signal) & (macd_series < signal_series)).fillna(False)

    return pd.DataFrame(
        {
            "entries": entries.astype(bool),
            "exits": exits.astype(bool),
        },
        index=macd_series.index,
    )


def shift_signals_to_next_bar(entries, exits):
    """Shift close-generated signals forward one bar for next-open execution.

    This implements the project assumption that signals are generated after the
    candle close and trades execute on the following bar open.
    """
    entry_series = _as_series(entries, "entries").fillna(False).astype(bool)
    exit_series = _as_series(exits, "exits").fillna(False).astype(bool)

    if len(entry_series) != len(exit_series):
        raise ValueError("`entries` and `exits` must have the same length.")

    if not entry_series.index.equals(exit_series.index):
        exit_series = pd.Series(exit_series.to_numpy(), index=entry_series.index, name="exits")

    shifted_entries = entry_series.shift(1, fill_value=False).fillna(False).astype(bool)
    shifted_exits = exit_series.shift(1, fill_value=False).fillna(False).astype(bool)

    return pd.DataFrame(
        {
            "entries": shifted_entries,
            "exits": shifted_exits,
        },
        index=entry_series.index,
    )
