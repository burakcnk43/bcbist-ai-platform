from typing import Dict, Any
from ..core.logger import logger

class CatalystEngine:
    """Forward-looking Catalyst and Sentiment Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        """Analyzes price targets, recommendations, and news sentiment (simulated)."""
        try:
            target_price = info.get('targetMeanPrice', 0)
            current_price = info.get('currentPrice', 1)
            rec_key = info.get('recommendationKey', 'none')

            # --- Catalyst Score (0-100) ---
            score = 50

            # Upside Potential
            if target_price > current_price:
                upside = (target_price / current_price) - 1
                if upside > 0.30: score += 30
                elif upside > 0.15: score += 15

            # Recommendation Trend
            if rec_key == 'strong_buy': score += 20
            elif rec_key == 'buy': score += 10

            metrics = {
                "upside": (target_price / current_price) - 1 if current_price > 0 else 0,
                "catalyst_score": min(max(score, 0), 100)
            }
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Catalyst Engine: {str(e)}")
            return {"catalyst_score": 50}

catalyst_engine = CatalystEngine()
