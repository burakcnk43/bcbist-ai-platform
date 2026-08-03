from fastapi import APIRouter, HTTPException

from backend.schemas.portfolio import PortfolioBase
from backend.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
portfolio_service = PortfolioService()


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
