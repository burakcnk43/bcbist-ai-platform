from typing import Dict, Any
import numpy as np
from core.logger import logger

class GrowthEngine:
    """Institutional Grade Growth Analysis Engine (V4)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            def safe_f(val):
                try:
                    if val is None: return None
                    f = float(val)
                    return f if not np.isnan(f) and not np.isinf(f) else None
                except: return None

            rev_growth = safe_f(info.get('revenueGrowth'))
            eps_growth = safe_f(info.get('earningsGrowth'))

            score_pts = []
            if rev_growth is not None: score_pts.append(100 if rev_growth > 0.20 else (50 if rev_growth > 0 else 0))
            if eps_growth is not None: score_pts.append(100 if eps_growth > 0.15 else (50 if eps_growth > 0 else 0))

            return {
                "revenue_growth": rev_growth,
                "eps_growth": eps_growth,
                "growth_score": int(sum(score_pts)/len(score_pts)) if score_pts else None
            }
        except Exception:
            return {"growth_score": None}

growth_engine = GrowthEngine()
