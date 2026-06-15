"""Prepare real EUR/USD H1 data for the MACD backtest project."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import DATA_PATH, END_DATE, START_DATE, SYMBOL
from common.data_loader import load_ohlcv_csv


OUTPUT_PATH = PROJECT_ROOT / DATA_PATH
MT5_RAW_PATH = PROJECT_ROOT / "data/raw/EURUSD_H1_2024_mt5_raw.csv"
EXPECTED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
MIN_ROWS = 1000
PROJECT_START = pd.Timestamp(START_DATE)
PROJECT_END = pd.Timestamp(f"{END_DATE} 23:59:59")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare EUR/USD H1 data from MT5 or a downloaded CSV.",
    )
    parser.add_argument(
        "--source",
        choices=["mt5", "csv"],
        required=True,
        help="Data source mode: export from MetaTrader 5 or normalize a CSV.",
    )
    parser.add_argument(
        "--input",
        help="Raw CSV path for --source csv, for example data/raw/YOUR_FILE.csv.",
    )
    parser.add_argument(
        "--resample-h1",
        action="store_true",
        help="Resample input data to 1-hour OHLCV bars before saving.",
    )
    return parser.parse_args()


def _resolve_path(path: str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved
    return resolved


def load_forexsb_csv(path: Path) -> pd.DataFrame:
    """Load a no-header Forex Strategy Builder OHLCV CSV file.

    ForexSB exports can be tab, space, comma, or semicolon separated. Supported
    layouts are either `date time open high low close volume` or
    `timestamp open high low close volume`.
    """
    raw = pd.read_csv(path, sep=r"[\t;, ]+", header=None, engine="python")
    raw = raw.dropna(axis=1, how="all")

    if raw.shape[1] == 7:
        timestamp = raw.iloc[:, 0].astype(str) + " " + raw.iloc[:, 1].astype(str)
        data = pd.DataFrame(
            {
                "timestamp": timestamp,
                "open": raw.iloc[:, 2],
                "high": raw.iloc[:, 3],
                "low": raw.iloc[:, 4],
                "close": raw.iloc[:, 5],
                "volume": raw.iloc[:, 6],
            }
        )
    elif raw.shape[1] == 6:
        data = pd.DataFrame(
            {
                "timestamp": raw.iloc[:, 0],
                "open": raw.iloc[:, 1],
                "high": raw.iloc[:, 2],
                "low": raw.iloc[:, 3],
                "close": raw.iloc[:, 4],
                "volume": raw.iloc[:, 5],
            }
        )
    else:
        raise ValueError(
            "Unsupported ForexSB CSV format. Expected either 7 columns "
            "`date time open high low close volume` or 6 columns "
            "`timestamp open high low close volume`."
        )

    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="raise")
    for column in ["open", "high", "low", "close", "volume"]:
        data[column] = pd.to_numeric(data[column], errors="raise")

    return (
        data[EXPECTED_COLUMNS]
        .sort_values("timestamp")
        .drop_duplicates(subset="timestamp", keep="last")
        .reset_index(drop=True)
    )


def _normalize_timestamps(series: pd.Series) -> pd.Series:
    timestamps = pd.to_datetime(series, errors="raise", utc=True)
    return timestamps.dt.tz_localize(None)


def _filter_date_range(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    filtered["timestamp"] = _normalize_timestamps(filtered["timestamp"])
    mask = (filtered["timestamp"] >= PROJECT_START) & (filtered["timestamp"] <= PROJECT_END)
    return filtered.loc[mask].reset_index(drop=True)


def _resample_to_h1(df: pd.DataFrame) -> pd.DataFrame:
    resampled = (
        df.set_index("timestamp")
        .sort_index()
        .resample("1h")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )
    return resampled


def _clean_final_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df[EXPECTED_COLUMNS].copy()
    cleaned["timestamp"] = _normalize_timestamps(cleaned["timestamp"])
    for column in ["open", "high", "low", "close", "volume"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    return (
        cleaned.sort_values("timestamp")
        .drop_duplicates(subset="timestamp", keep="last")
        .reset_index(drop=True)
    )


def _approx_timeframe_minutes(df: pd.DataFrame) -> float:
    if len(df) < 2:
        return float("nan")
    diffs = df["timestamp"].diff().dropna().dt.total_seconds() / 60.0
    if diffs.empty:
        return float("nan")
    return float(diffs.median())


def _validation_summary(df: pd.DataFrame) -> dict[str, object]:
    missing_ohlc = int(df[["open", "high", "low", "close"]].isna().sum().sum())
    return {
        "rows": len(df),
        "min_timestamp": df["timestamp"].min() if not df.empty else "N/A",
        "max_timestamp": df["timestamp"].max() if not df.empty else "N/A",
        "missing_ohlc_values": missing_ohlc,
        "approx_timeframe_minutes": _approx_timeframe_minutes(df),
        "output_path": OUTPUT_PATH.relative_to(PROJECT_ROOT),
    }


def _validate_final_data(df: pd.DataFrame) -> list[str]:
    errors = []
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append(f"Missing columns: {', '.join(missing_columns)}")
        return errors

    if len(df) < MIN_ROWS:
        errors.append(f"Expected at least {MIN_ROWS} rows for a full year of H1 forex bars.")

    if df["timestamp"].duplicated().any():
        errors.append("Duplicate timestamps found.")

    if not df["timestamp"].is_monotonic_increasing:
        errors.append("Timestamps are not strictly increasing.")

    if len(df) >= 2 and not (df["timestamp"].diff().dropna() > pd.Timedelta(0)).all():
        errors.append("Timestamps are not strictly increasing.")

    missing_ohlc = df[["open", "high", "low", "close"]].isna().sum().sum()
    if missing_ohlc:
        errors.append(f"Found {int(missing_ohlc)} missing OHLC values.")

    return errors


def _print_summary(summary: dict[str, object]) -> None:
    print(f"Rows: {summary['rows']}")
    print(f"Min timestamp: {summary['min_timestamp']}")
    print(f"Max timestamp: {summary['max_timestamp']}")
    print(f"Missing OHLC values: {summary['missing_ohlc_values']}")
    print(f"Detected approximate timeframe in minutes: {summary['approx_timeframe_minutes']}")
    print(f"Output path: {summary['output_path']}")


def _save_final_data(df: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)


def _validate_and_save(df: pd.DataFrame, source_label: str) -> int:
    final = _clean_final_data(_filter_date_range(df))
    summary = _validation_summary(final)
    errors = _validate_final_data(final)

    print(f"Source mode: {source_label}")
    _print_summary(summary)

    if errors:
        print("Validation failed. Final processed CSV was not overwritten.")
        for error in errors:
            print(f"- {error}")
        return 1

    _save_final_data(final)
    print("DATA PREPARATION COMPLETE")
    return 0


def prepare_from_mt5() -> int:
    try:
        import MetaTrader5 as mt5
    except ModuleNotFoundError:
        print("MetaTrader5 Python package is not installed.")
        print("Install only if using MT5 export mode: pip install MetaTrader5")
        return 1

    start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    if not mt5.initialize():
        print("MT5 initialization failed.")
        print(f"mt5.last_error(): {mt5.last_error()}")
        return 1

    try:
        rates = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_H1, start, end)
        last_error = mt5.last_error()
    finally:
        mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("MT5 returned no bars.")
        print(f"mt5.last_error(): {last_error}")
        return 1

    raw = pd.DataFrame(rates)
    raw["timestamp"] = pd.to_datetime(raw["time"], unit="s", utc=True).dt.tz_localize(None)
    MT5_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(MT5_RAW_PATH, index=False)
    print(f"MT5 raw data saved to: {MT5_RAW_PATH.relative_to(PROJECT_ROOT)}")

    normalized = raw.rename(columns={"tick_volume": "volume"})
    normalized = normalized[EXPECTED_COLUMNS]
    return _validate_and_save(normalized, "mt5")


def prepare_from_csv(input_path: str, resample_h1: bool) -> int:
    if not input_path:
        print("CSV mode requires --input data/raw/<RAW_FILE_NAME>.csv")
        return 2

    raw_path = _resolve_path(input_path)
    if not raw_path.exists():
        print(f"Input CSV not found: {raw_path}")
        return 1

    try:
        data = load_ohlcv_csv(raw_path)
        parser_label = "csv"
        print("CSV parser: header-based OHLCV parser")
    except Exception as exc:
        print(f"Header-based CSV parser failed: {exc}")
        print("Trying ForexSB no-header fallback parser.")
        data = load_forexsb_csv(raw_path)
        parser_label = "csv_forexsb_no_header"
        print("CSV parser: ForexSB no-header fallback parser")

    data = _filter_date_range(data)

    if resample_h1:
        data = _resample_to_h1(data)

    return _validate_and_save(data, parser_label)


def main() -> int:
    args = parse_args()
    if args.source == "mt5":
        return prepare_from_mt5()
    return prepare_from_csv(args.input, args.resample_h1)


if __name__ == "__main__":
    raise SystemExit(main())
