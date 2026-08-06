import pandas as pd
import ta
from typing import Dict, Any
from ..core.logger import logger

class TrendEngine:
    """Professional Trend Analysis (EMA Alignment & ADX Confirmation)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or len(history) < 50:
            return {"trend_score": 50}

        try:
            close = history['Close']
            high = history['High']
            low = history['Low']

            ema_20 = ta.trend.ema_indicator(close, window=20).iloc[-1]
            ema_50 = ta.trend.ema_indicator(close, window=50).iloc[-1]
            ema_200 = ta.trend.ema_indicator(close, window=200).iloc[-1] if len(close) >= 200 else ema_50

            adx = ta.trend.ADXIndicator(high, low, close).adx().iloc[-1]

            # Score (0-100)
            score = 0

            # 1. EMA Alignment (Perfect order is 20 > 50 > 200)
            if ema_20 > ema_50: score += 30
            if ema_50 > ema_200: score += 30
            if close.iloc[-1] > ema_20: score += 10

            # 2. ADX Confirmation (Strength of trend)
            if adx > 25: score += 30
            elif adx < 15: score -= 20 # Sideways/Weak trend

            metrics = {"trend_score": max(0, min(score, 100))}
            logger.info(f"[TREND] Final Score: {metrics['trend_score']}")
            return metrics
        except Exception as e:
            logger.error(f"[ERROR] Trend Engine: {str(e)}")
            return {"trend_score": 50}

trend_engine = TrendEngine()
