import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.core.logger import logger

class MomentumEngine:
    """Relative Strength and Momentum Analysis Engine (V4)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 20:
            return {"momentum_score": None}

        try:
            close = history['Close']
            def get_mom(p):
                if len(close) > p:
                    return float((close.iloc[-1] / close.iloc[-(p+1)]) - 1)
                return None

            metrics = {
                "mom5": get_mom(5),
                "mom20": get_mom(20),
                "mom100": get_mom(100)
            }

            # Score
            score_pts = []
            if metrics["mom5"] is not None: score_pts.append(100 if metrics["mom5"] > 0 else 0)
            if metrics["mom20"] is not None: score_pts.append(100 if metrics["mom20"] > 0.05 else 0)

            if score_pts:
                metrics['momentum_score'] = int(sum(score_pts) / len(score_pts))
            else:
                metrics['momentum_score'] = None

            return metrics
        except Exception as e:
            logger.error(f"[MOMENTUM ERROR] {str(e)}")
            return {"momentum_score": None}

momentum_engine = MomentumEngine()
