from typing import Dict, Any
from ..core.logger import logger

class GrowthEngine:
    """Growth Potential and Stability Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            rev_growth = info.get('revenueGrowth', 0)
            eps_growth = info.get('earningsGrowth', 0)
            fcf_growth = info.get('freeCashflow', 0) # Simplification for growth

            # Growth Stability (CAGR Proxy)
            growth_score = (rev_growth * 0.4 + eps_growth * 0.6) * 100

            metrics = {
                "rev_growth": rev_growth,
                "eps_growth": eps_growth,
                "growth_score_raw": growth_score
            }

            # --- Final Growth Score (0-100) ---
            score = 50
            if rev_growth > 0.20: score += 20
            if eps_growth > 0.15: score += 30

            metrics['growth_score'] = min(max(score, 0), 100)
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Growth Engine: {str(e)}")
            return {"growth_score": 50}

growth_engine = GrowthEngine()
