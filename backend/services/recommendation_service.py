import concurrent.futures
from typing import List
from ..schemas.recommendation import RecommendationResponse, RecommendationItem
from .registry_service import registry_service
from .stock_service import stock_service
from ..core.logger import logger

# Import all engines
from ..engines.technical_engine import technical_engine
from ..engines.fundamental_engine import fundamental_engine
from ..engines.risk_engine import risk_engine
from ..engines.growth_engine import growth_engine
from ..engines.value_engine import value_engine
from ..engines.momentum_engine import momentum_engine
from ..engines.trend_engine import trend_engine
from ..engines.sector_engine import sector_engine
from ..engines.volatility_engine import volatility_engine
from ..engines.liquidity_engine import liquidity_engine
from ..engines.catalyst_engine import catalyst_engine
from ..engines.dividend_engine import dividend_engine
from ..engines.confidence_engine import confidence_engine
from ..engines.scoring_engine import scoring_engine

class RecommendationService:
    """Professional Orchestrator with Parallel Processing."""

    def _analyze_single_symbol(self, symbol: str, strategy: str) -> RecommendationItem:
        """Internal helper to analyze one stock."""
        try:
            data = stock_service.analyze_stock(symbol)
            if not data or data.history is None:
                return None

            # Run All 12 Engines
            tech = technical_engine.calculate_metrics(data.history)
            fund = fundamental_engine.calculate_metrics(data.info, data.income_stmt, data.balance_sheet, data.cash_flow)
            risk = risk_engine.calculate_metrics(data.history, data.info)
            growth = growth_engine.calculate_metrics(data.info)
            value = value_engine.calculate_metrics(data.info)
            mom = momentum_engine.calculate_metrics(data.history)
            trend = trend_engine.calculate_metrics(data.history)
            sec = sector_engine.calculate_metrics(data.info)
            vol = volatility_engine.calculate_metrics(data.history)
            liq = liquidity_engine.calculate_metrics(data.history)
            cat = catalyst_engine.calculate_metrics(data.info)
            div = dividend_engine.calculate_metrics(data.info)

            # Aggregate all results for scoring
            all_scores = {**tech, **fund, **risk, **growth, **value, **mom,
                         **trend, **sec, **vol, **liq, **cat, **div}

            ai_score = scoring_engine.calculate_total_score(all_scores, strategy)
            conf = confidence_engine.calculate(tech, fund, risk)

            return RecommendationItem(
                symbol=symbol,
                company=registry_service.get_stock_info(symbol).name,
                ai_score=ai_score,
                technical_score=tech.get('technical_score', 50),
                fundamental_score=fund.get('fundamental_score', 50),
                risk_score=risk.get('risk_score', 50),
                recommendation_reason=self._generate_reason(strategy, ai_score, tech, fund, div),
                confidence=conf
            )
        except Exception as e:
            logger.error(f"[ERROR] Parallel Scan {symbol}: {str(e)}")
            return None

    async def get_recommendations(self, strategy: str) -> RecommendationResponse:
        logger.info(f"[SCAN START] Parallel Strategy: {strategy}")

        all_symbols = registry_service.get_all_symbols()
        recommendations = []

        # Professional Parallel Execution using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future_to_symbol = {executor.submit(self._analyze_single_symbol, s, strategy): s for s in all_symbols}
            for future in concurrent.futures.as_completed(future_to_symbol):
                result = future.result()
                if result:
                    recommendations.append(result)

        # Sort by AI Score descending
        recommendations.sort(key=lambda x: x.ai_score, reverse=True)
        top_10 = recommendations[:10]

        logger.info(f"[SCAN END] Strategy: {strategy} | Total Processed: {len(recommendations)}")

        return RecommendationResponse(
            strategy=strategy,
            count=len(top_10),
            recommendations=top_10
        )

    def _generate_reason(self, strategy: str, score: int, tech: dict, fund: dict, div: dict) -> str:
        """Dynamic reason generation based on actual metrics."""
        if strategy == "dividend" and div.get('dividend_score', 0) > 70:
            return "Exceptional dividend yield and payout stability detected."
        if score > 85:
            return "Institutional-grade pick with strong technical/fundamental alignment."
        if fund.get('fundamental_score', 0) > 75:
            return "High quality balance sheet and valuation discount."
        if tech.get('technical_score', 0) > 75:
            return "Strong momentum and bullish trend confirmation."

        return "Consistent performance within strategy specific risk parameters."

recommendation_service = RecommendationService()
