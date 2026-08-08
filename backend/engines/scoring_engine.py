from typing import Dict, Any
from backend.core.logger import logger

class ScoringEngine:
    """Professional Multi-Factor Dynamic Weighted Scoring Engine (V4)."""

    def __init__(self):
        self.strategy_config = {
            "daily": {
                "weights": {
                    "technical_score": 0.40,
                    "momentum_score": 0.30,
                    "trend_score": 0.10,
                    "volatility_score": 0.10,
                    "liquidity_score": 0.10
                },
                "thresholds": {"min_ai_score": 75}
            },
            "long-term": {
                "weights": {
                    "fundamental_score": 0.50,
                    "growth_score": 0.20,
                    "value_score": 0.15,
                    "risk_score": 0.10,
                    "dividend_score": 0.05
                },
                "thresholds": {"min_ai_score": 70}
            }
        }

    def calculate_ai_score(self, metrics: Dict[str, Any], strategy: str) -> int:
        """Calculates 0-100 AI Score using ONLY available metrics (V4)."""
        try:
            config = self.strategy_config.get(strategy, self.strategy_config["daily"])
            weights = config["weights"]

            total_weighted_val = 0.0
            total_active_weight = 0.0

            for key, weight in weights.items():
                val = metrics.get(key)
                if val is not None:
                    total_weighted_val += float(val) * weight
                    total_active_weight += weight

            if total_active_weight > 0:
                final_score = int(total_weighted_val / total_active_weight)
                return min(max(final_score, 0), 100)

            return 50 # Default neutral if no metrics available
        except Exception as e:
            logger.error(f"[SCORING ERROR] {str(e)}")
            return 50

    def is_highly_eligible(self, metrics: Dict[str, Any], strategy: str) -> bool:
        ai_score = metrics.get("ai_score", 0)
        conf = metrics.get("confidence", 0)
        thresh = self.strategy_config.get(strategy, {}).get("thresholds", {"min_ai_score": 75})

        return ai_score >= thresh["min_ai_score"] and conf >= 70

scoring_engine = ScoringEngine()
