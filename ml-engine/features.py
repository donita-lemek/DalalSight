import pandas as pd
import numpy as np

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({'MACD': macd, 'Signal': signal_line})

def calculate_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    returns = series.pct_change()
    volatility = returns.rolling(window=window).std() * np.sqrt(252) # Annualized
    return volatility

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame where columns are tickers and rows are dates with closing prices,
    returns a stacked or multi-level DataFrame containing the features.
    For modeling purposes, it's often easier to build features per ticker.
    """
    df_features = pd.DataFrame(index=df.index)
    
    for ticker in df.columns:
        price_series = df[ticker]
        df_features[(ticker, 'Close')] = price_series
        df_features[(ticker, 'RSI')] = calculate_rsi(price_series)
        
        macd_df = calculate_macd(price_series)
        df_features[(ticker, 'MACD')] = macd_df['MACD']
        df_features[(ticker, 'MACD_Signal')] = macd_df['Signal']
        
        df_features[(ticker, 'Volatility')] = calculate_volatility(price_series)
        df_features[(ticker, 'Returns')] = price_series.pct_change()
        
    df_features.columns = pd.MultiIndex.from_tuples(df_features.columns, names=['Ticker', 'Feature'])
    return df_features
