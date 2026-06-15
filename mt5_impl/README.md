# MetaTrader 5 Implementation

This folder contains the MetaTrader 5 Expert Advisor and manual Strategy Tester instructions for the manually calculated MACD crossover strategy.

## Files

- Expert Advisor: `mt5_impl/MACD_Crossover_Manual.mq5`
- MT5 custom symbol import CSV: `data/mt5_import/EURUSD_CUSTOM_H1_2024.csv`
- MT5 exported HTML report: `mt5_impl/reports/mt5_report.html`
- Manual result summary: `mt5_impl/reports/mt5_results_summary.md`

## Strategy

- Instrument: EURUSD, or a custom symbol imported from `EURUSD_CUSTOM_H1_2024.csv`
- Timeframe: H1
- Date range: 2024-01-01 to 2024-12-31
- Mode: long-only / flat
- Position size: `0.10` lot
- Initial tester deposit: `100000 USD`
- Manual EMA/MACD calculation only. The EA does not use built-in indicator handles or external indicator files.

The EA evaluates once per new H1 bar, calculates signals from completed bars only, and sends market orders after the new bar starts. This matches the project assumption that signals are generated after candle close and execution occurs on the next bar open.

## Copy And Compile

1. Open MetaTrader 5.
2. Open MetaEditor.
3. Create a new Expert Advisor file named `MACD_Crossover_Manual.mq5`, or copy this repository file into your MT5 data folder under `MQL5/Experts/`.
4. Paste or copy the contents of `mt5_impl/MACD_Crossover_Manual.mq5`.
5. Compile in MetaEditor and confirm there are no compile errors.

## Custom Symbol Import

Use the prepared import CSV if you want MT5 data alignment to be closer to vectorbt and Nautilus:

```text
data/mt5_import/EURUSD_CUSTOM_H1_2024.csv
```

In MT5:

1. Open `View -> Symbols`.
2. Create or select a custom symbol, for example `EURUSD_CUSTOM`.
3. Use the custom symbol import tool.
4. Import `EURUSD_CUSTOM_H1_2024.csv`.
5. Confirm the columns map as:
   `Date`, `Time`, `Open`, `High`, `Low`, `Close`, `TickVolume`, `Volume`, `Spread`.
6. Do not shift timestamps. The project data treats timestamps as UTC/no-shift bar open times.

If you use broker-provided EURUSD history instead of the custom imported CSV, results may differ because broker data, timezone, spread, and execution settings may not match the project CSV.

## Strategy Tester Settings

Suggested settings:

```text
Expert: MACD_Crossover_Manual
Symbol: EURUSD or custom symbol created from EURUSD_CUSTOM_H1_2024.csv
Timeframe: H1
Date: 2024-01-01 to 2024-12-31
Initial deposit: 100000 USD
Lot size input: 0.10
Model: Open prices only, or 1 minute OHLC if custom symbol import supports it
Optimization: Off
```

Inputs:

```text
FastPeriod: 12
SlowPeriod: 26
SignalPeriod: 9
LotSize: 0.10
MagicNumber: 26012024
SlippagePoints: 10
PrintDebug: false
```

## Reports

After running the Strategy Tester, save the exported report under:

```text
mt5_impl/reports/
```

Current report files:

```text
mt5_impl/reports/mt5_report.html
mt5_impl/reports/mt5_results_summary.md
```

No screenshot file is currently included. The exported HTML Strategy Tester report is available.

## Known Limitations

- The MT5 report shows History Quality of 16% and 6106 bars, while the Python processed CSV contains 6250 rows.
- Results differ from vectorbt and Nautilus because MT5 uses its own Strategy Tester execution, order handling, and custom-symbol bar processing.
- Do not use vectorbt or Nautilus numbers as MT5 results.
