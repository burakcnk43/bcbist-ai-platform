from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/")
async def get_portfolio_overview():
    """Returns AI-tracked portfolio insights for the simulated user."""
    return {
        "status": "ready",
        "total_value": 0.0,
        "base_currency": "TRY",
        "ai_health_score": 0,
        "risk_profile": "balanced",
        "holdings": [],
        "diversification": {
            "sector_spread": {},
            "asset_allocation": {"stocks": 100}
        }
    }
