import numpy as np
import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class RiskEngine:
    """Institutional Risk Analysis Engine with Tail-Risk and Risk-Adjusted Returns."""

    def calculate_metrics(self, history: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Calculates advanced risk metrics."""
        if history is None or history.empty or len(history) < 100:
            return {"risk_score": 50}

        try:
            returns = history['Close'].pct_change().dropna()
            if returns.empty:
                return {"risk_score": 50}

            # --- Volatility & Returns ---
            ann_vol = returns.std() * np.sqrt(252)

            # --- Sharpe & Sortino ---
            avg_return = returns.mean() * 252
            sharpe = (avg_return / ann_vol) if ann_vol > 0 else 0

            neg_returns = returns[returns < 0]
            downside_std = neg_returns.std() * np.sqrt(252)
            sortino = (avg_return / downside_std) if downside_std > 0 else sharpe

            # --- Value at Risk (VaR) & CVaR ---
            var_95 = np.percentile(returns, 5)
            cvar_95 = returns[returns <= var_95].mean() if not returns[returns <= var_95].empty else var_95

            # --- Drawdown ---
            roll_max = history['Close'].cummax()
            drawdown = (history['Close'] / roll_max) - 1.0
            max_drawdown = float(drawdown.min())

            beta = float(info.get('beta', 1.0) or 1.0)

            metrics = {
                "volatility": float(ann_vol),
                "sharpe": float(sharpe),
                "sortino": float(sortino),
                "var_95": float(var_95),
                "cvar_95": float(cvar_95),
                "max_drawdown": max_drawdown,
                "beta": beta
            }

            # --- Risk Scoring (100 is Safest) ---
            score = 100
            if ann_vol > 0.45: score -= 30
            if max_drawdown < -0.35: score -= 30
            if beta > 1.6: score -= 20
            if sharpe < 0: score -= 20

            metrics['risk_score'] = max(min(score, 100), 0)
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Risk Engine: {str(e)}")
            return {"risk_score": 50}

risk_engine = RiskEngine()
