from typing import Dict, Any
from ..core.logger import logger

class SectorEngine:
    """Sector Analysis Engine (Dynamic comparison targets)."""

    def __init__(self):
        # Estimated BIST Sector Medians (In real app, update from DB)
        self.sector_averages = {
            "Financial Services": {"pe": 8, "roe": 0.30},
            "Transportation": {"pe": 10, "roe": 0.25},
            "Defense": {"pe": 25, "roe": 0.20},
            "Steel": {"pe": 12, "roe": 0.15},
            "Automotive": {"pe": 15, "roe": 0.35},
            "Energy": {"pe": 20, "roe": 0.18},
            "Technology": {"pe": 35, "roe": 0.20}
        }

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        try:
            sector = info.get('sector', 'Unknown')
            pe = info.get('trailingPE', 0) or 20
            roe = info.get('returnOnEquity', 0) or 0.1

            target = self.sector_averages.get(sector, {"pe": 15, "roe": 0.15})

            score = 50
            if pe < target["pe"]: score += 25
            if roe > target["roe"]: score += 25

            logger.info(f"[SECTOR] Final Score: {score}")
            return {"sector_score": score}
        except Exception as e:
            logger.error(f"[ERROR] Sector Engine: {str(e)}")
            return {"sector_score": 50}

sector_engine = SectorEngine()
