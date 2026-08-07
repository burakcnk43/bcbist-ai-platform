from typing import Dict, Any
from ..core.logger import logger

class ValueEngine:
    """Valuation and Margin of Safety Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            pe = info.get('trailingPE', 0)
            pb = info.get('priceToBook', 0)
            ps = info.get('priceToSalesTrailing12Months', 0)
            yield_val = info.get('dividendYield', 0) or 0

            # --- Discount Score ---
            # Targeting PE < 15, PB < 2 as baseline "value"
            score = 50
            if 0 < pe < 12: score += 20
            if 0 < pb < 1.5: score += 20
            if yield_val > 0.04: score += 10

            metrics = {
                "pe": pe,
                "pb": pb,
                "ps": ps,
                "yield": yield_val
            }

            metrics['value_score'] = min(max(score, 0), 100)
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Value Engine: {str(e)}")
            return {"value_score": 50}

value_engine = ValueEngine()
