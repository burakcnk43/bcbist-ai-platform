from typing import Dict, Any
import numpy as np
from core.logger import logger

class ValueEngine:
    """Valuation and Margin of Safety Engine (V4)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            def safe_f(val):
                try:
                    if val is None: return None
                    f = float(val)
                    return f if not np.isnan(f) and not np.isinf(f) else None
                except: return None

            pe = safe_f(info.get('trailingPE', info.get('forwardPE')))
            pb = safe_f(info.get('priceToBook'))
            ps = safe_f(info.get('priceToSalesTrailing12Months'))
            yield_val = safe_f(info.get('dividendYield'))

            # --- Score (100 is undervalued) ---
            score_pts = []
            if pe: score_pts.append(100 if pe < 15 else (50 if pe < 25 else 0))
            if pb: score_pts.append(100 if pb < 2 else (50 if pb < 4 else 0))

            metrics = {
                "pe": pe,
                "pb": pb,
                "ps": ps,
                "yield": yield_val,
                "value_score": int(sum(score_pts)/len(score_pts)) if score_pts else None
            }
            return metrics

        except Exception as e:
            logger.error(f"[VALUE ERROR] {str(e)}")
            return {"value_score": None}

value_engine = ValueEngine()
