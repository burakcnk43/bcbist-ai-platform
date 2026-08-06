from typing import Dict, Any
from ..core.logger import logger

class ValueEngine:
    """Professional Value Analysis Engine (P/E, P/B relative to benchmarks)."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            pe = info.get('trailingPE', 0) or 0
            pb = info.get('priceToBook', 0) or 0
            ps = info.get('priceToSalesTrailing12Months', 0) or 0

            # Value Score (0-100)
            score = 0

            # P/E Scoring (Max 40 pts) - Target BIST median approx 12-15
            if 0 < pe < 12: score += 40
            elif 12 <= pe < 20: score += 25

            # P/B Scoring (Max 30 pts)
            if 0 < pb < 1.5: score += 30
            elif 1.5 <= pb < 3: score += 15

            # P/S Scoring (Max 30 pts)
            if 0 < ps < 1.0: score += 30
            elif 1.0 <= ps < 2.5: score += 15

            metrics = {
                "pe_ratio": pe,
                "pb_ratio": pb,
                "value_score": min(score, 100)
            }
            logger.info(f"[VALUE] Final Score: {metrics['value_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Value Engine: {str(e)}")
            return {"value_score": 50}

value_engine = ValueEngine()
