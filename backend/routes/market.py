from fastapi import APIRouter

from backend.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()


@router.get("/bist100", summary="Get BIST 100 universe")
async def get_bist100() -> dict[str, object]:
    """Return the BIST 100 universe list for the frontend."""
    stocks = await market_service.get_bist100_universe()
    return {"stocks": stocks}


@router.get("/hot-stocks", summary="Get hot stocks")
async def get_hot_stocks() -> dict[str, object]:
    """Return a lightweight hot-stocks payload."""
    stocks = await market_service.get_hot_stocks()
    return {"stocks": stocks}
