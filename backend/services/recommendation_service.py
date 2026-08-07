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
    """Professional Institutional-Grade Orchestrator for BIST Analysis."""

    def _analyze_single_stock(self, symbol: str, strategy: str) -> Optional[Dict[str, Any]]:
        """Processes full analysis pipeline for one stock with strict quality checks."""
        try:
            data = stock_service.analyze_stock(symbol)
            if not data or data.history is None or data.history.empty:
                return None

            # --- 1. Comprehensive Factor Calculation ---
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

            # --- 2. Multi-Factor Score Aggregation ---
            all_metrics = {**tech, **fund, **risk, **mom, **trend, **growth, **value, **div, **sec, **vol, **liq, **cat}
            ai_score = scoring_engine.calculate_ai_score(all_metrics, strategy)

            # --- 3. Independent Confidence Assessment ---
            conf = confidence_engine.calculate_confidence(tech, fund, risk)

            # --- 4. Strict Quality Enforcements (Strategy Specific) ---
            if not scoring_engine.is_eligible(ai_score, strategy):
                return None

            # Daily Quality Rules (Rule: min Confidence 70, min Tech 70, min Liquidity 50)
            if strategy == "daily":
                if conf < 70 or tech.get("technical_score", 0) < 70 or liq.get("liquidity_score", 0) < 50:
                    return None
                if trend.get("trend_score", 0) < 50: # Must be neutral/positive trend
                    return None

            # Long Term Quality (Rule: min Fund 70, min Growth 60)
            if strategy == "long-term":
                if fund.get("fundamental_score", 0) < 70 or growth.get("growth_score", 0) < 60:
                    return None

            stock_meta = stock_registry.get_stock_data(symbol)

            return {
                "rec": RecommendationItem(
                    symbol=symbol,
                    company=stock_meta["name"],
                    ai_score=ai_score,
                    technical_score=int(tech.get("technical_score", 50)),
                    fundamental_score=int(fund.get("fundamental_score", 50)),
                    risk_score=int(risk.get("risk_score", 50)),
                    recommendation_reason=self._generate_reason(strategy, ai_score, tech, fund, div),
                    confidence=conf
                ),
                "sector": stock_meta["sector"]
            }
        except Exception:
            return None

    async def get_recommendations(self, strategy: str) -> RecommendationResponse:
        """High-performance global market scanner with ranking and diversity."""
        start_time = time.time()

        # --- Cache Check ---
        cache_key = f"v2_final_recs_{strategy}"
        cached_res = get_cached(cache_key)
        if cached_res:
            return cached_res

        logger.info(f"[SCAN START] Full Market Scan: {strategy}")

        symbols = stock_registry.get_all_symbols()
        total_stocks = len(symbols)

        results = []
        failed_count = 0

        # --- Parallel Market Scanning (Institutional Scale) ---
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(self._analyze_single_stock, s, strategy): s for s in symbols}
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
                else:
                    failed_count += 1

        # --- Global Quality Ranking ---
        # Ensure we sort by AI Score descending across ALL analyzed stocks
        results.sort(key=lambda x: x["rec"].ai_score, reverse=True)
        valid_stocks = len(results)

        # --- Sector Diversification Logic (Max 2 per sector) ---
        final_list = []
        sector_counts = {}
        for item in results:
            sect = item["sector"]
            if sector_counts.get(sect, 0) < 2:
                final_list.append(item["rec"])
                sector_counts[sect] = sector_counts.get(sect, 0) + 1
            if len(final_list) >= 10:
                break

        exec_time = time.time() - start_time

        response = RecommendationResponse(
            strategy=strategy,
            count=len(final_list),
            recommendations=final_list
        )

        # Cache results to prevent redundant processing
        set_cached(cache_key, response, expire=1800)

        # Detailed Production Log
        logger.info(f"\n[BIST ALL PRODUCTION REPORT]\n"
                    f"STRATEGY         : {strategy}\n"
                    f"TOTAL MARKET     : {total_stocks}\n"
                    f"ANALYZED/VALID   : {valid_stocks}\n"
                    f"FAILED/FILTERED  : {total_stocks - valid_stocks}\n"
                    f"TOP 10 DIVERSE   : {len(final_list)}\n"
                    f"EXECUTION TIME   : {exec_time:.2f} sec")

        return response

    def _generate_reason(self, strategy: str, score: int, tech: dict, fund: dict, div: dict) -> str:
        """Generates dynamic investment rationales based on factor convergence."""
        if score > 90:
            return "Exceptional multi-factor convergence with top-tier institutional metrics."
        if strategy == "dividend" and div.get("dividend_score", 0) > 85:
            return "Leading dividend yield profile with elite payout sustainability."
        if tech.get("technical_score", 0) > 85:
            return "Strong bullish momentum confirmed by institutional trend indicators."
        if fund.get("fundamental_score", 0) > 85:
            return "Premium balance sheet quality with significant intrinsic value gap."
        return "High-probability signal derived from synchronized market factors."

recommendation_service = RecommendationService()
