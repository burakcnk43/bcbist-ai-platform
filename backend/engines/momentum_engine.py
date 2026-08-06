import pandas as pd
import numpy as np
from typing import Dict, Any
from ..core.logger import logger

class MomentumEngine:
    """Professional Momentum Analysis (Relative Strength & Volatility-Adjusted Momentum)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or len(history) < 60:
            return {"momentum_score": 50}

        try:
            close = history['Close']

            # 1. Price Momentum (Short vs Long)
            mom_10 = (close.iloc[-1] / close.iloc[-10]) - 1
            mom_30 = (close.iloc[-1] / close.iloc[-30]) - 1
            mom_60 = (close.iloc[-1] / close.iloc[-60]) - 1

            # 2. Volume Momentum
            avg_vol_short = history['Volume'].tail(5).mean()
            avg_vol_long = history['Volume'].tail(20).mean()
            vol_mom = (avg_vol_short / avg_vol_long) if avg_vol_long > 0 else 1.0

            # 3. Momentum Quality (ADX as proxy for trend strength)
            # (Handled mostly in trend engine, but we add a bit here)

            score = 50
            if mom_10 > 0.05: score += 15
            if mom_30 > 0.10: score += 15
            if mom_60 > 0.20: score += 10
            if vol_mom > 1.2: score += 10

            # Penalize overbought momentum
            if mom_10 > 0.20: score -= 10

            metrics = {"momentum_score": max(0, min(score, 100))}
            logger.info(f"[MOMENTUM] Final Score: {metrics['momentum_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Momentum Engine: {str(e)}")
            return {"momentum_score": 50}

momentum_engine = MomentumEngine()
