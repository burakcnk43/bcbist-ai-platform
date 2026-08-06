from typing import Dict, Any
from ..core.logger import logger

class CatalystEngine:
    """Catalyst Analysis Engine (Dividend news, target price gaps)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            score = 50

            # 1. Target Price Gap
            target = info.get('targetMedianPrice', 0) or 0
            current = info.get('currentPrice', 1)
            if target > current:
                gap = (target / current) - 1
                if gap > 0.30: score += 30
                elif gap > 0.15: score += 15

            # 2. Recommendation Trend
            rec = info.get('recommendationKey', 'none')
            if rec == 'strong_buy': score += 20
            elif rec == 'buy': score += 10

            logger.info(f"[CATALYST] Final Score: {score}")
            return {"catalyst_score": min(score, 100)}
        except Exception as e:
            logger.error(f"[ERROR] Catalyst Engine: {str(e)}")
            return {"catalyst_score": 50}

catalyst_engine = CatalystEngine()
