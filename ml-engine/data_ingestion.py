import yfinance as yf
import pandas as pd
from typing import List

# Pre-selected basket of Indian stocks as per the implementation plan
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
    """
    Fetches historical adjusted close prices for the given list of tickers.
    Returns a DataFrame where rows are dates and columns are tickers.
    """
    print(f"Fetching {period} of historical data for {len(tickers)} tickers...")
    data = yf.download(tickers, period=period, progress=False)
    
    # yf.download returns a MultiIndex column DataFrame if multiple tickers are passed
    # We only care about 'Adj Close' or 'Close'
    if 'Adj Close' in data:
        prices = data['Adj Close']
    else:
        prices = data['Close']
        
    prices = prices.dropna(how='all')
    prices.ffill(inplace=True)
    prices.bfill(inplace=True)
    
    return prices

if __name__ == "__main__":
    df = fetch_historical_data()
    print(df.tail())
