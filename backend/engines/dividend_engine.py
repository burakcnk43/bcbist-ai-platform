from typing import Dict, Any
import numpy as np
from backend.core.logger import logger

class DividendEngine:
    """Institutional Grade Dividend Analysis Engine (V4)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            def safe_f(val):
                try:
                    if val is None: return None
                    f = float(val)
                    return f if not np.isnan(f) and not np.isinf(f) else None
                except: return None

            yield_val = safe_f(info.get('dividendYield'))
            payout = safe_f(info.get('payoutRatio'))

            score = 0
            if yield_val:
                if yield_val > 0.05: score = 100
                elif yield_val > 0.02: score = 70
                else: score = 40

            return {
                "dividend_yield": yield_val,
                "payout_ratio": payout,
                "dividend_score": score if yield_val is not None else None
            }
        except Exception:
            return {"dividend_score": None}

dividend_engine = DividendEngine()
