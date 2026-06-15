"""Reusable performance metric calculations."""

import numpy as np
import pandas as pd


def _valid_numeric_series(values, name):
    return pd.to_numeric(pd.Series(values, name=name), errors="coerce").dropna()


def calculate_total_return(equity_curve):
    """Calculate total return from an equity curve.

    NaN values are ignored. Total return is `final equity / initial equity - 1`.

    Raises:
        ValueError: If fewer than two valid equity values exist or if initial
            equity is zero.
    """
    equity = _valid_numeric_series(equity_curve, "equity_curve")
    if len(equity) < 2:
        raise ValueError("At least two valid equity values are required.")

    initial_equity = float(equity.iloc[0])
    if initial_equity == 0.0:
        raise ValueError("Initial equity must be non-zero.")

    return float(equity.iloc[-1] / initial_equity - 1.0)


def calculate_sharpe_ratio(returns, periods_per_year):
    """Calculate annualized Sharpe ratio from periodic returns.

    The risk-free rate is assumed to be zero. NaN returns are ignored. If there
    are no valid returns, fewer than two valid returns, or zero return
    volatility, NaN is returned.
    """
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive.")

    valid_returns = _valid_numeric_series(returns, "returns")
    if len(valid_returns) < 2:
        return float("nan")

    std_returns = float(valid_returns.std(ddof=1))
    if std_returns == 0.0 or np.isnan(std_returns):
        return float("nan")

    return float(valid_returns.mean() / std_returns * np.sqrt(periods_per_year))


def calculate_max_drawdown(equity_curve):
    """Calculate maximum drawdown from an equity curve.

    Running peak is the cumulative maximum equity. Drawdown is
    `equity / running peak - 1`, and the returned value is the minimum
    drawdown, which should be negative or zero.

    Raises:
        ValueError: If no valid equity values exist.
    """
    equity = _valid_numeric_series(equity_curve, "equity_curve")
    if equity.empty:
        raise ValueError("At least one valid equity value is required.")

    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0
    return float(drawdown.min())
