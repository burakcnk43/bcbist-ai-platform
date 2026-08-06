from typing import Dict, Any
from ..core.logger import logger

class ConfidenceEngine:
    """Professional Data Confidence Engine (Measures reliability of signals)."""

    def calculate(self, tech: Dict, fund: Dict, risk: Dict) -> int:
        try:
            score = 100

            # 1. Data Integrity Check
            if not tech or tech.get('technical_score') is None: score -= 25
            if not fund or fund.get('fundamental_score') is None: score -= 25

            # 2. Signal Discrepancy (e.g. strong tech but terrible fund decreases confidence)
            t_score = tech.get('technical_score', 50)
            f_score = fund.get('fundamental_score', 50)
            diff = abs(t_score - f_score)
            if diff > 50: score -= 20 # High conflict signal

            # 3. Risk Dampening
            if risk.get('volatility', 0) > 0.60: score -= 20

            final_score = max(10, score)
            logger.info(f"[CONFIDENCE] Final Score: {final_score}")
            return int(final_score)
        except Exception as e:
            logger.error(f"[ERROR] Confidence Engine: {str(e)}")
            return 50

confidence_engine = ConfidenceEngine()
