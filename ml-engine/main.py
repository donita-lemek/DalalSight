from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np

from data_ingestion import fetch_historical_data, NIFTY_TICKERS
from allocator import ModernPortfolioTheoryAllocator

app = FastAPI(title="DalalSight ML Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AllocationRequest(BaseModel):
    risk_capacity: str
    selected_industries: List[str]

# Mocking expected returns since real-time training of BiLSTM/ARIMA is too slow for synchronous API
MOCK_EXPECTED_RETURNS = {
    "RELIANCE.NS": 0.12,
    "TCS.NS": 0.15,
    "HDFCBANK.NS": 0.14,
    "INFY.NS": 0.11,
    "SUNPHARMA.NS": 0.18,
    "TATASTEEL.NS": 0.08,
    "ICICIBANK.NS": 0.13,
    "HINDUNILVR.NS": 0.09
}

print("Loading historical data for Covariance matrix calculation...")
# Fetch 1 year of data to compute covariance matrix quickly
HISTORICAL_PRICES = fetch_historical_data(tickers=NIFTY_TICKERS, period="1y")
print("Startup complete.")

@app.get("/health")
def health_check():
    return {"status": "ML Engine is running"}

@app.post("/allocate")
def allocate_portfolio(req: AllocationRequest):
    # In a fully integrated version, we'd filter NIFTY_TICKERS by req.selected_industries.
    # For now, we use all tickers to ensure the covariance matrix matches.
    
    # Initialize the allocator
    allocator = ModernPortfolioTheoryAllocator(
        expected_returns=MOCK_EXPECTED_RETURNS, 
        historical_prices=HISTORICAL_PRICES,
        risk_free_rate=0.07
    )
    
    # Run the Markowitz optimizer
    allocation_weights = allocator.allocate(risk_capacity=req.risk_capacity)
    
    # Filter out near-zero weights
    cleaned_allocation = {k: round(v, 4) for k, v in allocation_weights.items() if v > 0.001}
    
    return {
        "risk_capacity": req.risk_capacity,
        "allocation": cleaned_allocation,
        "expected_portfolio_return": sum(MOCK_EXPECTED_RETURNS[k] * v for k, v in cleaned_allocation.items()),
    }
