import time
import concurrent.futures
from typing import List, Dict, Any, Optional

# Absolute Package Imports for Production Stability
from backend.schemas.recommendation import RecommendationResponse, RecommendationItem
from backend.services.stock_registry import stock_registry
from backend.services.stock_service import stock_service
from backend.core.logger import logger
from backend.core.cache import get_cached, set_cached

# Engine Imports
from backend.engines.technical_engine import technical_engine
from backend.engines.fundamental_engine import fundamental_engine
from backend.engines.risk_engine import risk_engine
from backend.engines.momentum_engine import momentum_engine
from backend.engines.trend_engine import trend_engine
from backend.engines.scoring_engine import scoring_engine
from backend.engines.confidence_engine import confidence_engine
from backend.engines.volatility_engine import volatility_engine

class RecommendationService:
    """Institutional-Grade Orchestrator for Full BIST V4 Scan."""

    def _analyze_single_stock(self, symbol: str, strategy: str) -> Optional[Dict[str, Any]]:
        try:
            data = stock_service.analyze_stock(symbol)
            if not data or data.history is None or data.history.empty:
                return None

            # Safe Engine Execution
            def run_safe(func, *args):
                try: return func(*args)
                except Exception: return {}

            tech = run_safe(technical_engine.calculate_metrics, data.history)
            fund = run_safe(fundamental_engine.calculate_metrics, data.info, data.income_stmt, data.balance_sheet, data.cash_flow)
            risk = run_safe(risk_engine.calculate_metrics, data.history, data.info)
            mom = run_safe(momentum_engine.calculate_metrics, data.history)
            trend = run_safe(trend_engine.calculate_metrics, data.history)
            vol = run_safe(volatility_engine.calculate_metrics, data.history)

            # Score & Confidence
            all_metrics = {**tech, **fund, **risk, **mom, **trend, **vol}
            ai_score = scoring_engine.calculate_ai_score(all_metrics, strategy)
            conf = confidence_engine.calculate_confidence(tech, fund, risk, trend, data.info)

            metrics_final = {**all_metrics, "ai_score": ai_score, "confidence": conf}

            if not scoring_engine.is_highly_eligible(metrics_final, strategy):
                return None

            stock_meta = stock_registry.get_stock_data(symbol)

            return {
                "metrics": metrics_final,
                "item": RecommendationItem(
                    symbol=symbol,
                    company=stock_meta["name"],
                    ai_score=ai_score,
                    technical_score=int(tech.get("technical_score", 50)) if tech.get("technical_score") else 50,
                    fundamental_score=int(fund.get("fundamental_score", 50)) if fund.get("fundamental_score") else 50,
                    risk_score=int(risk.get("risk_score", 50)) if risk.get("risk_score") else 50,
                    recommendation_reason="BIST V4 Quant Signal",
                    confidence=conf
                ),
                "sector": stock_meta["sector"]
            }
        except Exception:
            return None

    async def get_recommendations(self, strategy: str) -> RecommendationResponse:
        cache_key = f"v4_recs_{strategy}"
        cached = get_cached(cache_key)
        if cached: return cached

        symbols = stock_registry.get_all_symbols()
        results_pool = []

        # Balanced concurrency for yfinance (20 workers instead of 40 to avoid rate limits)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self._analyze_single_stock, s, strategy): s for s in symbols}
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res: results_pool.append(res)

        # Global Rank
        results_pool.sort(key=lambda x: x["item"].ai_score, reverse=True)

        # Sector Diversification (Max 2)
        final_list = []
        sector_counts = {}
        for res in results_pool:
            sect = res["sector"]
            if sector_counts.get(sect, 0) < 2:
                final_list.append(res["item"])
                sector_counts[sect] = sector_counts.get(sect, 0) + 1
            if len(final_list) >= 10: break

        response = RecommendationResponse(
            strategy=strategy,
            count=len(final_list),
            recommendations=final_list
        )

        set_cached(cache_key, response, expire=3600)
        return response

recommendation_service = RecommendationService()
