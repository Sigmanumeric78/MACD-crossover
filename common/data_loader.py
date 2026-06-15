"""Data loading and validation helpers for OHLCV input data."""

import pandas as pd


_TIMESTAMP_ALIASES = {"timestamp", "time", "date", "datetime"}
_VOLUME_ALIASES = {"volume", "tick_volume", "tickvolume"}
_OHLC_COLUMNS = ("open", "high", "low", "close")


def _normalized_key(column):
    return str(column).strip().lower()


def _find_column(columns, aliases):
    for column in columns:
        if _normalized_key(column) in aliases:
            return column
    return None


def load_ohlcv_csv(path):
    """Load, normalize, and clean OHLCV data from a CSV file.

    The returned DataFrame uses the normalized schema `timestamp`, `open`,
    `high`, `low`, `close`, and `volume`. Timestamps are parsed as datetimes,
    sorted ascending, and duplicate timestamps are dropped while keeping the
    last row.
    """
    df = pd.read_csv(path)
    normalized = validate_ohlcv_columns(df)

    try:
        normalized["timestamp"] = pd.to_datetime(normalized["timestamp"], errors="raise")
    except Exception as exc:
        raise ValueError("Unable to parse `timestamp` values as datetimes.") from exc

    return (
        normalized.sort_values("timestamp")
        .drop_duplicates(subset="timestamp", keep="last")
        .reset_index(drop=True)
    )


def validate_ohlcv_columns(df):
    """Validate and normalize OHLCV columns.

    Accepted timestamp aliases include `timestamp`, `time`, `date`,
    `datetime`, and `Date`. OHLC columns may be uppercase or lowercase. Accepted
    volume aliases include `volume`, `tick_volume`, `tickVolume`, and `Volume`;
    when volume is missing, it is created with zero values.

    Raises:
        ValueError: If timestamp or required OHLC columns are missing, or if
            OHLC columns cannot be converted to numeric values.
    """
    timestamp_column = _find_column(df.columns, _TIMESTAMP_ALIASES)
    if timestamp_column is None:
        raise ValueError(
            "Missing required timestamp column. Accepted names: timestamp, time, date, datetime, Date."
        )

    source_columns = {"timestamp": timestamp_column}
    missing_ohlc = []
    for column in _OHLC_COLUMNS:
        source_column = _find_column(df.columns, {column})
        if source_column is None:
            missing_ohlc.append(column)
        else:
            source_columns[column] = source_column

    if missing_ohlc:
        missing = ", ".join(missing_ohlc)
        raise ValueError(f"Missing required OHLC columns after normalization: {missing}.")

    volume_column = _find_column(df.columns, _VOLUME_ALIASES)
    normalized = pd.DataFrame(index=df.index)
    normalized["timestamp"] = df[source_columns["timestamp"]]

    for column in _OHLC_COLUMNS:
        try:
            normalized[column] = pd.to_numeric(df[source_columns[column]], errors="raise")
        except Exception as exc:
            raise ValueError(f"Column `{source_columns[column]}` must contain numeric values.") from exc

    if volume_column is None:
        normalized["volume"] = 0
    else:
        normalized["volume"] = pd.to_numeric(df[volume_column], errors="coerce").fillna(0)

    return normalized[["timestamp", "open", "high", "low", "close", "volume"]]
