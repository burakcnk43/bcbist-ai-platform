from typing import Dict, Any
from ..core.logger import logger

class DividendEngine:
    """Professional Dividend Analysis Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            yield_val = info.get('dividendYield', 0) or 0
            payout_ratio = info.get('payoutRatio', 0) or 0
            five_year_avg = info.get('fiveYearAvgDividendYield', 0) or 0

            metrics = {
                "dividend_yield": yield_val,
                "payout_ratio": payout_ratio,
                "dividend_growth": info.get('dividendRate', 0) or 0
            }

            # Dividend Score (0-100)
            score = 0
            if yield_val > 0.05: score += 50
            elif yield_val > 0.02: score += 30

            # Safety: payout ratio between 10% and 70% is healthy
            if 0.1 < payout_ratio < 0.7: score += 30

            # Growth/History
            if yield_val > five_year_avg: score += 20

            metrics['dividend_score'] = min(score, 100)
            logger.info(f"[DIVIDEND] Score: {metrics['dividend_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Dividend Engine: {str(e)}")
            return {"dividend_score": 0}

dividend_engine = DividendEngine()
