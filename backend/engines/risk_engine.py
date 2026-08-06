import numpy as np
import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class RiskEngine:
    """Professional Risk Analysis Engine with VaR, CVaR and Sharpe/Sortino Ratios."""

    def calculate_metrics(self, history: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 60:
            return {"risk_score": 50}

        try:
            returns = history['Close'].pct_change().dropna()

            # Volatility Metrics
            ann_vol = returns.std() * np.sqrt(252)

            # Value at Risk (VaR) 95% Confidence
            var_95 = np.percentile(returns, 5)

            # Conditional VaR (CVaR) - Expected Shortfall
            cvar_95 = returns[returns <= var_95].mean()

            # Sharpe Ratio
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

            # Sortino Ratio (Downside deviation)
            negative_returns = returns[returns < 0]
            downside_std = negative_returns.std() * np.sqrt(252)
            sortino = (returns.mean() * 252) / downside_std if downside_std != 0 else 0

            # Max Drawdown
            rolling_max = history['Close'].cummax()
            drawdown = (history['Close'] - rolling_max) / rolling_max
            max_dd = drawdown.min()

            metrics = {
                "volatility": ann_vol,
                "var_95": var_95,
                "cvar_95": cvar_95,
                "sharpe": sharpe,
                "sortino": sortino,
                "max_drawdown": max_dd,
                "beta": info.get('beta', 1.0)
            }

            # Risk Score (0-100, 100 = Low Risk/Very Safe)
            score = 100
            if ann_vol > 0.45: score -= 30
            if max_dd < -0.35: score -= 30
            if metrics['beta'] > 1.6: score -= 20
            if sharpe < 0: score -= 20

            metrics['risk_score'] = max(0, score)
            logger.info(f"[RISK] Score: {metrics['risk_score']}")
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Risk Engine Detail: {str(e)}")
            return {"risk_score": 50}

risk_engine = RiskEngine()
