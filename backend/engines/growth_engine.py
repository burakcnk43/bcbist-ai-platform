from typing import Dict, Any
from ..core.logger import logger

class GrowthEngine:
    """Professional Growth Analysis Engine (Revenue/EPS CAGR & Stability)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            rev_growth = info.get('revenueGrowth', 0) or 0
            eps_growth = info.get('earningsGrowth', 0) or 0
            rev_quarters = info.get('revenueQuarterlyGrowth', 0) or 0

            # Growth Score (0-100)
            score = 0

            # Revenue Growth (Max 40 pts)
            if rev_growth > 0.30: score += 40
            elif rev_growth > 0.15: score += 25
            elif rev_growth > 0.05: score += 10

            # EPS Growth (Max 40 pts)
            if eps_growth > 0.25: score += 40
            elif eps_growth > 0.10: score += 20

            # Quarterly Momentum (Max 20 pts)
            if rev_quarters > 0.10: score += 20

            metrics = {
                "revenue_growth": rev_growth,
                "eps_growth": eps_growth,
                "growth_score": min(score, 100)
            }
            logger.info(f"[GROWTH] Final Score: {metrics['growth_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Growth Engine: {str(e)}")
            return {"growth_score": 50}

growth_engine = GrowthEngine()
