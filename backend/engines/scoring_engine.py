from typing import Dict, Any
from ..core.logger import logger

class ScoringEngine:
    """Professional Multi-Factor Weighted Scoring Engine with Institutional Configuration."""

    def __init__(self):
        # Comprehensive Strategy Configuration
        self.strategy_config = {
            "daily": {
                "weights": {
                    "technical_score": 0.35,
                    "momentum_score": 0.25,
                    "trend_score": 0.10,
                    "liquidity_score": 0.10,
                    "volatility_score": 0.10,
                    "sector_score": 0.05,
                    "risk_score": 0.05
                },
                "min_score": 75
            },
            "weekly": {
                "weights": {
                    "technical_score": 0.25,
                    "momentum_score": 0.20,
                    "trend_score": 0.15,
                    "fundamental_score": 0.15,
                    "risk_score": 0.10,
                    "sector_score": 0.10,
                    "liquidity_score": 0.05
                },
                "min_score": 72
            },
            "monthly": {
                "weights": {
                    "fundamental_score": 0.25,
                    "trend_score": 0.20,
                    "growth_score": 0.15,
                    "value_score": 0.10,
                    "technical_score": 0.10,
                    "risk_score": 0.10,
                    "sector_score": 0.10
                },
                "min_score": 75
            },
            "long-term": {
                "weights": {
                    "fundamental_score": 0.35,
                    "growth_score": 0.25,
                    "value_score": 0.15,
                    "dividend_score": 0.10,
                    "risk_score": 0.10,
                    "sector_score": 0.05
                },
                "min_score": 80
            },
            "dividend": {
                "weights": {
                    "dividend_score": 0.55,
                    "fundamental_score": 0.20,
                    "value_score": 0.10,
                    "risk_score": 0.10,
                    "sector_score": 0.05
                },
                "min_score": 78
            },
            "value": {
                "weights": {
                    "value_score": 0.45,
                    "fundamental_score": 0.25,
                    "dividend_score": 0.10,
                    "risk_score": 0.10,
                    "sector_score": 0.10
                },
                "min_score": 76
            },
            "high-growth": {
                "weights": {
                    "growth_score": 0.45,
                    "momentum_score": 0.15,
                    "fundamental_score": 0.15,
                    "catalyst_score": 0.10,
                    "technical_score": 0.10,
                    "risk_score": 0.05
                },
                "min_score": 80
            },
            "high-risk": {
                "weights": {
                    "momentum_score": 0.35,
                    "volatility_score": 0.25,
                    "technical_score": 0.15,
                    "catalyst_score": 0.10,
                    "growth_score": 0.10,
                    "risk_score": 0.05
                },
                "min_score": 70
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
                # Default to neutral 50 if a metric is missing
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

    def is_eligible(self, score: int, strategy: str) -> bool:
        """Enforces high-quality institutional thresholds."""
        config = self.strategy_config.get(strategy, self.strategy_config["daily"])
        return score >= config["min_score"]

scoring_engine = ScoringEngine()
