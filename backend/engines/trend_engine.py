import pandas as pd
import ta
from typing import Dict, Any
from core.logger import logger

class TrendEngine:
    """Trend Quality and Confirmation Engine (V4)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 20:
            return {"trend_score": None}

        try:
            close = history['Close']
            ema20 = ta.trend.ema_indicator(close, window=20)
            ema50 = ta.trend.ema_indicator(close, window=min(50, len(close)))

            last_price = float(close.iloc[-1])
            last_ema20 = float(ema20.iloc[-1])

            is_uptrend = last_price > last_ema20

            metrics = {
                "is_uptrend": is_uptrend,
                "trend_score": 100 if is_uptrend else 0
            }
            return metrics
        except Exception as e:
            logger.error(f"[TREND ERROR] {str(e)}")
            return {"trend_score": None}

trend_engine = TrendEngine()
