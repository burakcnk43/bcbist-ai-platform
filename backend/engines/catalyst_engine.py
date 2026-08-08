from typing import Dict, Any
import numpy as np
from core.logger import logger

class CatalystEngine:
    """Forward-looking Catalyst and Sentiment Engine (V4)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            target = info.get('targetMeanPrice')
            current = info.get('currentPrice')

            if target and current and current > 0:
                upside = (float(target) / float(current)) - 1
                score = 50
                if upside > 0.30: score = 90
                elif upside > 0.15: score = 75
                elif upside < 0: score = 30

                return {
                    "upside": float(upside),
                    "catalyst_score": score
                }

            return {"catalyst_score": None}
        except Exception:
            return {"catalyst_score": None}

catalyst_engine = CatalystEngine()
