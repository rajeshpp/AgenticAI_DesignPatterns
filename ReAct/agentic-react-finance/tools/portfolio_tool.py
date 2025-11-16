# tools/portfolio_tool.py
"""Tool to analyze a portfolio given per-ticker summaries.
   More defensive: skips tickers without prices and reports missing tickers.
"""
from typing import List, Dict
import numpy as np

def analyze_portfolio(positions: List[Dict], summaries: List[Dict]) -> Dict:
    """Return a portfolio-level analysis: weighted volatility, exposures.
       If some tickers are missing prices, they are reported and excluded from totals.
    """
    sum_map = {s["ticker"]: s for s in summaries}
    total_value = 0.0
    position_values = []
    missing = []

    for p in positions:
        t = p["ticker"]
        shares = p.get("shares", 0)
        s = sum_map.get(t)
        latest = None
        if s:
            latest = s.get("latest_price") or s.get("latest") or None

        if latest is None or latest == 0:
            missing.append(t)
            # skip adding this position to total (we could also decide to use 0 or fallback)
            position_values.append({"ticker": t, "value": 0.0, "shares": shares, "note": "missing_price"})
            continue

        value = latest * shares
        position_values.append({"ticker": t, "value": value, "shares": shares})
        total_value += value

    if total_value == 0:
        return {
            "error": "portfolio has zero total value or missing data",
            "missing_tickers": missing,
            "positions": position_values,
        }

    weighted_vol = 0.0
    exposures = []
    for pv in position_values:
        weight = pv["value"] / total_value if total_value > 0 else 0.0
        ticker = pv["ticker"]
        vol = sum_map.get(ticker, {}).get("annualized_volatility", 0.0)
        weighted_vol += weight * vol
        exposures.append({"ticker": ticker, "weight": weight})

    return {
        "total_value": total_value,
        "weighted_annualized_volatility": weighted_vol,
        "exposures": exposures,
        "positions": position_values,
        "missing_tickers": missing,
    }
