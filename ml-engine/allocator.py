import numpy as np
import pandas as pd
from scipy.optimize import minimize

class ModernPortfolioTheoryAllocator:

    def __init__(self, expected_returns: dict, historical_prices: pd.DataFrame, risk_free_rate: float = 0.07):

        # keep only tickers that exist in dataframe
        available_tickers = [
            t for t in expected_returns.keys()
            if t in historical_prices.columns
        ]

        if len(available_tickers) == 0:
            raise ValueError("No valid ticker data available")

        self.tickers = available_tickers

        self.expected_returns = np.array(
            [expected_returns[t] for t in self.tickers]
        )

        returns = historical_prices[self.tickers].pct_change().dropna()

        self.cov_matrix = returns.cov() * 252

        self.risk_free_rate = risk_free_rate