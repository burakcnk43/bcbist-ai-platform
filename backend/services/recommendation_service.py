import time
import concurrent.futures
from typing import List, Dict, Any, Optional
from ..schemas.recommendation import RecommendationResponse, RecommendationItem
from .stock_registry import stock_registry
from .stock_service import stock_service
from ..core.logger import logger
from ..core.cache import get_cached, set_cached

# Institutional Engine Imports
from ..engines.technical_engine import technical_engine
from ..engines.fundamental_engine import fundamental_engine
from ..engines.risk_engine import risk_engine
from ..engines.momentum_engine import momentum_engine
from ..engines.trend_engine import trend_engine
from ..engines.growth_engine import growth_engine
from ..engines.value_engine import value_engine
from ..engines.dividend_engine import dividend_engine
from ..engines.sector_engine import sector_engine
from ..engines.volatility_engine import volatility_engine
from ..engines.liquidity_engine import liquidity_engine
from ..engines.confidence_engine import confidence_engine
from ..engines.catalyst_engine import catalyst_engine
from ..engines.scoring_engine import scoring_engine

class RecommendationService:
    """Institutional-Grade Orchestrator for BIST V3 Analysis."""

    def _analyze_single_stock(self, symbol: str, strategy: str) -> Optional[Dict[str, Any]]:
        """Processes full analysis pipeline for one stock."""
        try:
            data = stock_service.analyze_stock(symbol)
            if not data or data.history is None or data.history.empty:
                return None

            # --- 1. Multi-Factor Metrics ---
            tech = technical_engine.calculate_metrics(data.history)
            fund = fundamental_engine.calculate_metrics(data.info, data.income_stmt, data.balance_sheet, data.cash_flow)
            risk = risk_engine.calculate_metrics(data.history, data.info)
            mom = momentum_engine.calculate_metrics(data.history)
            trend = trend_engine.calculate_metrics(data.history)
            growth = growth_engine.calculate_metrics(data.info)
            value = value_engine.calculate_metrics(data.info)
            div = dividend_engine.calculate_metrics(data.info)
            sec = sector_engine.calculate_metrics(data.info)
            vol = volatility_engine.calculate_metrics(data.history)
            liq = liquidity_engine.calculate_metrics(data.history)
            cat = catalyst_engine.calculate_metrics(data.info)

            # --- 2. Score Aggregation ---
            all_metrics = {**tech, **fund, **risk, **mom, **trend, **growth, **value, **div, **sec, **vol, **liq, **cat}
            ai_score = scoring_engine.calculate_ai_score(all_metrics, strategy)

            # --- 3. Independent Confidence ---
            conf = confidence_engine.calculate_confidence(tech, fund, risk, trend, data.info)

            metrics_final = {**all_metrics, "ai_score": ai_score, "confidence": conf}

            stock_meta = stock_registry.get_stock_data(symbol)

            return {
                "metrics": metrics_final,
                "item": RecommendationItem(
                    symbol=symbol,
                    company=stock_meta["name"],
                    ai_score=ai_score,
                    technical_score=int(tech.get("technical_score", 50)),
                    fundamental_score=int(fund.get("fundamental_score", 50)),
                    risk_score=int(risk.get("risk_score", 50)),
                    recommendation_reason="", # Population later
                    confidence=conf
                ),
                "sector": stock_meta["sector"]
            }
        except Exception:
            return None

    async def get_recommendations(self, strategy: str) -> RecommendationResponse:
        """High-performance global market scanner with V3 filtering and ranking."""
        start_time = time.time()

        # Cache Check
        cache_key = f"v3_recs_{strategy}"
        cached_res = get_cached(cache_key)
        if cached_res:
            return cached_res

        logger.info(f"[SCAN START] Full BIST Scan V3: {strategy}")

        symbols = stock_registry.get_all_symbols()
        total_stocks = len(symbols)

        results_pool = []

        # Parallel Execution (40 Workers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(self._analyze_single_stock, s, strategy): s for s in symbols}
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res: results_pool.append(res)

        analyzed_count = len(results_pool)

        # --- Stage 1: High Quality Filter ---
        v3_candidates = [r for r in results_pool if scoring_engine.is_highly_eligible(r["metrics"], strategy)]

        # --- Stage 2: Fallback (Zero Empty Responses) ---
        if not v3_candidates:
            # If nothing hits strict V3 thresholds, take the best available from the whole pool
            results_pool.sort(key=lambda x: x["item"].ai_score, reverse=True)
            v3_candidates = results_pool[:20] # Take top 20 to pick diverse ones
            warning_msg = "Market criteria below institutional thresholds. Highest quality candidate selected."
        else:
            warning_msg = None

        # --- Stage 3: Global Ranking ---
        v3_candidates.sort(key=lambda x: x["item"].ai_score, reverse=True)

        # --- Stage 4: Sector Diversity (Max 2) ---
        final_list = []
        sector_counts = {}
        for res in v3_candidates:
            sect = res["sector"]
            if sector_counts.get(sect, 0) < 2:
                item = res["item"]
                item.recommendation_reason = warning_msg if warning_msg else self._generate_reason(strategy, item.ai_score, res["metrics"])
                final_list.append(item)
                sector_counts[sect] = sector_counts.get(sect, 0) + 1
            if len(final_list) >= 10:
                break

        exec_time = time.time() - start_time

        response = RecommendationResponse(
            strategy=strategy,
            count=len(final_list),
            recommendations=final_list
        )

        set_cached(cache_key, response, expire=1800)

        # Institutional Execution Report
        logger.info(f"\n[BIST EXECUTION REPORT V3]\n"
                    f"STRATEGY        : {strategy}\n"
                    f"STOCKS SCANNED  : {total_stocks}\n"
                    f"VALID/ANALYZED  : {analyzed_count}\n"
                    f"FILTERED (V3)   : {len(v3_candidates)}\n"
                    f"TOP SCORE       : {v3_candidates[0]['item'].ai_score if v3_candidates else 0}\n"
                    f"RETURNED        : {len(final_list)}\n"
                    f"EXECUTION TIME  : {exec_time:.2f} sec")

        return response

    def _generate_reason(self, strategy: str, score: int, metrics: dict) -> str:
        """Dynamic institutional rationale."""
        if score > 88: return "Exceptional multi-factor alignment with high institutional conviction."
        if strategy == "daily" and metrics.get("technical_score", 0) > 80:
            return "Powerful bullish momentum confirmed by institutional indicators."
        if strategy == "long-term" and metrics.get("fundamental_score", 0) > 80:
            return "Premium fundamental quality with robust growth stability."
        return "High-probability signal derived from synchronized market data."

recommendation_service = RecommendationService()
