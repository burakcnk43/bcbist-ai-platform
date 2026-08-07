import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class LiquidityEngine:
    """Volume and Liquidity Risk Engine."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty:
            return {"liquidity_score": 50}

        try:
            volume = history['Volume']
            avg_volume_20 = volume.tail(20).mean()

            # --- Liquidity Score (0-100) ---
            # Thresholds for BIST liquidity (in TRY volume roughly)
            # Assuming volume in shares, we adjust for price in real app
            score = 0
            if avg_volume_20 > 5000000: score = 90
            elif avg_volume_20 > 1000000: score = 75
            elif avg_volume_20 > 500000: score = 50
            else: score = 30

            metrics = {
                "avg_vol_20": avg_volume_20,
                "liquidity_score": score
            }
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Liquidity Engine: {str(e)}")
            return {"liquidity_score": 50}

liquidity_engine = LiquidityEngine()
