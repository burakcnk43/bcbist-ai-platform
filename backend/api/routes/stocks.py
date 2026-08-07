import time
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ...services.stock_registry import stock_registry
from ...services.stock_service import stock_service
from ...schemas.stock import StockInfo
from ...core.cache import get_cached, set_cached

# Engine Imports for Detailed Analysis
from ...engines.technical_engine import technical_engine
from ...engines.fundamental_engine import fundamental_engine
from ...engines.risk_engine import risk_engine
from ...engines.momentum_engine import momentum_engine
from ...engines.trend_engine import trend_engine
from ...engines.growth_engine import growth_engine
from ...engines.value_engine import value_engine
from ...engines.dividend_engine import dividend_engine
from ...engines.sector_engine import sector_engine
from ...engines.volatility_engine import volatility_engine
from ...engines.liquidity_engine import liquidity_engine
from ...engines.confidence_engine import confidence_engine
from ...engines.catalyst_engine import catalyst_engine
from ...engines.scoring_engine import scoring_engine

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/search", response_model=List[StockInfo])
async def search_stocks(query: str):
    """Fast case-insensitive search for stocks by ticker, company, or sector."""
    cache_key = f"search_v3_{query.lower()}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    q = query.upper()
    symbols = stock_registry.get_all_symbols()
    results = []

    for symbol in symbols:
        meta = stock_registry.get_stock_data(symbol)
        if q in symbol or q in meta["name"].upper() or q in meta.get("sector", "").upper():
            results.append(StockInfo(
                symbol=symbol,
                name=meta["name"],
                sector=meta["sector"],
                industry=meta.get("industry", "Genel"),
                ai_score=None # Deferred to detail or recs
            ))

    set_cached(cache_key, results, expire=3600)
    return results

@router.get("/{symbol}", response_model=Dict[str, Any])
async def get_stock_detail(symbol: str):
    """Returns every available institutional-grade metric for a specific stock."""
    symbol = symbol.upper()

    cache_key = f"stock_detail_v3_{symbol}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    data = stock_service.analyze_stock(symbol)
    if not data or data.history is None or data.history.empty:
        raise HTTPException(status_code=404, detail="Stock analysis data unavailable.")

    # 1. Component Deep Dive
    tech = technical_engine.calculate_metrics(data.history)
    fund = fundamental_engine.calculate_metrics(data.info, data.income_stmt, data.balance_sheet, data.cash_flow)
    risk = risk_engine.calculate_metrics(data.history, data.info)
    mom = momentum_engine.calculate_metrics(data.history)
    trend = trend_engine.calculate_metrics(data.history)
    growth = growth_engine.calculate_metrics(data.info)
    val = value_engine.calculate_metrics(data.info)
    div = dividend_engine.calculate_metrics(data.info)
    sec = sector_engine.calculate_metrics(data.info)
    vola = volatility_engine.calculate_metrics(data.history)
    liq = liquidity_engine.calculate_metrics(data.history)
    cat = catalyst_engine.calculate_metrics(data.info)

    # 2. Comprehensive AI Score & Confidence
    metrics_map = {**tech, **fund, **risk, **mom, **trend, **growth, **val, **div, **sec, **vola, **liq, **cat}
    ai_score = scoring_engine.calculate_ai_score(metrics_map, "daily")
    conf = confidence_engine.calculate_confidence(tech, fund, risk, trend, data.info)

    stock_meta = stock_registry.get_stock_data(symbol)

    detail = {
        "symbol": symbol,
        "company_name": stock_meta["name"],
        "sector": stock_meta["sector"],
        "industry": stock_meta["industry"],
        "price": data.history['Close'].iloc[-1],
        "daily_change_pct": ((data.history['Close'].iloc[-1] / data.history['Close'].iloc[-2]) - 1) * 100 if len(data.history) > 1 else 0,
        "ai_scores": {
            "overall": ai_score,
            "confidence": conf,
            "technical": tech.get("technical_score", 50),
            "fundamental": fund.get("fundamental_score", 50),
            "risk": risk.get("risk_score", 50)
        },
        "engines": {
            "momentum": mom,
            "trend": trend,
            "growth": growth,
            "valuation": val,
            "dividend": div,
            "volatility": vola,
            "liquidity": liq,
            "catalyst": cat,
            "sector_relative": sec
        },
        "key_ratios": fund,
        "technical_indicators": tech,
        "risk_metrics": risk,
        "institutional_opinion": "Strong Conviction" if ai_score > 85 else "Neutral Outlook",
        "timestamp": time.time()
    }

    set_cached(cache_key, detail, expire=1800)
    return detail
