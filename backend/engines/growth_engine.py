from typing import Dict, Any
import numpy as np
from ..core.logger import logger

class GrowthEngine:
    """Institutional Grade Growth Analysis Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        """Calculates revenue/EPS growth quality and momentum."""
        try:
            # 1. Revenue Growth
            rev_growth = info.get('revenueGrowth', 0) or 0
            rev_quarters = info.get('revenueQuarterlyGrowth', 0) or 0

            # 2. EPS Growth
            eps_growth = info.get('earningsGrowth', 0) or 0
            eps_quarters = info.get('earningsQuarterlyGrowth', 0) or 0

            # 3. Margin Expansion (Efficiency Growth)
            gross_margin = info.get('grossMargins', 0) or 0
            operating_margin = info.get('operatingMargins', 0) or 0

            # --- Growth Score Logic (0-100) ---
            score = 50

            # Top-line Growth (Max 25 pts)
            if rev_growth > 0.30: score += 25
            elif rev_growth > 0.15: score += 15
            elif rev_growth < 0: score -= 15

            # Bottom-line Growth (Max 25 pts)
            if eps_growth > 0.25: score += 25
            elif eps_growth > 0.10: score += 15
            elif eps_growth < 0: score -= 15

            # Quarterly Momentum (Max 10 pts)
            if rev_quarters > 0.10 or eps_quarters > 0.10:
                score += 10

            metrics = {
                "revenue_growth": rev_growth,
                "eps_growth": eps_growth,
                "growth_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[GROWTH ENGINE ERROR] {str(e)}")
            return {"growth_score": 50}

growth_engine = GrowthEngine()
