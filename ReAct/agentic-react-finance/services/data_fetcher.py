# services/data_fetcher.py
"""Reliable data fetcher for yfinance with fallbacks and clearer errors."""
from typing import Optional
import pandas as pd
import datetime
import time
import yfinance as yf

def fetch_price_history(ticker: str, period_days: int, max_retries: int = 2) -> pd.Series:
    """
    Return a pandas Series of daily adjusted close prices for the last `period_days` days.
    This function tries yf.download first, then falls back to Ticker.history if needed.
    Raises RuntimeError with useful message if no data can be obtained.
    """
    end = datetime.datetime.utcnow().date()
    start = end - datetime.timedelta(days=period_days + 7)  # a bit extra to ensure enough business days

    last_exception: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            # Use explicit start/end and auto_adjust to avoid warnings and ensure adjusted prices
            df = yf.download(
                ticker,
                start=start.isoformat(),
                end=(end + datetime.timedelta(days=1)).isoformat(),
                progress=False,
                auto_adjust=True,   # use adjusted close directly
                threads=False
            )

            # If df is empty, try Ticker.history fallback
            if df is None or df.empty:
                tkr = yf.Ticker(ticker)
                df = tkr.history(start=start.isoformat(), end=(end + datetime.timedelta(days=1)).isoformat(), auto_adjust=True)
            
            if df is None or df.empty:
                raise ValueError(f"No price rows returned for ticker '{ticker}' (attempt {attempt}).")

            # Prefer 'Close' if auto_adjust True gives adjusted close; robustly find a column
            price_col = None
            for col_name in ["Close", "Adj Close", "Close"]:
                if col_name in df.columns:
                    price_col = col_name
                    break
            if price_col is None:
                # Maybe auto_adjust produced a single column DataFrame
                if df.shape[1] == 1:
                    price_col = df.columns[0]
                else:
                    raise ValueError(f"Could not find price column for ticker '{ticker}'. Columns: {list(df.columns)}")

            series = df[price_col].dropna()
            if series.empty:
                raise ValueError(f"No non-null prices for ticker '{ticker}' after dropping NaNs.")

            # Trim to exactly last `period_days` business days if too long
            if len(series) > period_days:
                series = series.iloc[-period_days:]

            return series

        except Exception as exc:
            last_exception = exc
            # simple backoff
            time.sleep(0.5 * attempt)

    # If we exit loop, fail with informative error
    raise RuntimeError(f"Failed to fetch data for {ticker} after {max_retries} attempts. Last error: {last_exception}")
