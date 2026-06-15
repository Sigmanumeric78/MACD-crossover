# MT5 Strategy Tester Result Summary

## Run Settings
- Expert: MACD_Crossover_Manual
- Symbol: EURUSD_CUSTOM
- Timeframe: H1
- Date range: 2024-01-01 to 2024-12-31
- Initial deposit: 100000 USD
- Lot size: 0.10
- Modeling mode: Open prices only
- Spread: 0/custom symbol
- Data source: data/mt5_import/EURUSD_CUSTOM_H1_2024.csv

## Key Results
- Total net profit: -432.54 USD
- Total return: -0.0043254 / -0.43254%
- Sharpe ratio: -1.23
- Max drawdown: 649.41 USD / 0.65% equity drawdown maximal
- Number of trades: 230
- Final balance/equity: 99567.46 USD final balance

## Report Files
- HTML report: mt5_impl/reports/mt5_report.html
- Screenshot: Not included; the exported HTML Strategy Tester report is available.

## Notes
- MT5 was run manually using Strategy Tester on EURUSD_CUSTOM.
- The EA used manual EMA/MACD logic with FastPeriod=12, SlowPeriod=26, SignalPeriod=9, and LotSize=0.10.
- The report shows History Quality of 16% and 6106 bars, while the Python CSV contains 6250 H1 rows. This difference is documented as an MT5 custom-symbol/import/testing limitation.
- Results differ slightly from vectorbt and Nautilus because MT5 uses its own Strategy Tester execution, order handling, and custom-symbol bar processing.
