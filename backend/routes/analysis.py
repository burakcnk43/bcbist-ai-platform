from fastapi import APIRouter, HTTPException

from backend.schemas.stock import StockAnalysisRequest, StockAnalysisResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])
analysis_service = AnalysisService()


@router.post("/stock", response_model=StockAnalysisResponse, summary="Analyze a stock")
async def analyze_stock(request: StockAnalysisRequest) -> StockAnalysisResponse:
    """Analyze a single stock and return the normalized payload."""
    try:
        result = analysis_service.analyze_symbol(request.symbol)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StockAnalysisResponse(**result)


@router.get("/news", summary="Get analysis news")
async def get_analysis_news(symbol: str, limit: int = 8) -> dict[str, object]:
    """Return normalized news items for a given stock symbol."""
    try:
        news = analysis_service.get_analysis_news(symbol, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"symbol": symbol, "news": news}
