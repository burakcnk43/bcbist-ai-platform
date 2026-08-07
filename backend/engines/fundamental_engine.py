from typing import Dict, Any
import numpy as np
from ..core.logger import logger

class FundamentalEngine:
    """Institutional Grade Fundamental Analysis Engine with NaN-safe logic."""

    def calculate_metrics(self, info: Dict, income: Dict, balance: Dict, cash: Dict) -> Dict[str, Any]:
        """Calculates professional financial ratios with robust error handling."""
        metrics = {}
        try:
            def safe_float(val, default=0.0):
                try:
                    if val is None or (isinstance(val, float) and np.isnan(val)):
                        return default
                    return float(val)
                except (ValueError, TypeError):
                    return default

            # --- 1. Key Extraction ---
            pe = safe_float(info.get('trailingPE', info.get('forwardPE')))
            pb = safe_float(info.get('priceToBook'))
            ps = safe_float(info.get('priceToSalesTrailing12Months'))
            ev_ebitda = safe_float(info.get('enterpriseToEbitda'))

            roe = safe_float(info.get('returnOnEquity'))
            roa = safe_float(info.get('returnOnAssets'))
            roic = safe_float(info.get('returnOnCapital'))

            curr_ratio = safe_float(info.get('currentRatio'))
            quick_ratio = safe_float(info.get('quickRatio')) # Acid Test
            debt_eq = safe_float(info.get('debtToEquity'))

            rev_growth = safe_float(info.get('revenueGrowth'))
            eps_growth = safe_float(info.get('earningsGrowth', 0.05))

            metrics.update({
                'pe_ratio': pe, 'pb_ratio': pb, 'ps_ratio': ps, 'ev_ebitda': ev_ebitda,
                'roe': roe, 'roa': roa, 'roic': roic,
                'current_ratio': curr_ratio, 'quick_ratio': quick_ratio, 'debt_equity': debt_eq,
                'revenue_growth': rev_growth, 'eps_growth': eps_growth
            })

            # --- 2. Piotroski F-Score (9 points check proxy) ---
            f_score = 0
            # Profitability
            if safe_float(info.get('netIncomeToCommon')) > 0: f_score += 1
            if roa > 0: f_score += 1
            if safe_float(info.get('operatingCashflow')) > 0: f_score += 1
            if safe_float(info.get('operatingCashflow')) > safe_float(info.get('netIncomeToCommon')): f_score += 1
            # Health/Liquidity
            if debt_eq < 100: f_score += 1
            if curr_ratio > 1.2: f_score += 1
            if info.get('sharesOutstanding') == info.get('impliedSharesOutstanding'): f_score += 1 # Dilution check proxy

            metrics['piotroski_score'] = f_score

            # --- 3. Altman Z-Score Proxy ---
            # Using current ratio and roa as stability proxies
            metrics['altman_z'] = (1.2 * curr_ratio) + (3.3 * roa)

            # --- 4. Graham Intrinsic Value & Number ---
            eps = safe_float(info.get('trailingEps'))
            if eps > 0:
                growth_val = eps_growth * 100
                metrics['graham_value'] = (eps * (8.5 + 2 * growth_val) * 4.4) / 4.5
                metrics['graham_number'] = np.sqrt(22.5 * eps * safe_float(info.get('bookValue')))
            else:
                metrics['graham_value'] = 0
                metrics['graham_number'] = 0

            # --- 5. Fundamental Score Calculation ---
            score = 50
            if 0 < pe < 15: score += 10
            if roe > 0.18: score += 10
            if f_score >= 4: score += 15
            if rev_growth > 0.12: score += 10
            if debt_eq < 80: score += 5

            metrics['fundamental_score'] = int(min(max(score, 0), 100))
            return metrics

        except Exception as e:
            logger.error(f"[FUNDAMENTAL ENGINE ERROR] {str(e)}")
            return {"fundamental_score": 50}

fundamental_engine = FundamentalEngine()
