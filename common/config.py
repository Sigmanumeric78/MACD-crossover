"""Project-wide configuration constants."""

SYMBOL = "EURUSD"
TIMEFRAME = "H1"
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

FAST_EMA_PERIOD = 12
SLOW_EMA_PERIOD = 26
SIGNAL_EMA_PERIOD = 9

INITIAL_CASH = 100000.0
TRADE_SIZE_UNITS = 10000.0
STRATEGY_MODE = "long_only_flat"
EXECUTION_ASSUMPTION = "signals_on_close_execute_next_bar_open"

DATA_PATH = "data/processed/EURUSD_H1_2024_clean.csv"
VECTORBT_RESULTS_PATH = "vectorbt_impl/vectorbt_results.csv"
VECTORBT_TRADES_PATH = "vectorbt_impl/vectorbt_trades.csv"
VECTORBT_EQUITY_PATH = "reports/vectorbt_equity_curve.csv"

NAUTILUS_RESULTS_PATH = "nautilus_impl/nautilus_results.csv"
NAUTILUS_TRADES_PATH = "nautilus_impl/nautilus_trades.csv"
NAUTILUS_EQUITY_PATH = "reports/nautilus_equity_curve.csv"
