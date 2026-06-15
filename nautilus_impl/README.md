# Nautilus Trader Implementation

This folder contains the Nautilus Trader implementation of the manually calculated MACD crossover strategy.

Run from the project root:

```bash
python nautilus_impl/run_nautilus_backtest.py
```

## Data Requirement

The runner requires the Phase 2.6 processed CSV:

```text
data/processed/EURUSD_H1_2024_clean.csv
```

Expected columns:

```text
timestamp, open, high, low, close, volume
```

## Strategy Rule

The Nautilus strategy calculates EMA and MACD manually inside the event-driven strategy.
It does not use Nautilus built-in EMA or MACD indicators, pandas `.ewm()`, TA-Lib, pandas-ta, vectorbt indicators, or any technical indicator library.

The strategy is long-only, uses a fixed 10,000 unit EUR/USD quantity, and submits market orders from `on_bar` after completed H1 bars are received.

## Result Files

- `nautilus_impl/nautilus_results.csv`
- `nautilus_impl/nautilus_trades.csv`
- `reports/nautilus_equity_curve.csv`

## Current Limitations

The low-level Nautilus report API did not expose a full bar-level equity series in this runner.
The saved equity curve is reconstructed from closed position PnL, so Sharpe ratio and max drawdown are based on closed-trade equity rather than every H1 bar.

Nautilus results are expected to differ slightly from vectorbt because this implementation is event-driven and routes orders through a simulated venue instead of using vectorized signal arrays.
