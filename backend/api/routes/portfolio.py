from fastapi import APIRouter

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/")
async def get_portfolio_overview():
    """Returns the user's AI-tracked portfolio status and insights."""
    return {
        "status": "ready",
        "total_value": 0.0,
        "ai_score_avg": 0,
        "holdings": []
    }
