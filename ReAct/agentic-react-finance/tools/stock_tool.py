# tools/stock_tool.py
"""
Tool for fetching and summarizing stock data.

This version:
 - Uses fetch_price_history() for reliable data retrieval
 - Avoids pandas FutureWarnings by using .iloc[...] instead of float(series)
 - Handles missing/latest price safely
 - Returns clean structured data for the agent
"""

from typing import Dict, Any
import numpy as np
import pandas as pd

from services.data_fetcher import fetch_price_history


def summarize_stock(ticker: str, days: int) -> Dict[str, Any]:
    """
    Fetch recent adjusted prices for `ticker` (last `days` days),
    compute daily returns, annualized volatility, annualized returns,
    and return a structured summary dict.
    """
    try:
        prices: pd.Series = fetch_price_history(ticker, days)
    except Exception as exc:
        return {"ticker": ticker, "error": f"fetch_error: {exc}"}

    # Ensure data exists
    if prices is None or prices.empty:
        return {"ticker": ticker, "error": "no_data"}

    # Convert to numeric & drop NaNs
    try:
        prices = prices.dropna().astype(float)
    except Exception:
        return {"ticker": ticker, "error": "invalid_price_data"}

    if prices.empty:
        return {"ticker": ticker, "error": "no_valid_prices_after_dropna"}

    # Latest price (warning-free)
    try:
        latest_price = float(prices.iloc[-1])
    except Exception:
        return {"ticker": ticker, "error": "could_not_extract_latest_price"}

    # Compute daily returns
    try:
        returns = prices.pct_change().dropna()
    except Exception:
        returns = pd.Series(dtype=float)

    observations = int(len(prices))

    # Default values
    annualized_vol = 0.0
    annualized_ret = 0.0

    if not returns.empty:
        # Standard deviation → returns.std() returns a scalar, but safe-cast manually
        daily_std = returns.std(ddof=0)
        daily_mean = returns.mean()

        # Convert to floats safely (iloc no longer needed; std() returns numpy.float)
        annualized_vol = float(daily_std * np.sqrt(252))
        annualized_ret = float(daily_mean * 252)

    return {
        "ticker": ticker,
        "latest_price": latest_price,
        "annualized_volatility": annualized_vol,
        "annualized_return": annualized_ret,
        "observations": observations,
    }
