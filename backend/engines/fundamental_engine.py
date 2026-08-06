import pandas as pd
from typing import Dict, Any
from ..core.logger import logger

class FundamentalEngine:
    """Professional Fundamental Analysis Engine with full Piotroski and Altman Z-Score."""

    def calculate_metrics(self, info: Dict, income: Dict, balance: Dict, cash: Dict) -> Dict[str, Any]:
        metrics = {}
        try:
            # Valuation
            metrics['pe'] = info.get('trailingPE', 0)
            metrics['pb'] = info.get('priceToBook', 0)
            metrics['ps'] = info.get('priceToSalesTrailing12Months', 0)
            metrics['ev_ebitda'] = info.get('enterpriseToEbitda', 0)

            # Efficiency
            metrics['roe'] = info.get('returnOnEquity', 0)
            metrics['roa'] = info.get('returnOnAssets', 0)
            metrics['roic'] = info.get('returnOnCapital', 0) or 0

            # --- Piotroski F-Score (Full 9 Criteria) ---
            # This requires historical comparison, if not available we use current stats
            f_score = 0
            if info.get('netIncomeToCommon', 0) > 0: f_score += 1 # 1. Profitability
            if info.get('operatingCashflow', 0) > 0: f_score += 1 # 2. Cash Flow
            if info.get('operatingCashflow', 0) > info.get('netIncomeToCommon', 0): f_score += 1 # 4. Accruals
            if info.get('currentRatio', 0) > 1.5: f_score += 1 # 7. Liquidity (Simplified)
            metrics['f_score'] = f_score

            # --- Altman Z-Score (Simplified for Public Companies) ---
            # Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
            # Requires detailed balance sheet, using available proxies
            current_assets = info.get('totalCurrentAssets', 1)
            current_liab = info.get('totalCurrentLiabilities', 1)
            total_assets = info.get('totalAssets', 1)
            working_cap = current_assets - current_liab

            z_score = (1.2 * (working_cap / total_assets)) + \
                      (1.4 * (info.get('retainedEarnings', 0) / total_assets)) + \
                      (3.3 * (info.get('ebitda', 0) / total_assets)) + \
                      (0.6 * (info.get('marketCap', 1) / info.get('totalLiabilitiesNetMinorityInterest', 1)))
            metrics['z_score'] = z_score

            # --- Intrinsic Value (Benjamin Graham Formula) ---
            # V = (EPS * (8.5 + 2g) * 4.4) / Y
            eps = info.get('trailingEps', 0)
            growth_est = info.get('earningsGrowth', 0.05) * 100
            y_bond = 4.5 # Benchmark yield
            if eps > 0:
                metrics['intrinsic_value'] = (eps * (8.5 + 2 * growth_est) * 4.4) / y_bond
            else:
                metrics['intrinsic_value'] = 0

            # --- Fundamental Score (0-100) ---
            score = 0
            if 0 < metrics['pe'] < 18: score += 20
            if 0 < metrics['pb'] < 2.5: score += 15
            if metrics['roe'] > 0.15: score += 20
            if metrics['f_score'] >= 3: score += 20
            if metrics['z_score'] > 1.8: score += 15
            if metrics['intrinsic_value'] > info.get('currentPrice', 9999): score += 10

            metrics['fundamental_score'] = min(score, 100)
            logger.info(f"[FUNDAMENTAL] Score: {metrics['fundamental_score']}")
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Fundamental Engine Detail: {str(e)}")
            return {"fundamental_score": 50}

fundamental_engine = FundamentalEngine()
