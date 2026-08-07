import pandas as pd
import ta
from typing import Dict, Any
from ..core.logger import logger

class TrendEngine:
    """Trend Quality and Confirmation Engine."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 200:
            return {"trend_score": 50}

        try:
            close = history['Close']
            high = history['High']
            low = history['Low']

            # --- Trend Confirmation ---
            ema20 = ta.trend.ema_indicator(close, window=20).iloc[-1]
            ema50 = ta.trend.ema_indicator(close, window=50).iloc[-1]
            ema200 = ta.trend.ema_indicator(close, window=200).iloc[-1]

            is_uptrend = ema20 > ema50 > ema200

            # --- ADX Trend Strength ---
            adx = ta.trend.ADXIndicator(high, low, close).adx().iloc[-1]

            # --- SuperTrend (Basic) ---
            atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range().iloc[-1]
            upper_band = ((high.iloc[-1] + low.iloc[-1]) / 2) + (3 * atr)
            lower_band = ((high.iloc[-1] + low.iloc[-1]) / 2) - (3 * atr)

            metrics = {
                "is_uptrend": is_uptrend,
                "adx": adx,
                "supertrend_confirm": close.iloc[-1] > lower_band
            }

            # --- Trend Score (0-100) ---
            score = 50
            if is_uptrend: score += 20
            if adx > 25: score += 15
            if metrics['supertrend_confirm']: score += 15

            metrics['trend_score'] = min(max(score, 0), 100)
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Trend Engine: {str(e)}")
            return {"trend_score": 50}

trend_engine = TrendEngine()
