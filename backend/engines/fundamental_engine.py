from typing import Dict, Any
import numpy as np
from core.logger import logger

class FundamentalEngine:
    """Institutional Grade Fundamental Analysis Engine with NaN-safe logic (V4)."""

    def calculate_metrics(self, info: Dict, income: Dict, balance: Dict, cash: Dict) -> Dict[str, Any]:
        """Calculates professional financial ratios with absolute crash protection."""
        metrics = {}
        try:
            def safe_f(val, default=None):
                try:
                    if val is None: return default
                    f_val = float(val)
                    return f_val if not np.isnan(f_val) and not np.isinf(f_val) else default
                except (ValueError, TypeError):
                    return default

            # --- 1. Key Extraction ---
            metrics['pe_ratio'] = safe_f(info.get('trailingPE', info.get('forwardPE')))
            metrics['pb_ratio'] = safe_f(info.get('priceToBook'))
            metrics['ps_ratio'] = safe_f(info.get('priceToSalesTrailing12Months'))
            metrics['ev_ebitda'] = safe_f(info.get('enterpriseToEbitda'))

            metrics['roe'] = safe_f(info.get('returnOnEquity'))
            metrics['roa'] = safe_f(info.get('returnOnAssets'))
            metrics['roic'] = safe_f(info.get('returnOnCapital'))

            metrics['current_ratio'] = safe_f(info.get('currentRatio'))
            metrics['quick_ratio'] = safe_f(info.get('quickRatio'))
            metrics['debt_equity'] = safe_f(info.get('debtToEquity'))

            metrics['revenue_growth'] = safe_f(info.get('revenueGrowth'))
            metrics['eps_growth'] = safe_f(info.get('earningsGrowth'))

            # --- 2. Piotroski F-Score Proxy ---
            f_score = 0
            found_f = 0
            if safe_f(info.get('netIncomeToCommon')) is not None:
                if safe_f(info.get('netIncomeToCommon')) > 0: f_score += 1
                found_f += 1
            if metrics['roa'] is not None:
                if metrics['roa'] > 0: f_score += 1
                found_f += 1
            if safe_f(info.get('operatingCashflow')) is not None:
                if safe_f(info.get('operatingCashflow')) > 0: f_score += 1
                found_f += 1

            metrics['piotroski_score'] = f_score if found_f > 0 else None

            # --- 3. Graham Value ---
            eps = safe_f(info.get('trailingEps'))
            book = safe_f(info.get('bookValue'))
            if eps and eps > 0 and book and book > 0:
                metrics['graham_number'] = float(np.sqrt(22.5 * eps * book))
            else:
                metrics['graham_number'] = None

            # --- 4. Fundamental Score Calculation ---
            score_parts = []
            if metrics['pe_ratio']:
                score_parts.append(100 if metrics['pe_ratio'] < 20 else 0)
            if metrics['roe']:
                score_parts.append(100 if metrics['roe'] > 0.15 else 0)
            if metrics['debt_equity']:
                score_parts.append(100 if metrics['debt_equity'] < 100 else 0)

            if score_parts:
                metrics['fundamental_score'] = int(sum(score_parts) / len(score_parts))
            else:
                metrics['fundamental_score'] = None

            return metrics

        except Exception as e:
            logger.error(f"[FUNDAMENTAL ENGINE ERROR] {str(e)}")
            return {"fundamental_score": None}

fundamental_engine = FundamentalEngine()
