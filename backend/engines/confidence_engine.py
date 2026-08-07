from typing import Dict, Any
from ..core.logger import logger

class ConfidenceEngine:
    """Institutional Grade Signal Reliability and Data Integrity Engine."""

    def calculate_confidence(self, tech: Dict[str, Any], fund: Dict[str, Any], risk: Dict[str, Any],
                             trend: Dict[str, Any], info: Dict[str, Any]) -> int:
        """Determines reliability score (0-100) based on signal harmony and data quality."""
        try:
            score = 100

            # --- 1. Data Integrity & Freshness ---
            # Penalize if major indicators are missing or at default values
            if tech.get('technical_score', 50) == 50: score -= 15
            if fund.get('fundamental_score', 50) == 50: score -= 15

            # --- 2. Signal Discrepancy (Conflict Detection) ---
            # If Technical and Fundamental signals are opposing, confidence drops
            t_score = tech.get('technical_score', 50)
            f_score = fund.get('fundamental_score', 50)
            if abs(t_score - f_score) > 40:
                score -= 25
            elif abs(t_score - f_score) > 25:
                score -= 10

            # --- 3. Trend Consistency ---
            # If the current price is far from moving averages or trend is negative
            if trend.get('trend_score', 50) < 40:
                score -= 15

            # --- 4. Volatility Impact ---
            # Abnormal volatility decreases the reliability of fixed indicators
            vol = risk.get('volatility', 0.3)
            if vol > 0.60:
                score -= 20
            elif vol > 0.45:
                score -= 10

            # --- 5. Missing Financial Data Penalty ---
            # Check for empty statements in info or specific fundamental metrics
            if not info.get('trailingPE') and not info.get('forwardPE'):
                score -= 10
            if not info.get('returnOnEquity'):
                score -= 10

            final_score = int(min(max(score, 10), 100))
            return final_score

        except Exception as e:
            logger.error(f"[CONFIDENCE ENGINE ERROR] {str(e)}")
            return 50

confidence_engine = ConfidenceEngine()
