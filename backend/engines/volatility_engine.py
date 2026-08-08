import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.core.logger import logger

class VolatilityEngine:
    """Institutional Volatility Rank Engine (V4)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 10:
            return {"volatility_score": None}

        try:
            returns = history['Close'].pct_change().dropna()
            if returns.empty: return {"volatility_score": None}

            daily_std = float(returns.std())
            # 100 is stable, 0 is volatile. BIST avg is ~0.02
            score = 100 - (daily_std * 2000)

            return {
                "daily_std": daily_std,
                "volatility_score": int(max(min(score, 100), 0))
            }
        except Exception:
            return {"volatility_score": None}

volatility_engine = VolatilityEngine()
