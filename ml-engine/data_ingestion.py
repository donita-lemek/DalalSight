import yfinance as yf
import pandas as pd
from typing import List

NIFTY_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "SUNPHARMA.NS",
    "TATASTEEL.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS"
]

def fetch_historical_data(tickers: List[str] = NIFTY_TICKERS, period: str = "5y") -> pd.DataFrame:

    print(f"Fetching {period} of historical data for {len(tickers)} tickers...")

    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        progress=False
    )

    # yfinance returns MultiIndex columns when multiple tickers are downloaded
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    prices = prices.dropna(how="all")
    prices = prices.ffill().bfill()

    print("Downloaded tickers:", prices.columns.tolist())

    return prices


if __name__ == "__main__":
    df = fetch_historical_data()
    print(df.tail())