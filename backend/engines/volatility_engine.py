import pandas as pd
import numpy as np
from typing import Dict, Any
from ..core.logger import logger

class VolatilityEngine:
    """Institutional Volatility Rank and ATR Analysis Engine."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Calculates volatility metrics and stable-rank score."""
        if history is None or history.empty or len(history) < 30:
            return {"volatility_score": 50}

        try:
            returns = history['Close'].pct_change().dropna()
            if returns.empty:
                return {"volatility_score": 50}

            # 1. Standard Deviation (Daily & Annualized)
            daily_std = float(returns.std())
            ann_vol = daily_std * np.sqrt(252)

            # 2. ATR Percentage (Price normalized volatility)
            # (Close - Low) + (High - Close) proxy for range
            high = history['High']
            low = history['Low']
            close = history['Close']
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
            atr_pct = (tr.tail(20).mean() / close.iloc[-1])

            # --- Volatility Score (0-100) ---
            # 100 = Extremely Stable, 0 = Extremely Volatile
            # Benchmark: 2% daily std (~32% annual) is "normal" for BIST
            score = 100 - (daily_std * 2500)

            # Penalize parabolic spikes
            if atr_pct > 0.08: score -= 20

            metrics = {
                "ann_vol": float(ann_vol),
                "atr_pct": float(atr_pct),
                "volatility_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[VOLATILITY ENGINE ERROR] {str(e)}")
            return {"volatility_score": 50}

volatility_engine = VolatilityEngine()
