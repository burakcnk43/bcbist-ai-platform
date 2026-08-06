import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class LiquidityEngine:
    """Liquidity Analysis Engine (Volume Rank & Turnover)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or len(history) < 10:
            return {"liquidity_score": 50}
        try:
            avg_vol = history['Volume'].tail(10).mean()
            # BIST Volume check (approximate thresholds)
            score = 0
            if avg_vol > 5000000: score = 90
            elif avg_vol > 1000000: score = 75
            elif avg_vol > 250000: score = 50
            else: score = 30

            metrics = {"liquidity_score": score}
            logger.info(f"[LIQUIDITY] Final Score: {score}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Liquidity Engine: {str(e)}")
            return {"liquidity_score": 50}

liquidity_engine = LiquidityEngine()
