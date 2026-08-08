from typing import Dict, Any
import numpy as np
from core.logger import logger

class ConfidenceEngine:
    """Institutional Grade Data Integrity & Signal Harmony Engine (V4)."""

    def calculate_confidence(self, tech: Dict, fund: Dict, risk: Dict, trend: Dict, info: Dict) -> int:
        """Determines reliability score (0-100) based on data completeness (V4)."""
        try:
            score = 100

            # Check for missing entire engines
            if tech.get('technical_score') is None: score -= 25
            if fund.get('fundamental_score') is None: score -= 25
            if risk.get('risk_score') is None: score -= 15

            # Data density check
            if not info.get('trailingPE') and not info.get('forwardPE'): score -= 10
            if not info.get('revenueGrowth'): score -= 10

            # Volatility penalty
            vol = risk.get('volatility', 0.3)
            if vol and vol > 0.60: score -= 15

            return int(max(min(score, 100), 10))
        except Exception:
            return 50

confidence_engine = ConfidenceEngine()
