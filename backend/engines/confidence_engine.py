from typing import Dict, Any
from ..core.logger import logger

class ConfidenceEngine:
    """Professional Signal Reliability and Data Integrity Engine."""

    def calculate_confidence(self, tech: Dict[str, Any], fund: Dict[str, Any], risk: Dict[str, Any]) -> int:
        """Determines reliability score (0-100) based on signal harmony."""
        try:
            score = 100

            # --- 1. Data Availability Penalties ---
            # If indicators are at default values, penalize
            if tech.get('technical_score', 50) == 50: score -= 15
            if fund.get('fundamental_score', 50) == 50: score -= 15

            # --- 2. Signal Discrepancy (Conflict Detection) ---
            # Strong technicals with weak fundamentals decreases confidence
            t_score = tech.get('technical_score', 50)
            f_score = fund.get('fundamental_score', 50)

            discrepancy = abs(t_score - f_score)
            if discrepancy > 50:
                score -= 30
            elif discrepancy > 30:
                score -= 15

            # --- 3. Stability Checks ---
            # High volatility decreases confidence in the signal's persistence
            vol = risk.get('volatility', 0.3)
            if vol > 0.60:
                score -= 20
            elif vol > 0.40:
                score -= 10

            # --- 4. Liquidity Risk ---
            # Low liquidity makes indicators less reliable (manipulation/noise)
            # (Handled via risk metrics if available)

            final_score = int(min(max(score, 10), 100))
            return final_score

        except Exception as e:
            logger.error(f"[ERROR] Confidence Calculation: {str(e)}")
            return 50

confidence_engine = ConfidenceEngine()
