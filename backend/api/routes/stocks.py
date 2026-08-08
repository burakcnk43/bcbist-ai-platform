import time
import unicodedata
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.stock_registry import stock_registry
from services.stock_service import stock_service
from schemas.stock import StockInfo
from core.cache import get_cached, set_cached

# Engine Imports
from engines.technical_engine import technical_engine
from engines.fundamental_engine import fundamental_engine
from engines.risk_engine import risk_engine
from engines.momentum_engine import momentum_engine
from engines.trend_engine import trend_engine
from engines.growth_engine import growth_engine
from engines.value_engine import value_engine
from engines.dividend_engine import dividend_engine
from engines.sector_engine import sector_engine
from engines.volatility_engine import volatility_engine
from engines.liquidity_engine import liquidity_engine
from engines.confidence_engine import confidence_engine
from engines.catalyst_engine import catalyst_engine
from engines.scoring_engine import scoring_engine

router = APIRouter(prefix="/stocks", tags=["Stocks"])

def normalize_turkish(text: str) -> str:
    """Normalizes Turkish characters to their English counterparts."""
    text = text.upper()
    mapping = str.maketrans("ÇĞİÖŞÜ", "CGIOSU")
    return text.translate(mapping)

@router.get("/search", response_model=List[StockInfo])
async def search_stocks(query: str = ""):
    """Robust BIST-wide search (V4). Returns all stocks if query is empty."""
    cache_key = f"search_v4_{query.lower()}"
    cached = get_cached(cache_key)
    if cached: return cached

    q = normalize_turkish(query)
    symbols = stock_registry.get_all_symbols()
    results = []

    for sym in symbols:
        meta = stock_registry.get_stock_data(sym)
        name_norm = normalize_turkish(meta["name"])
        sect_norm = normalize_turkish(meta.get("sector", ""))

        if not q or (q in sym or q in name_norm or q in sect_norm):
            results.append(StockInfo(
                symbol=sym,
                name=meta["name"],
                sector=meta["sector"],
                industry=meta.get("industry", "Genel"),
                ai_score=None
            ))

    # Sort alphabetically
    results.sort(key=lambda x: x.symbol)

    set_cached(cache_key, results, expire=3600)
    return results

@router.get("/{symbol}", response_model=Dict[str, Any])
async def get_stock_detail(symbol: str):
    """Crash-proof Stock Detail API (V4). Returns partial data instead of 500."""
    symbol = symbol.upper()

    # Validation
    all_syms = stock_registry.get_all_symbols()
    if symbol not in all_syms:
        # Check if we should try with .IS
        if f"{symbol}.IS" in all_syms: symbol = f"{symbol}.IS"
        else: raise HTTPException(status_code=404, detail="Stock not in registry.")

    cache_key = f"stock_detail_v4_{symbol}"
    cached = get_cached(cache_key)
    if cached: return cached

    try:
        data = stock_service.analyze_stock(symbol)
        if not data or data.history is None or data.history.empty:
            raise HTTPException(status_code=404, detail="Data provider returned no history.")

        # Robust execution of engines
        def run_safe(engine_func, *args):
            try: return engine_func(*args)
            except Exception: return {}

        tech = run_safe(technical_engine.calculate_metrics, data.history)
        fund = run_safe(fundamental_engine.calculate_metrics, data.info, data.income_stmt, data.balance_sheet, data.cash_flow)
        risk = run_safe(risk_engine.calculate_metrics, data.history, data.info)
        mom = run_safe(momentum_engine.calculate_metrics, data.history)
        trend = run_safe(trend_engine.calculate_metrics, data.history)
        vol = run_safe(volatility_engine.calculate_metrics, data.history)

        # Scoring
        metrics_map = {**tech, **fund, **risk, **mom, **trend, **vol}
        ai_score = scoring_engine.calculate_ai_score(metrics_map, "daily")
        conf = confidence_engine.calculate_confidence(tech, fund, risk, trend, data.info)

        stock_meta = stock_registry.get_stock_data(symbol)

        # Safe price extraction
        price = float(data.history['Close'].iloc[-1]) if not data.history.empty else 0.0
        change = 0.0
        if len(data.history) > 1:
            change = ((data.history['Close'].iloc[-1] / data.history['Close'].iloc[-2]) - 1) * 100

        detail = {
            "symbol": symbol,
            "company_name": stock_meta["name"],
            "sector": stock_meta["sector"],
            "price": price,
            "daily_change_pct": change,
            "ai_score": ai_score,
            "confidence": conf,
            "technical_score": tech.get("technical_score"),
            "fundamental_score": fund.get("fundamental_score"),
            "risk_score": risk.get("risk_score"),
            "momentum": mom,
            "trend": trend,
            "risk_metrics": risk,
            "timestamp": time.time()
        }

        set_cached(cache_key, detail, expire=600)
        return detail

    except HTTPException: raise
    except Exception as e:
        # Final fallback to prevent 500
        return {
            "symbol": symbol,
            "error": "Partial analysis failure",
            "message": str(e),
            "ai_score": 50,
            "confidence": 10
        }
