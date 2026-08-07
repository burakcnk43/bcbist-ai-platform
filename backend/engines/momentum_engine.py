import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class MomentumEngine:
    """Relative Strength and Momentum Analysis Engine."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 200:
            return {"momentum_score": 50}

        try:
            close = history['Close']

            # --- Returns for different periods ---
            mom5 = (close.iloc[-1] / close.iloc[-5]) - 1
            mom10 = (close.iloc[-1] / close.iloc[-10]) - 1
            mom20 = (close.iloc[-1] / close.iloc[-20]) - 1
            mom50 = (close.iloc[-1] / close.iloc[-50]) - 1
            mom100 = (close.iloc[-1] / close.iloc[-100]) - 1
            mom200 = (close.iloc[-1] / close.iloc[-200]) - 1

            # --- Relative Strength (Simplified) ---
            # In a full app, this would be relative to XU100
            rs_score = mom20 * 0.4 + mom50 * 0.3 + mom200 * 0.3

            metrics = {
                "mom5": mom5,
                "mom10": mom10,
                "mom20": mom20,
                "mom50": mom50,
                "mom100": mom100,
                "mom200": mom200,
                "rs_score": rs_score
            }

            # --- Momentum Score (0-100) ---
            score = 50
            if mom10 > 0.05: score += 10
            if mom20 > 0.10: score += 15
            if mom200 > 0.20: score += 15
            if mom5 < -0.05: score -= 10 # Short term pullback penalty

            metrics['momentum_score'] = min(max(score, 0), 100)
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Momentum Engine: {str(e)}")
            return {"momentum_score": 50}

momentum_engine = MomentumEngine()
