import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.core.logger import logger

class LiquidityEngine:
    """Institutional Liquidity Risk Engine (V4)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty:
            return {"liquidity_score": None}

        try:
            volume = history['Volume']
            close = history['Close']

            # Daily Volume in TL (Approx)
            avg_volume_tl = (volume * close).tail(20).mean()

            score = 50
            if avg_volume_tl > 100_000_000: score = 95
            elif avg_volume_tl > 20_000_000: score = 80
            elif avg_volume_tl > 5_000_000: score = 60
            else: score = 30

            return {
                "avg_daily_volume_tl": float(avg_volume_tl) if not np.isnan(avg_volume_tl) else None,
                "liquidity_score": score
            }
        except Exception:
            return {"liquidity_score": None}

liquidity_engine = LiquidityEngine()
