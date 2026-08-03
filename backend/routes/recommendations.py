from fastapi import APIRouter, HTTPException

from backend.schemas.recommendations import RecommendationResponse
from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])
recommendation_service = RecommendationService()


@router.get("/daily", response_model=RecommendationResponse, summary="Daily recommendations")
async def get_daily_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="daily", count=len(recommendation_service.get_recommendations("daily")), recommendations=recommendation_service.get_recommendations("daily"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/weekly", response_model=RecommendationResponse, summary="Weekly recommendations")
async def get_weekly_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="weekly", count=len(recommendation_service.get_recommendations("weekly")), recommendations=recommendation_service.get_recommendations("weekly"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/monthly", response_model=RecommendationResponse, summary="Monthly recommendations")
async def get_monthly_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="monthly", count=len(recommendation_service.get_recommendations("monthly")), recommendations=recommendation_service.get_recommendations("monthly"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/long-term", response_model=RecommendationResponse, summary="Long-term recommendations")
async def get_long_term_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="long-term", count=len(recommendation_service.get_recommendations("long-term")), recommendations=recommendation_service.get_recommendations("long-term"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/dividend", response_model=RecommendationResponse, summary="Dividend recommendations")
async def get_dividend_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="dividend", count=len(recommendation_service.get_recommendations("dividend")), recommendations=recommendation_service.get_recommendations("dividend"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/value", response_model=RecommendationResponse, summary="Value recommendations")
async def get_value_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="value", count=len(recommendation_service.get_recommendations("value")), recommendations=recommendation_service.get_recommendations("value"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/high-growth", response_model=RecommendationResponse, summary="High-growth recommendations")
async def get_high_growth_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="high-growth", count=len(recommendation_service.get_recommendations("high-growth")), recommendations=recommendation_service.get_recommendations("high-growth"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/high-risk", response_model=RecommendationResponse, summary="High-risk recommendations")
async def get_high_risk_recommendations() -> RecommendationResponse:
    try:
        return RecommendationResponse(strategy="high-risk", count=len(recommendation_service.get_recommendations("high-risk")), recommendations=recommendation_service.get_recommendations("high-risk"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
