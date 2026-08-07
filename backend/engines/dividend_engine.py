from typing import Dict, Any
from ..core.logger import logger

class DividendEngine:
    """Institutional Grade Dividend Analysis Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        """Analyzes yield, payout stability, and growth history."""
        try:
            yield_val = info.get('dividendYield', 0) or 0
            payout = info.get('payoutRatio', 0) or 0
            div_rate = info.get('dividendRate', 0) or 0
            five_yr_avg = info.get('fiveYearAvgDividendYield', 0) or 0

            # --- Dividend Score (0-100) ---
            score = 0

            # 1. Yield Quality (Max 50 pts)
            if yield_val > 0.08: score += 50
            elif yield_val > 0.05: score += 40
            elif yield_val > 0.03: score += 25

            # 2. Payout Sustainability (Max 30 pts)
            # Target range 20% - 70% is ideal for BIST companies
            if 0.15 < payout < 0.65: score += 30
            elif payout < 0.90: score += 15

            # 3. Growth & Stability (Max 20 pts)
            if yield_val > five_yr_avg: score += 10
            if div_rate > 0: score += 10

            metrics = {
                "dividend_yield": yield_val,
                "payout_ratio": payout,
                "dividend_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[DIVIDEND ENGINE ERROR] {str(e)}")
            return {"dividend_score": 0}

dividend_engine = DividendEngine()
