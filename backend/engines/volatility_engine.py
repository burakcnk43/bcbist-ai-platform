import pandas as pd
import numpy as np
from typing import Dict, Any
from ..core.logger import logger

class VolatilityEngine:
    """Institutional Volatility Analysis Engine with safe standard deviation scaling."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Calculates volatility rank."""
        if history is None or history.empty or len(history) < 30:
            return {"volatility_score": 50}

        try:
            returns = history['Close'].pct_change().dropna()
            if returns.empty:
                return {"volatility_score": 50}

            std = float(returns.std())
            if np.isnan(std) or std == 0:
                return {"volatility_score": 50}

            # Scaled 0-100 where 100 is stable (low volatility)
            # Daily std of 0.05 (5%) is extremely high for BIST, mapping that to 0
            score = 100 - (std * 2000)

            metrics = {
                "daily_std": std,
                "volatility_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[VOLATILITY ERROR] {str(e)}")
            return {"volatility_score": 50}

volatility_engine = VolatilityEngine()
