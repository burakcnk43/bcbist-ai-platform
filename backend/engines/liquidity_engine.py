import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class LiquidityEngine:
    """Institutional Liquidity Risk and Turnover Engine."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Calculates liquidity score based on volume stability and depth."""
        if history is None or history.empty:
            return {"liquidity_score": 50}

        try:
            volume = history['Volume']
            close = history['Close']

            # TRY Volume (Value traded)
            try_vol = (volume * close).tail(20).mean()

            # Volume Stability (Std of volume)
            vol_std = volume.tail(20).std() / volume.tail(20).mean()

            # --- Liquidity Score (0-100) ---
            # Thresholds based on BIST daily value traded (TL)
            score = 0
            if try_vol > 500_000_000: score = 95    # Blue chip liquidity
            elif try_vol > 100_000_000: score = 85  # High liquidity
            elif try_vol > 20_000_000: score = 70   # Moderate liquidity
            elif try_vol > 5_000_000: score = 50    # Low liquidity
            else: score = 25                        # Illiquid

            # Penalty for erratic volume (Max 15 pts)
            if vol_std > 1.5: score -= 15

            metrics = {
                "daily_value_traded": float(try_vol),
                "liquidity_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[LIQUIDITY ENGINE ERROR] {str(e)}")
            return {"liquidity_score": 50}

liquidity_engine = LiquidityEngine()
