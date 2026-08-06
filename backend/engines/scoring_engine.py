from typing import Dict, Any
from ..core.logger import logger

class ScoringEngine:
    """Combines all 12 analysis scores into a final AI score based on Strategy."""

    def __init__(self):
        # Professional Strategy Weights
        self.strategy_weights = {
            "daily": {
                "technical_score": 0.40,
                "momentum_score": 0.30,
                "trend_score": 0.15,
                "liquidity_score": 0.10,
                "volatility_score": 0.05
            },
            "weekly": {
                "technical_score": 0.30,
                "momentum_score": 0.25,
                "trend_score": 0.20,
                "fundamental_score": 0.15,
                "risk_score": 0.10
            },
            "monthly": {
                "fundamental_score": 0.30,
                "trend_score": 0.25,
                "technical_score": 0.20,
                "growth_score": 0.15,
                "value_score": 0.10
            },
            "long-term": {
                "fundamental_score": 0.40,
                "growth_score": 0.30,
                "value_score": 0.20,
                "risk_score": 0.10
            },
            "dividend": {
                "dividend_score": 0.60,
                "fundamental_score": 0.20,
                "value_score": 0.10,
                "risk_score": 0.10
            },
            "value": {
                "value_score": 0.50,
                "fundamental_score": 0.30,
                "dividend_score": 0.10,
                "risk_score": 0.10
            },
            "high-growth": {
                "growth_score": 0.50,
                "momentum_score": 0.20,
                "fundamental_score": 0.20,
                "catalyst_score": 0.10
            },
            "high-risk": {
                "momentum_score": 0.40,
                "technical_score": 0.30,
                "volatility_score": 0.10, # Here volatility weight is positive because high risk seeks volatility
                "growth_score": 0.10,
                "catalyst_score": 0.10
            }
        }

    def calculate_total_score(self, scores: Dict[str, Any], strategy: str) -> int:
        weights = self.strategy_weights.get(strategy, {
            "technical_score": 0.20,
            "fundamental_score": 0.20,
            "growth_score": 0.15,
            "value_score": 0.10,
            "momentum_score": 0.10,
            "trend_score": 0.10,
            "risk_score": 0.15
        })

        total = 0.0
        weight_sum = 0.0

        for key, weight in weights.items():
            # Get the specific score from any motor that provides it
            val = scores.get(key, 50)
            total += val * weight
            weight_sum += weight

        if weight_sum > 0:
            final_score = int(total / weight_sum)
        else:
            final_score = 50

        final_score = min(max(final_score, 0), 100)
        logger.info(f"[TOTAL SCORE] Strategy: {strategy} | AI Score: {final_score}")
        return final_score

scoring_engine = ScoringEngine()
