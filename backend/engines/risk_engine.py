import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.core.logger import logger

class RiskEngine:
    """Institutional Risk Analysis Engine with V4 Robustness."""

    def calculate_metrics(self, history: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Calculates advanced risk metrics safely."""
        if history is None or history.empty or len(history) < 10:
            return {"risk_score": None}

        try:
            returns = history['Close'].pct_change().dropna()
            if returns.empty:
                return {"risk_score": None}

            def safe_val(val):
                return float(val) if not np.isnan(val) and not np.isinf(val) else None

            # --- 1. Volatility ---
            daily_std = returns.std()
            ann_vol = daily_std * np.sqrt(252)

            # --- 2. Risk-Adjusted ---
            avg_ret = returns.mean() * 252
            sharpe = (avg_ret / ann_vol) if ann_vol > 0 else 0

            # --- 3. Drawdown ---
            roll_max = history['Close'].cummax()
            drawdown = (history['Close'] / roll_max) - 1.0
            max_dd = float(drawdown.min())

            beta = info.get('beta')
            if beta is not None:
                beta = float(beta) if not np.isnan(beta) else 1.0
            else:
                beta = 1.0

            metrics = {
                "volatility": safe_val(ann_vol),
                "sharpe": safe_val(sharpe),
                "max_drawdown": safe_val(max_dd),
                "beta": safe_val(beta)
            }

            # --- 4. Risk Score (100 is Safe) ---
            score = 100
            if ann_vol > 0.50: score -= 40
            elif ann_vol > 0.35: score -= 20

            if max_dd < -0.40: score -= 30
            if beta > 1.5: score -= 20

            metrics['risk_score'] = max(min(score, 100), 0)
            return metrics

        except Exception as e:
            logger.error(f"[RISK ENGINE ERROR] {str(e)}")
            return {"risk_score": None}

risk_engine = RiskEngine()
