from fastapi import APIRouter
from ...schemas.recommendation import RecommendationResponse
from ...services.recommendation_service import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/daily", response_model=RecommendationResponse)
async def get_daily_recommendations():
    return await recommendation_service.get_recommendations("daily")

@router.get("/weekly", response_model=RecommendationResponse)
async def get_weekly_recommendations():
    return await recommendation_service.get_recommendations("weekly")

@router.get("/monthly", response_model=RecommendationResponse)
async def get_monthly_recommendations():
    return await recommendation_service.get_recommendations("monthly")

@router.get("/long-term", response_model=RecommendationResponse)
async def get_long_term_recommendations():
    return await recommendation_service.get_recommendations("long-term")

@router.get("/dividend", response_model=RecommendationResponse)
async def get_dividend_recommendations():
    return await recommendation_service.get_recommendations("dividend")

@router.get("/value", response_model=RecommendationResponse)
async def get_value_recommendations():
    return await recommendation_service.get_recommendations("value")

@router.get("/high-growth", response_model=RecommendationResponse)
async def get_high_growth_recommendations():
    return await recommendation_service.get_recommendations("high-growth")

@router.get("/high-risk", response_model=RecommendationResponse)
async def get_high_risk_recommendations():
    return await recommendation_service.get_recommendations("high-risk")
