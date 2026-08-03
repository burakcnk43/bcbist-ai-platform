from fastapi import APIRouter, HTTPException, Path

from backend.schemas.stock import (
    StockAnalysisRequest,
    StockAnalysisResponse,
    StockRegistryEntrySchema,
    StockRegistryResponse,
)
from backend.services.stock_registry import StockRegistryService
from backend.services.stock_service import StockService

router = APIRouter(prefix="/api/stocks", tags=["stocks"])
stock_service = StockService()
stock_registry_service = StockRegistryService()


@router.get(
    "",
    response_model=StockRegistryResponse,
    summary="List Borsa Istanbul stock registry",
    description="Return metadata for the complete Borsa Istanbul stock registry.",
)
async def list_stocks() -> StockRegistryResponse:
    """Return the complete stock registry for the backend."""
    stocks = stock_registry_service.get_registry()
    return StockRegistryResponse(count=len(stocks), stocks=stocks)


@router.get(
    "/{symbol}",
    response_model=StockRegistryEntrySchema,
    summary="Get stock metadata",
    description="Return metadata for a single Borsa Istanbul company.",
)
async def get_stock(symbol: str = Path(..., min_length=1, max_length=10)) -> StockRegistryEntrySchema:
    """Return metadata for a single stock symbol."""
    entry = stock_registry_service.get_symbol(symbol)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"{symbol} için kayıt bulunamadı.")
    return StockRegistryEntrySchema(**entry)


@router.post(
    "/analyze",
    response_model=StockAnalysisResponse,
    summary="Analyze a stock",
    description="Return technical, financial, valuation, and news data for a single ticker.",
    responses={
        404: {"description": "Ticker data could not be retrieved."},
        500: {"description": "Unexpected server error."},
    },
)
async def analyze_stock(request: StockAnalysisRequest) -> StockAnalysisResponse:
    """Analyze a single stock and return JSON-ready metrics for the future Flutter app."""
    try:
        result = stock_service.analyze_stock(request.symbol)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StockAnalysisResponse(**result)
