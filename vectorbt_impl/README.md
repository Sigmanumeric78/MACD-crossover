# vectorbt Implementation

This folder contains the vectorbt implementation of the manually calculated MACD crossover strategy.

## Run

Run from the project root:

```bash
python vectorbt_impl/run_vectorbt_backtest.py
```

## Data Requirement

The final backtest requires real EUR/USD H1 data at:

```text
data/processed/EURUSD_H1_2024_clean.csv
```

Expected columns:

```text
timestamp, open, high, low, close, volume
```

The current real CSV was normalized from ForexSB Historical Data `EURUSD60.csv` H1 data.

If the real CSV is missing, the script runs a deterministic synthetic smoke test only to validate code wiring. Smoke-test numbers are not final results and must not be used as final README evidence.

## Result Files

- `vectorbt_impl/vectorbt_results.csv`
- `vectorbt_impl/vectorbt_trades.csv`
- `reports/vectorbt_equity_curve.csv`

## Notes

- MACD and EMA values come from the shared manual logic in `common/macd.py`.
- Entries and exits come from `common/signals.py` and are shifted one bar for next-bar-open execution.
- The vectorbt runner sets `NUMBA_DISABLE_JIT=1` before importing vectorbt to avoid a numba cache issue in this environment.
