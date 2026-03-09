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

# Mock expected returns
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

@app.get("/health")
def health_check():
    return {"status": "ML Engine is running"}


@app.post("/allocate")
def allocate_portfolio(req: AllocationRequest):

    try:
        print("Request received:", req)

        # Fetch fresh market data per request
        historical_prices = fetch_historical_data(
            tickers=NIFTY_TICKERS,
            period="1y"
        )

        print("Historical data columns:", historical_prices.columns)

        allocator = ModernPortfolioTheoryAllocator(
            expected_returns=MOCK_EXPECTED_RETURNS,
            historical_prices=historical_prices,
            risk_free_rate=0.07
        )

        allocation_weights = allocator.allocate(
            risk_capacity=req.risk_capacity
        )

        cleaned_allocation = {
            k: round(v, 4)
            for k, v in allocation_weights.items()
            if v > 0.001
        }

        expected_return = sum(
            MOCK_EXPECTED_RETURNS[k] * v
            for k, v in cleaned_allocation.items()
        )

        return {
            "risk_capacity": req.risk_capacity,
            "allocation": cleaned_allocation,
            "expected_portfolio_return": expected_return,
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "error": "Portfolio allocation failed",
            "details": str(e)
        }