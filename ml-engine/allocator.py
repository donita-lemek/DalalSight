import numpy as np
import pandas as pd
from scipy.optimize import minimize

class ModernPortfolioTheoryAllocator:
    def __init__(self, expected_returns: dict, historical_prices: pd.DataFrame, risk_free_rate: float = 0.07):
        """
        expected_returns: Dictionary { 'TICKER': expected_annualized_return_float }
        historical_prices: DataFrame with Tickers as columns and prices as rows.
        risk_free_rate: 7% default as per specification.
        """
        # Ensure we only work with the tickers requested
        self.tickers = list(expected_returns.keys())
        self.expected_returns = np.array([expected_returns[t] for t in self.tickers])
        
        # Calculate daily returns from prices
        returns = historical_prices[self.tickers].pct_change().dropna()
        # Annualized covariance matrix (assumes 252 trading days)
        self.cov_matrix = returns.cov() * 252
        self.risk_free_rate = risk_free_rate

    def _portfolio_annualised_performance(self, weights):
        returns = np.sum(self.expected_returns * weights)
        # Volatility = sqrt( w.T * Cov * w )
        std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        return std, returns

    def _neg_sharpe_ratio(self, weights):
        p_volatility, p_returns = self._portfolio_annualised_performance(weights)
        # We want to MAXIMIZE Sharpe, so MINIMIZE negative Sharpe
        if p_volatility == 0:
            return 0
        return -(p_returns - self.risk_free_rate) / p_volatility

    def allocate(self, risk_capacity: str):
        """
        Risk capacities: 'Conservative', 'Moderate', 'Aggressive'
        Returns: Dict of { ticker: weight }
        """
        num_assets = len(self.tickers)
        args = ()
        
        # Constraints: Weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds logic mapped to user's risk capacity
        if risk_capacity.lower() == 'conservative':
            # Strict diversification, no asset holds more than 20%
            bound = (0.0, 0.20)
            bounds = tuple(bound for asset in range(num_assets))
        elif risk_capacity.lower() == 'moderate':
            # Standard long-only, max 40% per asset
            bound = (0.0, 0.40)
            bounds = tuple(bound for asset in range(num_assets))
        elif risk_capacity.lower() == 'aggressive':
            # Relaxed bounds, allow up to 80% per asset
            bound = (0.0, 0.80)
            bounds = tuple(bound for asset in range(num_assets))
        else:
            bound = (0.0, 1.0)
            bounds = tuple(bound for asset in range(num_assets))

        # Initial guess - equal distribution
        initial_guess = num_assets * [1. / num_assets,]
        
        result = minimize(self._neg_sharpe_ratio, initial_guess, args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
                        
        if not result.success:
            print("Optimization failed, returning equal weights.")
            weights = initial_guess
        else:
            weights = result.x

        allocation = {self.tickers[i]: float(weights[i]) for i in range(num_assets)}
        return allocation
