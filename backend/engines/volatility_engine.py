import pandas as pd
import numpy as np
from typing import Dict, Any
from ..core.logger import logger

class VolatilityEngine:
    """Volatility Analysis Engine (ATR Rank & Standard Deviation)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or len(history) < 20:
            return {"volatility_score": 50}
        try:
            returns = history['Close'].pct_change().dropna()
            std = returns.std()

            # Simple scoring: Low volatility is often preferred for "value" but high for "risk"
            # Here we scale 0-100 where higher is more stable (lower volatility)
            # Typical daily std for BIST is 0.02 - 0.04
            score = 100 - (std * 2000)

            metrics = {"volatility_score": max(0, min(score, 100))}
            logger.info(f"[VOLATILITY] Final Score: {metrics['volatility_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Volatility Engine: {str(e)}")
            return {"volatility_score": 50}

volatility_engine = VolatilityEngine()
