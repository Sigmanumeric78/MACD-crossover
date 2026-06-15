# MACD Crossover Strategy Backtesting Across vectorbt, Nautilus Trader, and MetaTrader 5

## Project Title

MACD Crossover Strategy Backtesting Across vectorbt, Nautilus Trader, and MetaTrader 5

## Project Overview

This project implements the same manually calculated MACD crossover strategy across three backtesting and trading environments:

- vectorbt
- Nautilus Trader
- MetaTrader 5

The goal is to compare implementation behavior across a vectorized Python framework, an event-driven Python trading engine, and the MetaTrader 5 Strategy Tester. The project prioritizes clear assumptions, reusable shared Python logic, and honest documentation of framework differences.

## Strategy Definition

- Instrument: EUR/USD
- Timeframe: H1
- Date range: 2024-01-01 to 2024-12-31
- Initial capital: 100000 USD
- Python trade size: 10000 EUR/USD units
- MT5 trade size: 0.10 lot
- Mode: long-only / flat
- Fast EMA period: 12
- Slow EMA period: 26
- Signal EMA period: 9
- MACD line: fast EMA minus slow EMA
- Signal line: EMA of the MACD line
- Entry: enter long when MACD crosses above the signal line
- Exit: exit to flat when MACD crosses below the signal line

The EMA uses SMA seeding: the first EMA value appears after `period` valid values and is seeded with the simple average of those values. Later EMA values use `alpha = 2 / (period + 1)`.

No built-in MACD or EMA indicators are used. The Python implementations avoid pandas `.ewm()`, TA-Lib, pandas-ta, vectorbt indicators, and Nautilus indicators. The MT5 Expert Advisor avoids built-in indicator handles and external indicator files.

Signals are generated after candle close. Execution is intended on the next bar open, or the equivalent event after a completed bar is received.

## Data Source and Preparation

The real dataset is ForexSB Historical Data `EURUSD60.csv`, normalized into the project schema.

- Raw source file: `data/raw/EURUSD60.csv`
- Processed Python file: `data/processed/EURUSD_H1_2024_clean.csv`
- MT5 import file: `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`
- Processed rows: 6250
- Processed date range: 2024-01-01 22:00:00 to 2024-12-31 21:00:00
- Processed columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`

Weekend and holiday gaps are normal for forex H1 data. The most common processed timestamp gap is 60 minutes, while larger gaps appear around market closures.

Prepare the processed CSV from the raw ForexSB file:

```bash
python data/prepare_eurusd_h1_data.py --source csv --input data/raw/EURUSD60.csv
```

The MT5 import CSV uses:

```text
Date, Time, Open, High, Low, Close, TickVolume, Volume, Spread
```

No timestamp shifting is applied. Project timestamps are treated as UTC/no-shift bar open times.

## Repository Structure

```text
macd-backtest-test/
├── README.md
├── MEMORY.md
├── .gitignore
├── requirements-vectorbt.txt
├── requirements-nautilus.txt
├── common/
│   ├── config.py
│   ├── macd.py
│   ├── data_loader.py
│   ├── signals.py
│   └── metrics.py
├── data/
│   ├── raw/EURUSD60.csv
│   ├── processed/EURUSD_H1_2024_clean.csv
│   ├── mt5_import/EURUSD_CUSTOM_H1_2024.csv
│   └── prepare_eurusd_h1_data.py
├── vectorbt_impl/
│   ├── run_vectorbt_backtest.py
│   ├── vectorbt_results.csv
│   └── vectorbt_trades.csv
├── nautilus_impl/
│   ├── macd_strategy.py
│   ├── run_nautilus_backtest.py
│   ├── nautilus_results.csv
│   └── nautilus_trades.csv
├── mt5_impl/
│   ├── MACD_Crossover_Manual.mq5
│   └── reports/
│       ├── mt5_report.html
│       └── mt5_results_summary.md
└── reports/
    ├── vectorbt_equity_curve.csv
    └── nautilus_equity_curve.csv
```

## Environment and Dependencies

Install vectorbt dependencies:

```bash
pip install -r requirements-vectorbt.txt
```

Install Nautilus Trader dependencies:

```bash
pip install -r requirements-nautilus.txt
```

This project was developed with Python 3.13 in the local environment. vectorbt required `NUMBA_DISABLE_JIT=1` to avoid a numba cache import issue in this environment; the vectorbt runner sets this before importing vectorbt.

MetaTrader 5 requires a separate MT5/MetaEditor installation. The Strategy Tester run was performed manually using the exported Expert Advisor and custom-symbol CSV.

## How to Run

Run vectorbt:

```bash
python vectorbt_impl/run_vectorbt_backtest.py
```

Run Nautilus Trader:

```bash
python nautilus_impl/run_nautilus_backtest.py
```

Run MT5 manually:

1. Compile `mt5_impl/MACD_Crossover_Manual.mq5` in MetaEditor.
2. Import `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv` into a custom symbol such as `EURUSD_CUSTOM`.
3. Run Strategy Tester:
   - Expert: `MACD_Crossover_Manual`
   - Symbol: `EURUSD_CUSTOM`
   - Timeframe: H1
   - Date range: 2024-01-01 to 2024-12-31
   - Initial deposit: 100000 USD
   - Lot size input: 0.10
   - Modeling mode: Open prices only
4. Save the MT5 report to `mt5_impl/reports/mt5_report.html`.
5. Record the manual MT5 results in `mt5_impl/reports/mt5_results_summary.md`.

## Results Summary

| Framework | Data | Trades | Total Return | Sharpe Ratio | Max Drawdown | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| vectorbt | REAL_CSV | 241 | -0.3863% | -0.9415 | -0.5761% | Vectorized signal portfolio |
| Nautilus Trader | REAL_CSV | 241 | -0.4280% | -6.1039 | -0.5740% | Event-driven; equity reconstructed from closed PnL |
| MetaTrader 5 | EURUSD_CUSTOM | 230 | -0.4325% | -1.23 | -0.65% | Manual Strategy Tester run; 16% history quality and 6106 bars |

These results are not profitable. They are included to compare implementations and execution behavior across frameworks.

## Framework-by-Framework Notes

vectorbt:

- Uses shared manual MACD logic from `common/macd.py`.
- Uses vectorized entries/exits from `common/signals.py`.
- Shifts signals by one bar and uses open prices for execution.
- Writes `vectorbt_impl/vectorbt_results.csv`, `vectorbt_impl/vectorbt_trades.csv`, and `reports/vectorbt_equity_curve.csv`.

Nautilus Trader:

- Implements manual EMA/MACD inside an event-driven Strategy subclass.
- Uses completed H1 bar events and submits market orders through a simulated venue.
- Uses a margin account for EUR/USD because the installed Nautilus API rejected `CurrencyPair` instruments on a single-currency cash account.
- Writes `nautilus_impl/nautilus_results.csv`, `nautilus_impl/nautilus_trades.csv`, and `reports/nautilus_equity_curve.csv`.
- The Nautilus equity curve is reconstructed from closed position PnL because a full bar-level equity curve was not exposed by the low-level report API used here.

MetaTrader 5:

- Uses `mt5_impl/MACD_Crossover_Manual.mq5`.
- Calculates EMA/MACD manually in MQL5.
- Runs through MT5 Strategy Tester on `EURUSD_CUSTOM`.
- Report is saved at `mt5_impl/reports/mt5_report.html`.
- No screenshot file is included.

## Why Results Differ

The implementations intentionally share the same strategy rules, but the frameworks execute and report differently:

- vectorbt uses vectorized signal arrays and shifted boolean masks.
- Nautilus Trader is event-driven and routes orders through a simulated trading venue.
- MetaTrader 5 uses Strategy Tester, custom-symbol processing, and its own order/fill engine.
- MT5 reported 6106 bars and 230 trades, while the Python processed CSV has 6250 rows and both Python frameworks report 241 trades.
- MT5 also reported History Quality of 16%, which limits direct numerical comparability.

The goal is implementation comparison, not perfect bit-level replication.

## Issues Encountered and Fixes

- Git repository was not initialized initially; fixed with `git init`.
- vectorbt import failed in this environment due numba cache behavior; fixed by setting `NUMBA_DISABLE_JIT=1` in the vectorbt runner.
- Real EUR/USD data was initially missing; fixed by using ForexSB Historical Data `EURUSD60.csv`.
- ForexSB CSV had no header; fixed by adding a fallback no-header parser to `data/prepare_eurusd_h1_data.py`.
- Nautilus installation and API details required package inspection; the runner uses a margin account for FX.
- Nautilus did not expose a full bar-level equity curve through the low-level report API used here; equity was reconstructed from closed position PnL.
- MT5 required a manual Strategy Tester run outside the Python/Linux workflow.
- MT5 screenshot is absent; the exported HTML Strategy Tester report is included.

## AI Tool Usage Notes

AI assistance was used for project scaffolding, implementation planning, code drafting, debugging, documentation drafting, and result interpretation. Verification was performed through actual terminal runs for the Python frameworks and through a manually produced MT5 Strategy Tester report.

Development decisions, commands, errors, fixes, and unresolved issues are recorded in `MEMORY.md`.

## Final Notes

The repository is ready for GitHub submission after staging and committing. The current result files are small enough to keep in the repository for this take-home style project. The main remaining limitation is that MT5 custom-symbol history quality and bar count differ from the Python processed dataset, so cross-framework comparisons should be interpreted as implementation-level comparisons rather than exact numerical replication.
