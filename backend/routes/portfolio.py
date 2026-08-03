from fastapi import APIRouter, HTTPException

from backend.schemas.portfolio import (
    PortfolioAnalyzeRequest,
    PortfolioAnalysisResponse,
    PortfolioBase,
    PortfolioDiversificationResponse,
    PortfolioRebalanceResponse,
    PortfolioRiskResponse,
)
from backend.services.portfolio_engine import PortfolioEngine
from backend.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
portfolio_service = PortfolioService()
portfolio_engine = PortfolioEngine()


@router.get("", summary="Get portfolio summary")
async def get_portfolio_summary() -> dict[str, object]:
    """Return the latest portfolio summary."""
    return portfolio_service.get_portfolio_summary()


@router.post("", summary="Create or update portfolio")
async def upsert_portfolio(payload: PortfolioBase) -> dict[str, object]:
    """Create or update a portfolio payload."""
    try:
        return portfolio_service.upsert_portfolio(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze", response_model=PortfolioAnalysisResponse, summary="Analyze a portfolio")
async def analyze_portfolio(payload: PortfolioAnalyzeRequest) -> PortfolioAnalysisResponse:
    try:
        return PortfolioAnalysisResponse(**portfolio_engine.analyze(payload.model_dump()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/risk", response_model=PortfolioRiskResponse, summary="Assess portfolio risk")
async def analyze_portfolio_risk(payload: PortfolioAnalyzeRequest) -> PortfolioRiskResponse:
    try:
        return PortfolioRiskResponse(**portfolio_engine.risk(payload.model_dump()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/rebalance", response_model=PortfolioRebalanceResponse, summary="Suggest portfolio rebalance")
async def rebalance_portfolio(payload: PortfolioAnalyzeRequest) -> PortfolioRebalanceResponse:
    try:
        result = portfolio_engine.rebalance(payload.model_dump())
        return PortfolioRebalanceResponse(portfolio_score=result["portfolio_score"], suggested_allocations=result.get("suggested_allocations", {}), ai_comments=result.get("ai_comments", []))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/diversification", response_model=PortfolioDiversificationResponse, summary="Assess diversification")
async def assess_diversification(payload: PortfolioAnalyzeRequest) -> PortfolioDiversificationResponse:
    try:
        result = portfolio_engine.diversification(payload.model_dump())
        return PortfolioDiversificationResponse(diversification_score=result["diversification_score"], sector_distribution=result.get("sector_distribution", {}), ai_comments=result.get("ai_comments", []))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
