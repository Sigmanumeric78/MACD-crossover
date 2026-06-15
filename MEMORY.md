# Project Memory

## Project Title

MACD Crossover Strategy Backtesting Across vectorbt, Nautilus Trader, and MetaTrader 5

## Objective

Implement the same manually calculated MACD crossover strategy across vectorbt, Nautilus Trader, and MetaTrader 5, then compare behavior and results across frameworks.

## Current Phase

Phase 0 - Repository Scaffold

## Initial Decisions

- Keep the project contained in `macd-backtest-test/`.
- Create only scaffold, documentation, config constants, and function stubs in Phase 0.
- Do not implement vectorbt, Nautilus Trader, or MetaTrader 5 strategy logic in Phase 0.
- Use shared `common/` modules for configuration, manual indicator calculations, data loading, signal generation, and metrics.
- Keep framework-specific implementation folders separate.
- Preserve final `reports/` folders in the repository structure; only temporary report artifacts should be ignored.

## Strategy Rules

- Manual EMA calculation is required.
- Built-in MACD or EMA indicator functions are not allowed in any implementation.
- Fast EMA period: 12.
- Slow EMA period: 26.
- Signal EMA period: 9.
- MACD line equals fast EMA minus slow EMA.
- Signal line equals EMA of the MACD line.
- Enter long when MACD crosses above the signal line.
- Exit to flat when MACD crosses below the signal line.
- Strategy is long-only.

## Data Assumptions

- Instrument: EUR/USD.
- Timeframe: 1-hour.
- Date range: 2024-01-01 to 2024-12-31.
- Initial capital: 100000 USD.
- Position sizing will use a fixed size, to be finalized later.
- Signals are generated after candle close.
- Trades execute on the next bar open.
- Raw market data will be placed under `data/raw/`.
- Processed data will be placed under `data/processed/`.
- Files prepared for MetaTrader 5 imports will be placed under `data/mt5_import/`.

## Framework Plan

- `vectorbt_impl/` will contain the vectorbt implementation in a later phase.
- `nautilus_impl/` will contain the Nautilus Trader implementation in a later phase.
- `mt5_impl/` will contain the MetaTrader 5 Expert Advisor and related reports in a later phase.
- Shared logic should remain in `common/` where practical to reduce cross-framework drift.

## Files Created In This Phase

- `README.md`
- `MEMORY.md`
- `.gitignore`
- `requirements-vectorbt.txt`
- `requirements-nautilus.txt`
- `common/__init__.py`
- `common/config.py`
- `common/macd.py`
- `common/data_loader.py`
- `common/signals.py`
- `common/metrics.py`
- `vectorbt_impl/README.md`
- `nautilus_impl/README.md`
- `mt5_impl/README.md`

## Directories Created In This Phase

- `data/raw/`
- `data/processed/`
- `data/mt5_import/`
- `vectorbt_impl/`
- `nautilus_impl/`
- `mt5_impl/reports/`
- `reports/`
- `common/`

## Commands Run

- `pwd`
- `rg --files -uu`
- `find . -maxdepth 2 -type d`
- `apply_patch` to create the Phase 0 scaffold files and initial project memory.
- `mkdir -p macd-backtest-test/data/raw macd-backtest-test/data/processed macd-backtest-test/data/mt5_import macd-backtest-test/mt5_impl/reports macd-backtest-test/reports`
- `apply_patch` to record the empty directory creation command in `MEMORY.md`.
- `apply_patch` to record final verification commands in `MEMORY.md`.
- `find macd-backtest-test -maxdepth 4 -print`
- `cat macd-backtest-test/MEMORY.md`
- `git status --short`
- `apply_patch` to record the `git status --short` result in `MEMORY.md`.

## Errors

- No implementation errors encountered.
- Note: initial workspace inspection commands were run before the scaffold files were created.
- `git status --short` returned `fatal: not a git repository (or any parent up to mount point /)`.

## Fixes

- No fixes were required in Phase 0.

## Assumptions

- The project root should be a new subdirectory named `macd-backtest-test/` under the current workspace.
- Empty data and report directories are part of the required scaffold even though they do not yet contain data or final reports.
- Dependency files are intentionally minimal and may be expanded in later phases.

## Unresolved Issues

- Fixed position size has not been finalized.
- Data source and CSV schema details have not been finalized.
- Spread, commission, slippage, and fill assumptions have not been finalized.
- Metric definitions may need to be aligned across frameworks during later phases.

## Current Status

Phase 0 scaffold files have been created. Strategy implementation has not started.

## Next Step

Begin Phase 1 only after confirmation. The likely next step is to define and implement shared manual EMA, MACD, signal, data validation, and metrics logic in `common/`.

## Phase 1 - Shared Manual Strategy Logic

### Files Modified

- `MEMORY.md`
- `mt5_impl/reports/mt5_results_summary.md`
- `README.md`
- `vectorbt_impl/README.md`
- `nautilus_impl/README.md`
- `mt5_impl/README.md`
- `README.md`
- `common/__init__.py`
- `common/macd.py`
- `common/data_loader.py`
- `common/signals.py`
- `common/metrics.py`

### Implementation Decisions

- Work is being performed from `/home/flynntag/Documents/macD/macd-backtest-test`.
- Git repository initialization was handled before implementation edits.
- Shared Phase 1 logic was implemented only in the existing `common/` modules.
- `manual_ema` accepts pandas Series, numpy arrays, and list-like input; pandas Series indexes are preserved.
- `manual_macd` returns a DataFrame with `fast_ema`, `slow_ema`, `macd`, `signal`, and `histogram`.
- `validate_ohlcv_columns` returns the normalized schema `timestamp`, `open`, `high`, `low`, `close`, `volume`.
- Missing volume is normalized to zero.
- Basic metrics ignore NaN values and return plain floats.

### EMA Seed Rule

- Implemented: first EMA value appears at the position of the `period`th non-NaN value. With no leading NaNs, this is index position `period - 1`.
- The seed value is the simple average of the first `period` non-NaN values.
- Values before the seed are NaN.
- Later EMA values use `alpha = 2 / (period + 1)` and `EMA[t] = alpha * value[t] + (1 - alpha) * EMA[t-1]`.
- Missing values after seeding produce NaN at that position and do not update the last EMA state.

### Signal Shifting Rule

- Implemented: close-generated entry and exit signals are shifted forward by one bar so execution occurs on the next bar open.
- Missing shifted values are filled with `False`.

### Commands Run

- `cat macd-backtest-test/MEMORY.md`
- `pwd`
- `git rev-parse --show-toplevel`
- `git init`
- `apply_patch` to add the Phase 1 memory section and record the Git check.
- `sed -n '1,220p' common/macd.py`
- `sed -n '1,220p' common/data_loader.py`
- `sed -n '1,220p' common/signals.py`
- `sed -n '1,220p' common/metrics.py`
- `sed -n '1,200p' common/__init__.py`
- `sed -n '1,260p' README.md`
- `sed -n '1,200p' common/config.py`
- `apply_patch` to implement shared Phase 1 helpers and lightly update `README.md`.
- `python - <<'PY' ... PY` inline sanity check covering `manual_ema`, `manual_macd`, signal generation, signal shifting, data validation/loading, and metrics.
- `apply_patch` to record Phase 1 sanity check results in `MEMORY.md`.
- `find . -maxdepth 3 -type d -name __pycache__ -print`
- `git status --short`
- `rm -rf common/__pycache__`
- `apply_patch` to record generated cache cleanup and final verification commands in `MEMORY.md`.
- `apply_patch` to adjust the final tree verification command to exclude Git internals.
- `apply_patch` to correct the final tree command so `.gitignore` remains visible.
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `git status --short`
- `cat MEMORY.md`

### Test Results

- Passed: `manual_ema([1, 2, 3, 4, 5], 3)` returns `[NaN, NaN, 2.0, 3.0, 4.0]`.
- Passed: `manual_macd` on an increasing close series from 1 to 100 returns the expected columns and matching length.
- Passed: `generate_macd_cross_signals` produced one entry and one exit on the hand-made MACD/signal series.
- Passed: `shift_signals_to_next_bar` moved a true signal at index `N` to index `N+1`.
- Passed: `validate_ohlcv_columns` normalized `Date`, `Open`, `High`, `Low`, `Close`, and `tick_volume` to `timestamp`, `open`, `high`, `low`, `close`, and `volume`.
- Passed: `load_ohlcv_csv` parsed timestamps, sorted ascending, dropped duplicate timestamps while keeping the last row, and reset the index.
- Passed: metrics helpers returned expected total return, non-NaN Sharpe ratio, and expected max drawdown on a small synthetic equity curve.
- Final inline output: `All Phase 1 sanity checks passed.`

### Errors Encountered

- `git rev-parse --show-toplevel` returned `fatal: not a git repository (or any parent up to mount point /)`.
- Fix: ran `git init` in `/home/flynntag/Documents/macD/macd-backtest-test`.
- Running inline Python generated `common/__pycache__`.
- Fix: removed `common/__pycache__` after sanity checks to keep the project tree clean.

### Unresolved Issues

- Framework-specific implementations are intentionally not started.
- Fixed position size, data source, CSV schema details beyond normalized OHLCV, spread, commission, slippage, and fill assumptions remain unresolved.

### Next Step

Begin Phase 2 only after confirmation. The likely next step is to implement the vectorbt backtest using the shared Phase 1 helpers.

## Phase 2 - vectorbt Backtest Runner

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `git status --short` shows all scaffold files as untracked because the repository was initialized in Phase 1 and no commits have been made.
- Phase 2 scope is vectorbt only. Nautilus Trader and MetaTrader 5 implementations remain untouched.

### Files Modified

- `MEMORY.md`
- `README.md`
- `common/config.py`
- `vectorbt_impl/README.md`
- `vectorbt_impl/run_vectorbt_backtest.py`

### Files Created

- `vectorbt_impl/run_vectorbt_backtest.py`
- `vectorbt_impl/vectorbt_results.csv`
- `vectorbt_impl/vectorbt_trades.csv`
- `reports/vectorbt_equity_curve.csv`

### Config Decisions

- Added `TRADE_SIZE_UNITS = 10000.0` for a fixed EUR/USD position size of 10,000 base currency units.
- Added `DATA_PATH = "data/processed/EURUSD_H1_2024_clean.csv"`.
- Added `VECTORBT_RESULTS_PATH = "vectorbt_impl/vectorbt_results.csv"`.
- Added `VECTORBT_TRADES_PATH = "vectorbt_impl/vectorbt_trades.csv"`.
- Added `VECTORBT_EQUITY_PATH = "reports/vectorbt_equity_curve.csv"`.
- Rationale: 10,000 units keeps vectorbt sizing simple and easier to compare later with MT5 0.10 lot.

### Data Mode Behavior

- Implemented: if `data/processed/EURUSD_H1_2024_clean.csv` exists, the runner uses `load_ohlcv_csv` and marks results as `REAL_CSV`.
- Implemented: if the real CSV is missing, the runner prints a clear warning and runs a deterministic in-memory synthetic smoke-test dataset marked as `SMOKE_TEST_ONLY_NOT_FINAL`.
- Synthetic smoke-test data uses 300 hourly candles starting at `2024-01-01 00:00:00`, numpy random seed 42, a mildly trending noisy close series, and generated OHLCV columns.
- Synthetic data is not written as a permanent input CSV.
- vectorbt uses shifted signals and the `open` series as execution price to match next-bar-open execution.

### Commands Run

- `pwd`
- `git status --short`
- `cat MEMORY.md`
- `apply_patch` to add the Phase 2 starting state to `MEMORY.md`.
- `apply_patch` to update config, add the vectorbt runner, update vectorbt README, lightly update root README, and record the changes in `MEMORY.md`.
- `python vectorbt_impl/run_vectorbt_backtest.py`
- `apply_patch` to record the missing `vectorbt` dependency error before installing requirements.
- `pip install -r requirements-vectorbt.txt`
- `pip install -r requirements-vectorbt.txt` with network escalation after DNS failure in the sandbox.
- `apply_patch` to record dependency installation results before rerunning the vectorbt runner.
- `python vectorbt_impl/run_vectorbt_backtest.py` after installing vectorbt.
- `python - <<'PY' ... PY` to test importing vectorbt with `NUMBA_DISABLE_JIT=1`.
- `apply_patch` to set `NUMBA_DISABLE_JIT=1` before importing vectorbt in the runner and record the import fix.
- `python vectorbt_impl/run_vectorbt_backtest.py` after applying the vectorbt import fix.
- `cat vectorbt_impl/vectorbt_results.csv`
- `sed -n '1,20p' vectorbt_impl/vectorbt_trades.csv`
- `sed -n '1,10p' reports/vectorbt_equity_curve.csv`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `find . -maxdepth 3 -type d -name '.numba*' -print`
- `rm -rf common/__pycache__`
- `apply_patch` to remove unused imports from `vectorbt_impl/run_vectorbt_backtest.py`.
- `apply_patch` to order standard-library imports and record final successful run details in `MEMORY.md`.
- `python vectorbt_impl/run_vectorbt_backtest.py` final rerun after cleanup.
- `rm -rf common/__pycache__` after the final rerun.
- `apply_patch` to record the final rerun and final verification commands in `MEMORY.md`.
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `git status --short`
- `cat vectorbt_impl/vectorbt_results.csv`
- `cat MEMORY.md`

### Errors Encountered

- First run of `python vectorbt_impl/run_vectorbt_backtest.py` failed because `vectorbt` was not installed.
- Exact error: `ModuleNotFoundError: No module named 'vectorbt'`.
- Script output before traceback: `Missing dependency: vectorbt` and `Install vectorbt dependencies with: pip install -r requirements-vectorbt.txt`.
- First `pip install -r requirements-vectorbt.txt` attempt failed due sandbox DNS resolution failure for `pypi.org`.
- Exact install error: `ERROR: Could not find a version that satisfies the requirement matplotlib (from versions: none)` and `ERROR: No matching distribution found for matplotlib`.
- After installation, `python vectorbt_impl/run_vectorbt_backtest.py` failed during vectorbt import inside numba caching.
- Exact runtime error: `RuntimeError: cannot cache function 'set_seed_nb': no locator available for file '/home/flynntag/.local/lib/python3.13/site-packages/vectorbt/utils/random_.py'`.

### Fixes Applied

- Reran `pip install -r requirements-vectorbt.txt` with network escalation.
- Install succeeded and installed `vectorbt-1.0.0`, `matplotlib-3.11.0`, and related dependencies.
- The install changed pandas in the active user environment from `3.0.3` to `2.3.3`, which pip selected while resolving vectorbt dependencies.
- Verified that `NUMBA_DISABLE_JIT=1` allows `import vectorbt` to succeed in this environment.
- Patched `vectorbt_impl/run_vectorbt_backtest.py` to set `NUMBA_DISABLE_JIT=1` before importing vectorbt.
- Removed generated `common/__pycache__` after script execution.
- Removed unused `START_DATE` and `END_DATE` imports from the vectorbt runner.
- Final rerun succeeded after cleanup.
- Removed generated `common/__pycache__` again after the final rerun.

### Output Summary

- Successful runner output used `SMOKE_TEST_ONLY_NOT_FINAL` because `data/processed/EURUSD_H1_2024_clean.csv` is missing.
- Rows: 300.
- Date range: `2024-01-01 00:00:00` to `2024-01-13 11:00:00`.
- Entries: 10.
- Exits: 10.
- Total Return: `0.000526`.
- Sharpe Ratio: `5.679035`.
- Max Drawdown: `-0.000292`.
- Number of Trades: 9.
- Results written to `vectorbt_impl/vectorbt_results.csv`.
- Trades written to `vectorbt_impl/vectorbt_trades.csv`.
- Equity curve written to `reports/vectorbt_equity_curve.csv`.
- These are synthetic smoke-test numbers only and must not be used as final README results.

### Unresolved Issues

- Real EUR/USD H1 CSV availability is not yet confirmed.
- Final vectorbt results remain pending until real EUR/USD H1 data is placed at `data/processed/EURUSD_H1_2024_clean.csv`.
- Nautilus Trader and MetaTrader 5 implementations are intentionally not started.

### Next Step

Begin Phase 3 only after confirmation. The likely next step is to implement Nautilus Trader or prepare real EUR/USD H1 data for final vectorbt results.

## Phase 2.5 - Real EUR/USD H1 Data Preparation

### Why This Phase Exists

- Phase 2 vectorbt execution currently works but falls back to `SMOKE_TEST_ONLY_NOT_FINAL` because `data/processed/EURUSD_H1_2024_clean.csv` is missing.
- This phase prepares a real EUR/USD H1 CSV at the required processed data path, then reruns the existing vectorbt backtest if real data becomes available.

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `git status --short` shows all project files as untracked because the repository has not been committed yet.
- Existing vectorbt smoke-test outputs are present from Phase 2.

### Data Source Priority

- Primary source: local MetaTrader 5 Python export using `copy_rates_range`.
- Rationale: MT5 bars come directly from the terminal and make later MetaTrader 5 Strategy Tester comparison easier.
- MT5 timestamps are handled as UTC/no-shift bar open timestamps.
- Fallback source: manually downloaded CSV from Dukascopy Historical Data Export, ForexSB, or HistData.
- Rationale: these are forex historical data sources that can be normalized into the project schema if MT5 is unavailable on this Linux environment.

### Files Created

- `data/prepare_eurusd_h1_data.py`

### Files Modified

- `MEMORY.md`
- `.gitignore`
- `README.md`

### Commands Run

- `pwd`
- `git status --short`
- `cat MEMORY.md`
- `apply_patch` to add the Phase 2.5 starting state and data source priority to `MEMORY.md`.
- `sed -n '1,260p' README.md`
- `sed -n '1,220p' .gitignore`
- `sed -n '1,220p' common/config.py`
- `sed -n '1,240p' common/data_loader.py`
- `apply_patch` to create `data/prepare_eurusd_h1_data.py`, update `.gitignore`, update README data preparation docs, and record the change in `MEMORY.md`.
- `python data/prepare_eurusd_h1_data.py --help`
- `python data/prepare_eurusd_h1_data.py --source mt5`
- `find data/raw -maxdepth 1 -type f -print`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `find data/processed -maxdepth 1 -type f -print`
- `rm -rf common/__pycache__`
- `apply_patch` to record Phase 2.5 check results and cleanup in `MEMORY.md`.
- `apply_patch` to record final Phase 2.5 verification commands in `MEMORY.md`.
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `git status --short`
- `find data/raw -maxdepth 1 -type f -print`
- `find data/processed -maxdepth 1 -type f -print`
- `cat MEMORY.md`

### MT5 Availability Issue

- MT5 export mode was attempted.
- Result: `MetaTrader5 Python package is not installed.`
- Script guidance printed: `Install only if using MT5 export mode: pip install MetaTrader5`.
- This is acceptable on the current Linux environment and no MT5 data was exported.

### CSV Input Used

- None.
- `find data/raw -maxdepth 1 -type f -print` returned no files, so there is no downloaded raw CSV available to normalize.

### Validation Results

- No real data validation was run because MT5 export failed and no raw CSV exists.

### Final Processed CSV

- `data/processed/EURUSD_H1_2024_clean.csv` does not exist.

### vectorbt REAL_CSV Rerun

- Not run in Phase 2.5 because no final processed real CSV exists.

### Errors Encountered

- MT5 mode failed cleanly because the `MetaTrader5` Python package is not installed.
- Running data preparation checks generated `common/__pycache__`.

### Fixes Applied

- Removed generated `common/__pycache__`.

### .gitignore Decision

- Added ignores for large raw market data downloads: `data/raw/*.zip` and `data/raw/*.bi5`.
- Did not ignore `data/processed/EURUSD_H1_2024_clean.csv` so the final cleaned one-year H1 CSV can be committed if small enough.

### Unresolved Issues

- Final real EUR/USD H1 data file is not yet prepared.
- MT5 is not available in this environment unless the `MetaTrader5` package and a usable terminal are installed.
- No fallback raw CSV is currently present in `data/raw/`.

### Next Step

Download or provide a real EUR/USD dataset, then run one of:

- `python data/prepare_eurusd_h1_data.py --source mt5`
- `python data/prepare_eurusd_h1_data.py --source csv --input data/raw/YOUR_FILE.csv`
- `python data/prepare_eurusd_h1_data.py --source csv --input data/raw/YOUR_M1_FILE.csv --resample-h1`

After `data/processed/EURUSD_H1_2024_clean.csv` exists, rerun `python vectorbt_impl/run_vectorbt_backtest.py` and confirm `Data mode: REAL_CSV`.

## Phase 2.6 - ForexSB EURUSD60 CSV Normalization and vectorbt REAL_CSV Run

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `git status --short` still shows the project files as untracked because no commit has been made.
- Raw file detected: `data/raw/EURUSD60.csv`.
- No processed real CSV was present in `data/processed/` at phase start.
- Scope remains data normalization and vectorbt rerun only; Nautilus Trader and MetaTrader 5 EA are not being implemented.

### Raw File Used

- `data/raw/EURUSD60.csv`.
- File size: 5.3M.
- First row observed: `2010-06-01 10:00 1.21266 1.21436 1.21185 1.21357 3720`.
- Last row observed: `2026-06-12 20:00 1.15712 1.15716 1.15641 1.15641 3252`.

### Data Source

- ForexSB Historical Data.

### File Format Detected

- No-header ForexSB H1 format.
- Actual separator observed: tab-delimited.
- Actual layout observed: `date time open high low close volume`.

### Resampling Used

- No. The downloaded `EURUSD60.csv` file is expected to already be H1 data.

### Parser Changes Made

- Added `load_forexsb_csv(path)` inside `data/prepare_eurusd_h1_data.py`.
- CSV mode now first tries the existing header-based `load_ohlcv_csv(path)`.
- If that fails, CSV mode tries the ForexSB fallback parser.
- The fallback supports tab, space, comma, or semicolon separators.
- The fallback supports both `date time open high low close volume` and `timestamp open high low close volume` layouts.
- The fallback normalizes to `timestamp`, `open`, `high`, `low`, `close`, `volume`, sorts ascending, drops duplicate timestamps keeping the last, and resets the index.

### Files Modified

- `data/prepare_eurusd_h1_data.py`
- `README.md`
- `vectorbt_impl/README.md`
- `MEMORY.md`

### Files Created

- `data/processed/EURUSD_H1_2024_clean.csv`

### Final Processed CSV Path

- `data/processed/EURUSD_H1_2024_clean.csv`

### Validation Results

- Processed CSV shape: `(6250, 6)`.
- Columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`.
- Min timestamp: `2024-01-01 22:00:00`.
- Max timestamp: `2024-12-31 21:00:00`.
- Duplicate timestamps: `0`.
- Missing OHLC values: `0`.
- Most common minute gap: `60.0` minutes with 6196 occurrences.
- Larger gaps are present due to normal forex weekend/holiday closures.

### vectorbt REAL_CSV Result Summary

- Data mode: `REAL_CSV`.
- Rows: 6250.
- Date range: `2024-01-01 22:00:00` to `2024-12-31 21:00:00`.
- Entries: 241.
- Exits: 242.
- Total Return: `-0.003863`.
- Sharpe Ratio: `-0.941478`.
- Max Drawdown: `-0.005761`.
- Number of Trades: 241.
- Results path: `vectorbt_impl/vectorbt_results.csv`.
- Trades path: `vectorbt_impl/vectorbt_trades.csv`.
- Equity curve path: `reports/vectorbt_equity_curve.csv`.

### Commands Run

- `pwd`
- `git status --short`
- `cat MEMORY.md`
- `find data/raw -maxdepth 1 -type f -print`
- `find data/processed -maxdepth 1 -type f -print`
- `apply_patch` to add the Phase 2.6 starting state to `MEMORY.md`.
- `ls -lh data/raw/EURUSD60.csv`
- `head -n 5 data/raw/EURUSD60.csv`
- `tail -n 5 data/raw/EURUSD60.csv`
- `sed -n '1,280p' data/prepare_eurusd_h1_data.py`
- `apply_patch` to add ForexSB no-header fallback parsing to `data/prepare_eurusd_h1_data.py` and record raw file inspection in `MEMORY.md`.
- `python data/prepare_eurusd_h1_data.py --source csv --input data/raw/EURUSD60.csv`
- `python - <<'PY' ... PY` validation snippet for the processed CSV.
- `python vectorbt_impl/run_vectorbt_backtest.py`
- `cat vectorbt_impl/vectorbt_results.csv`
- `sed -n '1,20p' vectorbt_impl/vectorbt_trades.csv`
- `sed -n '1,10p' reports/vectorbt_equity_curve.csv`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `rm -rf common/__pycache__`
- `sed -n '1,240p' README.md`
- `sed -n '1,220p' vectorbt_impl/README.md`
- `apply_patch` to update README, vectorbt README, and record normalization/validation/vectorbt results in `MEMORY.md`.
- `apply_patch` to record final Phase 2.6 verification commands in `MEMORY.md`.
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `git status --short`
- `python - <<'PY' ... PY` final processed CSV validation output.
- `cat vectorbt_impl/vectorbt_results.csv`
- `cat MEMORY.md`
- `apply_patch` to move the processed CSV memory entry from Phase 2.5 to Phase 2.6.

### Errors Encountered

- Header-based CSV parser failed on `EURUSD60.csv` because the file has no header.
- Exact parser message: `Missing required timestamp column. Accepted names: timestamp, time, date, datetime, Date.`
- Running normalization/vectorbt generated `common/__pycache__`.

### Fixes Applied

- CSV mode fell back to the new ForexSB no-header parser successfully.
- Removed generated `common/__pycache__`.

### Unresolved Issues

- Nautilus Trader implementation is intentionally not started.
- MetaTrader 5 EA implementation is intentionally not started.
- Cross-framework result comparison is pending.

### Next Step

Begin the next phase only after confirmation. The likely next step is Nautilus Trader implementation using the same processed `REAL_CSV` data and shared manual MACD logic.

## Phase 3 - Nautilus Trader Backtest Runner

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `data/processed/EURUSD_H1_2024_clean.csv` exists.
- `vectorbt_impl/vectorbt_results.csv` exists and reports `Data mode: REAL_CSV`.
- Vectorbt REAL_CSV summary from Phase 2.6: 6250 rows, date range `2024-01-01 22:00:00` to `2024-12-31 21:00:00`, 241 entries, 242 exits, total return `-0.003863`, Sharpe ratio `-0.941478`, max drawdown `-0.005761`, and 241 trades.
- Scope is Nautilus Trader only. MetaTrader 5 EA is not being implemented in this phase.

### Files Created

- `nautilus_impl/macd_strategy.py`
- `nautilus_impl/run_nautilus_backtest.py`
- `nautilus_impl/nautilus_results.csv`
- `nautilus_impl/nautilus_trades.csv`
- `reports/nautilus_equity_curve.csv`

### Files Modified

- `common/config.py`
- `README.md`
- `nautilus_impl/README.md`
- `MEMORY.md`

### Python/Nautilus Version and Import Status

- Python version: `Python 3.13.13`.
- Initial Nautilus import check: failed.
- Exact import error: `ModuleNotFoundError: No module named 'nautilus_trader'`.
- First sandboxed install command failed due DNS resolution for PyPI.
- Escalated install command succeeded.
- Installed Nautilus package: `nautilus_trader-1.228.0`.
- Installed supporting packages included `fsspec-2026.2.0`, `msgspec-0.21.1`, `portion-2.6.1`, `sortedcontainers-2.4.0`, and `uvloop-0.22.1`.
- Pip downgraded `fsspec` from `2026.3.0` to `2026.2.0`.
- Pip reported unrelated dependency warnings: `sentence-transformers 5.3.0 requires huggingface-hub>=0.20.0` and `pyiceberg 0.11.1 requires rich<15.0.0,>=10.11.0`.
- Nautilus import after installation: OK.
- Nautilus module path: `/home/flynntag/.local/lib/python3.13/site-packages/nautilus_trader/__init__.py`.

### Package Inspection Findings

- `nautilus_trader` package directory: `/home/flynntag/.local/lib/python3.13/site-packages/nautilus_trader`.
- Local search found `BacktestEngine` APIs under `nautilus_trader/backtest`.
- Local examples found standard Python strategy examples under `nautilus_trader/examples/strategies`, including `bb_mean_reversion.py`.
- `BacktestEngine` exposes `add_venue`, `add_instrument`, `add_strategy`, `add_data`, and `run`.
- Reports are available through `engine.trader.generate_account_report`, `generate_order_fills_report`, `generate_fills_report`, `generate_orders_report`, and `generate_positions_report`.
- `Bar`, `BarType`, `BarSpecification`, `CurrencyPair`, `Price`, `Quantity`, `Currency`, and `Money` constructors were inspected from installed docs.
- `Price(...)` does not accept a string directly; `Price.from_str(...)` should be used for string price increments and examples.
- A `CurrencyPair` cannot be added to a single-currency CASH account; the runner uses a MARGIN account for EUR/USD.

### Implementation Approach

- Create a Nautilus `Strategy` subclass named `ManualMACDCrossoverStrategy`.
- Use bar data only and subscribe to the configured H1 `BarType`.
- Maintain manual incremental EMA state inside the strategy using the same SMA seed rule as `common.macd.manual_ema`.
- Submit long-only market orders on MACD crossovers.
- Track `bars_seen`, `entries`, `exits`, `last_macd`, `last_signal`, and `position_open`.
- Use a fixed quantity of 10,000 EUR/USD units.

### Data Conversion Approach

- Load `data/processed/EURUSD_H1_2024_clean.csv` through `common.data_loader.load_ohlcv_csv`.
- Treat timestamps as UTC/no-shift bar open timestamps from the processed CSV.
- Convert pandas timestamps to UTC nanoseconds for Nautilus `Bar` objects.
- Create an EUR/USD `CurrencyPair` on venue `SIM` with instrument id `EURUSD.SIM`.
- Use externally aggregated `1-HOUR-LAST` bars.

### Commands Run

- `pwd`
- `git status --short`
- `cat MEMORY.md`
- `find data/processed -maxdepth 1 -type f -print`
- `cat vectorbt_impl/vectorbt_results.csv`
- `apply_patch` to add the Phase 3 starting state to `MEMORY.md`.
- `python --version`
- `python - <<'PY' ... PY` Nautilus import check.
- `apply_patch` to record Python version and initial Nautilus import failure before installation.
- `pip install -r requirements-nautilus.txt`
- `pip install -r requirements-nautilus.txt` with network escalation after sandbox DNS failure.
- `python - <<'PY' ... PY` Nautilus import check after installation.
- `apply_patch` to record Nautilus installation and successful import in `MEMORY.md`.
- `python - <<'PY' ... PY` package path inspection.
- `python - <<'PY' ... PY` local package keyword search for backtest APIs and examples.
- `sed -n '1,240p' .../examples/strategies/market_buy_on_start.py`
- `sed -n '1,280p' .../examples/strategies/bb_mean_reversion.py`
- `sed -n '1,280p' .../backtest/node.py`
- `sed -n '1,280p' .../backtest/config.py`
- `python - <<'PY' ... PY` inspect `BacktestEngine`, model constructors, enums, and report methods.
- `rg "CurrencyPair\\(" ...`
- `rg "Bar\\(" ...`
- `rg "BarType" ...`
- `python - <<'PY' ... PY` inspect model object docstrings and constructor docs.
- `sed -n '60,130p' .../test_kit/providers.py`
- `sed -n '190,250p' .../test_kit/stubs/data.py`
- `sed -n '1260,1295p' .../test_kit/providers.py`
- `python - <<'PY' ... PY` minimal low-level engine setup experiments.
- `python - <<'PY' ... PY` report method signature inspection.
- `apply_patch` to add Nautilus result path config constants, create the strategy, create the runner, and record API findings in `MEMORY.md`.
- `python nautilus_impl/run_nautilus_backtest.py`
- `cat nautilus_impl/nautilus_results.csv`
- `sed -n '1,20p' nautilus_impl/nautilus_trades.csv`
- `sed -n '1,10p' reports/nautilus_equity_curve.csv`
- `test -f nautilus_impl/nautilus_status.md && cat nautilus_impl/nautilus_status.md || true`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `python - <<'PY' ... PY` to compare Nautilus position PnL sum, account end value, and result row.
- `apply_patch` to prepend initial cash to the reconstructed Nautilus equity curve so total return uses the real start value.
- `sed -n '1,260p' README.md`
- `sed -n '1,220p' nautilus_impl/README.md`
- `sed -n '1,260p' common/config.py`
- `sed -n '1,320p' nautilus_impl/run_nautilus_backtest.py`
- `sed -n '1,280p' nautilus_impl/macd_strategy.py`
- `sed -n '320,680p' nautilus_impl/run_nautilus_backtest.py`
- `tail -n 220 MEMORY.md`
- `git status --short`
- `test -f nautilus_impl/nautilus_status.md && sed -n '1,220p' nautilus_impl/nautilus_status.md`
- `apply_patch` to remove an unused NumPy import, update README, and update Nautilus README.
- `apply_patch` to record Nautilus Phase 3 outcome in `MEMORY.md`.
- `python nautilus_impl/run_nautilus_backtest.py`
- `cat nautilus_impl/nautilus_results.csv`
- `sed -n '1,20p' nautilus_impl/nautilus_trades.csv`
- `sed -n '1,10p' reports/nautilus_equity_curve.csv`
- `git status --short`
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `find . -type d -name "__pycache__" -prune -exec rm -rf {} +`
- `apply_patch` to record final Phase 3 verification and cache cleanup in `MEMORY.md`.

### Errors Encountered

- Initial `nautilus_trader` import failed because the package is not installed.
- First `pip install -r requirements-nautilus.txt` failed in the sandbox due DNS resolution errors for `pypi.org`.
- Exact install error: `ERROR: Could not find a version that satisfies the requirement nautilus_trader (from versions: none)` and `ERROR: No matching distribution found for nautilus_trader`.
- Minimal engine experiment failed when constructing `Price("0.00001", precision=5)`: `TypeError: must be real number, not str`.
- Minimal engine experiment failed when adding a `CurrencyPair` to a single-currency CASH account: `InvalidConfiguration: Cannot add CurrencyPair instrument ... for a venue with a single-currency CASH account.`
- First successful Nautilus runner output had an internally inconsistent `total_return` because the reconstructed equity curve began at the first closed trade instead of initial cash.

### Fixes Applied

- Reran `pip install -r requirements-nautilus.txt` with network escalation.
- Retried Nautilus import successfully after installation.
- Used `Price.from_str(...)` for string price construction.
- Switched the simulated venue to `AccountType.MARGIN` for the EUR/USD `CurrencyPair`.
- Patched `_positions_to_equity` to prepend `INITIAL_CASH` at the first dataset timestamp.
- Removed generated `common/__pycache__` and `nautilus_impl/__pycache__` directories after final verification.

### Backtest Output Summary

- Data mode: `REAL_CSV`.
- Rows: 6250.
- Date range: `2024-01-01 22:00:00` to `2024-12-31 21:00:00`.
- Bars processed: 6250.
- Entries: 241.
- Exits: 241.
- Total Return: `-0.004280`.
- Sharpe Ratio: `-6.103943`.
- Max Drawdown: `-0.005740`.
- Number of Trades: 241.
- Start value: `100000.0`.
- End value: `99572.04`.
- Results path: `nautilus_impl/nautilus_results.csv`.
- Trades path: `nautilus_impl/nautilus_trades.csv`.
- Equity curve path: `reports/nautilus_equity_curve.csv`.
- No `nautilus_impl/nautilus_status.md` file was produced because execution succeeded.

### Comparison Notes vs vectorbt

- vectorbt REAL_CSV summary: 241 entries, 242 exits, total return `-0.003863`, Sharpe ratio `-0.941478`, max drawdown `-0.005761`, and 241 trades.
- Nautilus REAL_CSV summary: 241 entries, 241 exits, total return `-0.004280`, Sharpe ratio `-6.103943`, max drawdown `-0.005740`, and 241 trades.
- Small differences are expected because vectorbt is vectorized while Nautilus is event-driven and submits market orders on completed bar events.
- The Nautilus equity curve is reconstructed from closed position PnL because a full bar-level account equity series was not exposed by the low-level report API used here.

### Unresolved Issues

- Nautilus Sharpe ratio and max drawdown are based on closed-trade equity, not full bar-level mark-to-market equity.
- MetaTrader 5 EA implementation is intentionally not started.
- Final cross-framework comparison remains pending until MT5 is implemented.

### Next Step

Begin the next phase only after confirmation. The likely next step is MetaTrader 5 EA implementation and then final cross-framework comparison.

## Phase 4 - MetaTrader 5 Expert Advisor and Import CSV

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `data/processed/EURUSD_H1_2024_clean.csv` exists.
- `vectorbt_impl/vectorbt_results.csv` exists and reports `Data mode: REAL_CSV`.
- vectorbt summary: 6250 rows, date range `2024-01-01 22:00:00` to `2024-12-31 21:00:00`, 241 trades, total return `-0.003863`, Sharpe ratio `-0.941478`, max drawdown `-0.005761`.
- `nautilus_impl/nautilus_results.csv` exists and reports `Data mode: REAL_CSV`.
- Nautilus summary: 6250 rows, date range `2024-01-01 22:00:00` to `2024-12-31 21:00:00`, 241 trades, total return `-0.004280`, Sharpe ratio `-6.103943`, max drawdown `-0.005740`.
- Scope is MT5 import CSV, one MQL5 Expert Advisor, and MT5 run documentation only. No vectorbt or Nautilus logic changes are planned.

### Files Created

- `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`
- `mt5_impl/MACD_Crossover_Manual.mq5`
- `mt5_impl/reports/mt5_results_summary.md`

### Files Modified

- `README.md`
- `mt5_impl/README.md`
- `MEMORY.md`

### Commands Run

- `cat MEMORY.md`
- `pwd`
- `git status --short`
- `cat MEMORY.md`
- `find data/processed -maxdepth 1 -type f -print`
- `cat vectorbt_impl/vectorbt_results.csv`
- `cat nautilus_impl/nautilus_results.csv`
- `apply_patch` to record the Phase 4 starting state in `MEMORY.md`.
- `python - <<'PY' ... PY` to convert `data/processed/EURUSD_H1_2024_clean.csv` into `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`.
- `apply_patch` to record the MT5 import CSV creation in `MEMORY.md`.
- `sed -n '1,280p' README.md`
- `sed -n '1,240p' mt5_impl/README.md`
- `sed -n '1,220p' .gitignore`
- `apply_patch` to add `mt5_impl/MACD_Crossover_Manual.mq5`, add `mt5_impl/reports/mt5_results_summary.md`, update `mt5_impl/README.md`, and lightly update root `README.md`.
- `apply_patch` to record the MT5 EA and documentation changes in `MEMORY.md`.
- `grep -n "iMACD\\|iMA" mt5_impl/MACD_Crossover_Manual.mq5 || true`
- `grep -n "ManualEMA\\|CalculateMACD\\|OnInit\\|OnTick\\|CTrade" mt5_impl/MACD_Crossover_Manual.mq5`
- `head -n 5 data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`
- `tail -n 5 data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`
- `python - <<'PY' ... PY` to validate `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`.
- `apply_patch` to record static check and import CSV validation output in `MEMORY.md`.
- `git status --short`
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `cat mt5_impl/README.md`
- `cat mt5_impl/reports/mt5_results_summary.md`
- `find . -maxdepth 4 -type d -name __pycache__ -print`
- `find . -type d -name "__pycache__" -prune -exec rm -rf {} +`
- `apply_patch` to record final Phase 4 verification and cleanup in `MEMORY.md`.

### MT5 Import CSV Created

- Source: `data/processed/EURUSD_H1_2024_clean.csv`.
- Output: `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`.
- Output shape: `(6250, 9)`.
- Output columns: `Date`, `Time`, `Open`, `High`, `Low`, `Close`, `TickVolume`, `Volume`, `Spread`.
- First output timestamp: `2024.01.01 22:00`.
- Last output timestamp: `2024.12.31 21:00`.
- Timestamps were not shifted; they are treated as UTC/no-shift bar open times from the project data.
- Existing project volume was written as `TickVolume`; `Volume` and `Spread` were written as zero.

### MQL5 EA Implementation Details

- EA path: `mt5_impl/MACD_Crossover_Manual.mq5`.
- Uses `#include <Trade/Trade.mqh>` and a global `CTrade trade`.
- Inputs: `FastPeriod`, `SlowPeriod`, `SignalPeriod`, `LotSize`, `MagicNumber`, `SlippagePoints`, and `PrintDebug`.
- `OnInit()` validates period inputs, lot size, sets the expert magic number, sets slippage/deviation points, and prints the configuration.
- `OnTick()` detects new H1 bars with `iTime(_Symbol, PERIOD_H1, 0)` and evaluates only once per new bar.
- The EA uses completed bars only by calling `CopyRates(_Symbol, PERIOD_H1, 1, ...)`.
- Position logic is long-only, no shorting, no pyramiding, and manages only positions matching the current symbol and `MagicNumber`.
- Entry: open buy when previous manual MACD is less than or equal to previous signal and current manual MACD is greater than current signal.
- Exit: close managed long positions when previous manual MACD is greater than or equal to previous signal and current manual MACD is less than current signal.

### Manual EMA/MACD Confirmation

- Manual EMA uses the same SMA seed rule as the Python shared logic.
- First EMA value appears only after `period` valid values.
- EMA update uses `alpha = 2 / (period + 1)`.
- Manual MACD is calculated as fast EMA minus slow EMA.
- Signal line is calculated by applying the same manual EMA function to the MACD array.
- No built-in MT5 indicator handles, external indicator files, or technical-analysis libraries are used.

### Validation Output For MT5 Import CSV

- `head -n 5 data/mt5_import/EURUSD_CUSTOM_H1_2024.csv` showed the expected header and first rows beginning with `2024.01.01,22:00`.
- `tail -n 5 data/mt5_import/EURUSD_CUSTOM_H1_2024.csv` showed final rows ending with `2024.12.31,21:00`.
- Python validation output shape: `(6250, 9)`.
- Python validation output columns: `Date`, `Time`, `Open`, `High`, `Low`, `Close`, `TickVolume`, `Volume`, `Spread`.

### Static Check Results

- Prohibited indicator grep command produced no output: `grep -n "iMACD\\|iMA" mt5_impl/MACD_Crossover_Manual.mq5 || true`.
- Required symbol grep found `CTrade`, `ManualEMA`, `CalculateMACD`, `OnInit`, and `OnTick` in the EA.

### MT5 Execution Status

- EA implemented.
- MT5 import CSV prepared.
- Manual result summary template prepared.
- Local MT5 Strategy Tester was not run in this Linux/Python environment.
- No MT5 results were fabricated.

### Unresolved Issues

- MT5 Strategy Tester must be run manually after the EA is copied into MetaEditor/MT5.
- MT5 report files are pending under `mt5_impl/reports/`.
- Final cross-framework comparison remains pending until the MT5 Strategy Tester report is available.

### Next Step

Run the EA manually in MT5 Strategy Tester using either broker EURUSD history or the imported custom symbol CSV, then fill `mt5_impl/reports/mt5_results_summary.md` with the actual MT5 results.

## Final Polish Phase - Submission Readiness

### Starting State

- Confirmed working directory: `/home/flynntag/Documents/macD/macd-backtest-test`.
- `git status --short` still shows project files as untracked because no commit has been made.
- `mt5_impl/reports/` contains `mt5_report.html` and `mt5_results_summary.md`.
- No MT5 screenshot file is present.
- `vectorbt_impl/vectorbt_results.csv` reports `Data mode: REAL_CSV`.
- `nautilus_impl/nautilus_results.csv` reports `Data mode: REAL_CSV`.
- Generated cache directories were present at phase start: `common/__pycache__` and `nautilus_impl/__pycache__`.
- `mt5_impl/reports/mt5_results_summary.md` referenced `mt5_impl/reports/mt5_report_screenshot.png`, but that file does not exist.

### Files Modified

- `MEMORY.md`
- `README.md`
- `vectorbt_impl/README.md`
- `nautilus_impl/README.md`
- `mt5_impl/README.md`
- `mt5_impl/reports/mt5_results_summary.md`

### Commands Run

- `cat MEMORY.md`
- `wc -l MEMORY.md`
- `sed -n '1,220p' MEMORY.md`
- `sed -n '221,440p' MEMORY.md`
- `sed -n '441,660p' MEMORY.md`
- `sed -n '661,920p' MEMORY.md`
- `pwd`
- `git status --short`
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `ls -lh mt5_impl/reports/`
- `cat vectorbt_impl/vectorbt_results.csv`
- `cat nautilus_impl/nautilus_results.csv`
- `cat mt5_impl/reports/mt5_results_summary.md`
- `apply_patch` to record the final polish starting state in `MEMORY.md`.
- `apply_patch` to replace the missing MT5 screenshot path in `mt5_impl/reports/mt5_results_summary.md` with an honest note that no screenshot is included.
- `sed -n '1,320p' README.md`
- `sed -n '1,260p' vectorbt_impl/README.md`
- `sed -n '1,260p' nautilus_impl/README.md`
- `sed -n '1,320p' mt5_impl/README.md`
- `sed -n '1,240p' .gitignore`
- `apply_patch` to rewrite the root README for GitHub submission readiness and lightly update framework READMEs.
- `find . -type d -name "__pycache__" -prune -exec rm -rf {} +`
- `find . -type f -name "*.pyc" -delete`
- `find . -maxdepth 4 -type d -name "__pycache__" -print`
- `find . -type f -name "*.pyc" -print`
- `apply_patch` to record generated cache cleanup in `MEMORY.md`.

### Screenshot Mismatch Fix

- Fixed `mt5_impl/reports/mt5_results_summary.md`.
- Replaced `mt5_impl/reports/mt5_report_screenshot.png` with `Not included; the exported HTML Strategy Tester report is available.`
- No screenshot file was fabricated.

### Documentation Polish

- Rewrote `README.md` with submission-ready sections: project title, overview, strategy, data, structure, dependencies, run steps, results, framework notes, result differences, issues/fixes, AI usage, and final notes.
- Added final results table for vectorbt, Nautilus Trader, and MetaTrader 5.
- Documented that MT5 used `EURUSD_CUSTOM`, reported 230 trades, History Quality 16%, and 6106 bars.
- Updated framework READMEs with run steps, result paths, data requirements, and limitations.

### .gitignore Check

- `.gitignore` already ignores Python caches, `*.pyc`, virtual environments, local env files, OS files, logs, temporary files, large raw zip/bi5 downloads, and MT5 temporary tester/cache artifacts.
- `.gitignore` does not ignore final project artifacts such as `data/raw/EURUSD60.csv`, `data/processed/EURUSD_H1_2024_clean.csv`, `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`, framework result CSVs, or MT5 report files.

### Cleanup Performed

- Removed generated `__pycache__` directories.
- Removed generated `.pyc` files.
- Verification after cleanup printed no `__pycache__` directories and no `.pyc` files.

### Final Verification Commands

- `python vectorbt_impl/run_vectorbt_backtest.py`
- `python nautilus_impl/run_nautilus_backtest.py`
- `ls -lh mt5_impl/reports/`
- `cat mt5_impl/reports/mt5_results_summary.md`
- `git status --short`
- `find . -maxdepth 4 -type d -name "__pycache__" -print`
- `find . -type f -name "*.pyc" -print`
- `find . -type d -name "__pycache__" -prune -exec rm -rf {} +`
- `find . -type f -name "*.pyc" -delete`
- `git diff --stat`
- `find . -maxdepth 3 -not -path './.git' -not -path './.git/*' -print`
- `sed -n '1,260p' README.md`
- `apply_patch` to record final verification results and commit readiness in `MEMORY.md`.
- `sed -n '/^## Final Polish Phase - Submission Readiness/,$p' MEMORY.md`
- `apply_patch` to correct the final memory section file list and next step.

### MT5 Report Status

- MT5 HTML report exists: `mt5_impl/reports/mt5_report.html`.
- MT5 summary exists: `mt5_impl/reports/mt5_results_summary.md`.
- Screenshot is not present and is not claimed.

### Final Results Table

| Framework | Data | Trades | Total Return | Sharpe Ratio | Max Drawdown | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| vectorbt | REAL_CSV | 241 | -0.3863% | -0.9415 | -0.5761% | Vectorized signal portfolio |
| Nautilus Trader | REAL_CSV | 241 | -0.4280% | -6.1039 | -0.5740% | Event-driven; equity reconstructed from closed PnL |
| MetaTrader 5 | EURUSD_CUSTOM | 230 | -0.4325% | -1.23 | -0.65% | Manual Strategy Tester run; 16% history quality and 6106 bars |

### Final Verification Results

- vectorbt final rerun succeeded with `Data mode: REAL_CSV`, 6250 rows, 241 entries, 242 exits, and 241 trades.
- Nautilus final rerun succeeded with `Data mode: REAL_CSV`, 6250 rows, 6250 bars processed, 241 entries, 241 exits, and 241 trades.
- `mt5_impl/reports/` contains `mt5_report.html` and `mt5_results_summary.md`.
- `mt5_results_summary.md` is filled and states that no screenshot is included.
- Final cache checks printed no `__pycache__` directories and no `.pyc` files.
- `git diff --stat` printed no output because the repository contents are currently untracked rather than tracked modifications.
- `git status --short` shows the project files as untracked and ready to stage.

### Unresolved Limitations

- MT5 report has History Quality 16% and 6106 bars, while the Python processed CSV contains 6250 rows.
- Nautilus Sharpe ratio and drawdown are based on a closed-trade reconstructed equity curve.
- No MT5 screenshot is included; the exported HTML Strategy Tester report is included.

### Final GitHub Push Readiness

- Repository is clean of generated cache files.
- Final data, result CSVs, MT5 HTML report, and MT5 summary are present and intentionally not ignored.
- Ready for local commit preparation.
- Recommended commit command: `git commit -m "Complete MACD backtesting comparison across vectorbt, Nautilus, and MT5"`.

### Next Step

Stage and commit the project locally, then add a GitHub remote and push when ready.
