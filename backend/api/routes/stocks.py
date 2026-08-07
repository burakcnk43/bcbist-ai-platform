from fastapi import APIRouter, HTTPException
from typing import List
from ...services.stock_registry import stock_registry
from ...services.stock_service import stock_service
from ...schemas.stock import StockInfo

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/search", response_model=List[StockInfo])
async def search_stocks(query: str):
    """Fast case-insensitive search for stocks by ticker or company name."""
    query = query.upper()
    all_symbols = stock_registry.get_all_symbols()
    results = []

    for symbol in all_symbols:
        data = stock_registry.get_stock_data(symbol)
        if query in symbol or query in data["name"].upper():
            results.append(StockInfo(
                symbol=symbol,
                name=data["name"],
                sector=data["sector"]
            ))

    return results[:20] # Limit to 20 results for performance

@router.get("/{symbol}")
async def get_stock_details(symbol: str):
    """Returns detailed AI analysis for a specific stock symbol."""
    symbol = symbol.upper()
    data = stock_service.analyze_stock(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found or data unavailable")

    return {
        "symbol": data.symbol,
        "info": data.info,
        "is_active": True
    }
