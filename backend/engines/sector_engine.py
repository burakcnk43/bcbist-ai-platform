from typing import Dict, Any
from ..core.logger import logger

class SectorEngine:
    """Sector Comparative Performance Engine."""

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        """Compares stock with its sector (using proxies for sector averages)."""
        try:
            # In a production system, these averages would come from a DB or Real-time API
            sector_averages = {
                "Bankacılık": {"pe": 6, "roe": 0.35},
                "Holding": {"pe": 8, "roe": 0.25},
                "Ulaştırma": {"pe": 10, "roe": 0.20},
                "Otomotiv": {"pe": 12, "roe": 0.40},
                "Kimya": {"pe": 15, "roe": 0.30},
                "Enerji": {"pe": 18, "roe": 0.20}
            }

            sector = info.get('sector', 'Genel')
            avg = sector_averages.get(sector, {"pe": 15, "roe": 0.20})

            pe = info.get('trailingPE', 20)
            roe = info.get('returnOnEquity', 0.1)

            # --- Normalize Score (0-100) ---
            score = 50
            if pe < avg['pe']: score += 25
            if roe > avg['roe']: score += 25

            metrics = {
                "sector": sector,
                "sector_score": min(max(score, 0), 100)
            }
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Sector Engine: {str(e)}")
            return {"sector_score": 50}

sector_engine = SectorEngine()
