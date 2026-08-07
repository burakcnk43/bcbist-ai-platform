import time
import concurrent.futures
from typing import List, Dict, Any, Optional
from ..schemas.recommendation import RecommendationResponse, RecommendationItem
from .stock_registry import stock_registry
from .stock_service import stock_service
from ..core.logger import logger
from ..core.cache import get_cached, set_cached

# Engine Imports
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
    """Professional Institutional-Grade Orchestrator for BIST Analysis."""

    def _analyze_single_stock(self, symbol: str, strategy: str) -> Optional[Dict[str, Any]]:
        """Processes full analysis pipeline for one stock."""
        try:
            data = stock_service.analyze_stock(symbol)
            if not data or data.history is None or data.history.empty:
                return None

            # 1. Component Metrics
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

            # 2. Independent Confidence Calculation
            conf = confidence_engine.calculate_confidence(tech, fund, risk, trend, data.info)

            # 3. Score Aggregation
            metrics_map = {
                **tech, **fund, **risk, **mom, **trend, **growth, **value,
                **div, **sec, **vol, **liq, **cat, "confidence": conf
            }
            ai_score = scoring_engine.calculate_ai_score(metrics_map, strategy)
            metrics_map["ai_score"] = ai_score

            stock_meta = stock_registry.get_stock_data(symbol)

            return {
                "metrics": metrics_map,
                "item": RecommendationItem(
                    symbol=symbol,
                    company=stock_meta["name"],
                    ai_score=ai_score,
                    technical_score=int(tech.get("technical_score", 50)),
                    fundamental_score=int(fund.get("fundamental_score", 50)),
                    risk_score=int(risk.get("risk_score", 50)),
                    recommendation_reason="", # Filled later
                    confidence=conf
                ),
                "sector": stock_meta["sector"]
            }
        except Exception as e:
            return None

    async def get_recommendations(self, strategy: str) -> RecommendationResponse:
        """Executes parallel scan across all BIST stocks and ranks results with multi-stage fallbacks."""
        start_time = time.time()

        # Cache Check
        cache_key = f"v3_recs_{strategy}"
        cached_res = get_cached(cache_key)
        if cached_res:
            return cached_res

        symbols = stock_registry.get_all_symbols()
        total_count = len(symbols)

        raw_results = []

        # 1. Full Market Scanning (Parallel)
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(self._analyze_single_stock, s, strategy): s for s in symbols}
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res: raw_results.append(res)

        analyzed_count = len(raw_results)

        # 2. Stage 1: Strict Filtering
        stage1 = [r for r in raw_results if scoring_engine.check_eligibility(r["metrics"], strategy, mode="strict")]

        # 3. Stage 2: Fallback Filtering
        if not stage1:
            stage2 = [r for r in raw_results if scoring_engine.check_eligibility(r["metrics"], strategy, mode="fallback")]
            selected_results = stage2
            warning = "No stock met institutional thresholds today. High quality candidates are shown."
        else:
            selected_results = stage1
            warning = None

        # 4. Stage 3: Global Ranking (If still nothing, pick best of ALL)
        if not selected_results:
            raw_results.sort(key=lambda x: x["item"].ai_score, reverse=True)
            selected_results = raw_results[:1] # Take at least the best one
            warning = "Market conditions do not meet quality criteria. Showing best available candidate."

        # 5. Global Ranking for Final Selection
        selected_results.sort(key=lambda x: x["item"].ai_score, reverse=True)

        # 6. Sector Diversity (Max 2 per sector)
        final_recs = []
        sector_counts = {}
        for res in selected_results:
            sect = res["sector"]
            if sector_counts.get(sect, 0) < 2:
                item = res["item"]
                item.recommendation_reason = warning if warning else self._generate_reason(strategy, item.ai_score, res["metrics"])
                final_recs.append(item)
                sector_counts[sect] = sector_counts.get(sect, 0) + 1
            if len(final_recs) >= 10:
                break

        exec_time = time.time() - start_time

        # BIST EXECUTION REPORT
        logger.info(f"\n[BIST EXECUTION REPORT]\n"
                    f"STOCKS SCANNED  : {total_count}\n"
                    f"VALID/ANALYZED  : {analyzed_count}\n"
                    f"FILTERED        : {len(selected_results)}\n"
                    f"TOP SCORE       : {selected_results[0]['item'].ai_score if selected_results else 0}\n"
                    f"RETURNED        : {len(final_recs)}\n"
                    f"EXECUTION TIME  : {exec_time:.2f} sec\n"
                    f"STRATEGY        : {strategy}")

        response = RecommendationResponse(
            strategy=strategy,
            count=len(final_recs),
            recommendations=final_recs
        )

        set_cached(cache_key, response, expire=1800)
        return response

    def _generate_reason(self, strategy: str, score: int, metrics: dict) -> str:
        """Dynamic institutional rationale generation."""
        if score > 88: return "Exceptional multi-factor convergence with high institutional conviction."
        if strategy == "daily" and metrics.get("technical_score", 0) > 80:
            return "Strong bullish momentum confirmed by institutional trend indicators."
        if strategy == "long-term" and metrics.get("fundamental_score", 0) > 80:
            return "Premium quality balance sheet with significant intrinsic value gap."
        return "High-probability signal derived from synchronized market factors."

recommendation_service = RecommendationService()
