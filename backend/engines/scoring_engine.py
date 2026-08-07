from typing import Dict, Any
from ..core.logger import logger

class ScoringEngine:
    """Professional Multi-Factor Weighted Scoring Engine with V3 Thresholds."""

    def __init__(self):
        # Institutional Strategy Weights and Minimum Thresholds (V3)
        self.strategy_config = {
            "daily": {
                "weights": {
                    "technical_score": 0.30,
                    "momentum_score": 0.20,
                    "trend_score": 0.10,
                    "volatility_score": 0.05,
                    "liquidity_score": 0.10,
                    "fundamental_score": 0.05,
                    "growth_score": 0.05,
                    "value_score": 0.05,
                    "risk_score": 0.05,
                    "catalyst_score": 0.05,
                    "sector_score": 0.05
                },
                "thresholds": {
                    "min_ai_score": 80,
                    "min_technical": 75,
                    "min_confidence": 75
                }
            },
            "long-term": {
                "weights": {
                    "fundamental_score": 0.35,
                    "growth_score": 0.20,
                    "value_score": 0.15,
                    "dividend_score": 0.10,
                    "risk_score": 0.05,
                    "technical_score": 0.05,
                    "trend_score": 0.05,
                    "catalyst_score": 0.05,
                    "sector_score": 0.05
                },
                "thresholds": {
                    "min_ai_score": 82,
                    "min_fundamental": 75,
                    "min_confidence": 80
                }
            }
        }

    def calculate_ai_score(self, metrics: Dict[str, Any], strategy: str) -> int:
        """Calculates 0-100 AI Score with multi-factor influence."""
        try:
            config = self.strategy_config.get(strategy, self.strategy_config["daily"])
            weights = config["weights"]

            total_weighted_score = 0.0
            weight_sum = 0.0

            for key, weight in weights.items():
                val = metrics.get(key, 50)
                total_weighted_score += float(val) * weight
                weight_sum += weight

            if weight_sum > 0:
                final_score = int(total_weighted_score / weight_sum)
            else:
                final_score = 50

            return min(max(final_score, 0), 100)
        except Exception as e:
            logger.error(f"[SCORING ENGINE ERROR] {str(e)}")
            return 50

    def is_highly_eligible(self, metrics: Dict[str, Any], strategy: str) -> bool:
        """Strict V3 quality check."""
        config = self.strategy_config.get(strategy, self.strategy_config["daily"])
        thresh = config["thresholds"]

        if metrics.get("ai_score", 0) < thresh["min_ai_score"]: return False
        if metrics.get("confidence", 0) < thresh["min_confidence"]: return False

        if strategy == "daily":
            if metrics.get("technical_score", 0) < thresh["min_technical"]: return False
        elif strategy == "long-term":
            if metrics.get("fundamental_score", 0) < thresh["min_fundamental"]: return False

        return True

scoring_engine = ScoringEngine()
