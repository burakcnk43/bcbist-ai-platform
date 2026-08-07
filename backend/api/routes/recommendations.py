from fastapi import APIRouter
from ...schemas.recommendation import RecommendationResponse
from ...services.recommendation_service import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/daily", response_model=RecommendationResponse)
async def get_daily_recommendations():
    """Returns top 10 highest-quality daily stock recommendations."""
    return await recommendation_service.get_recommendations("daily")

@router.get("/long-term", response_model=RecommendationResponse)
async def get_long_term_recommendations():
    """Returns top 10 highest-quality long-term investment picks."""
    return await recommendation_service.get_recommendations("long-term")
