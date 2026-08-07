from typing import Dict, Any
from ..core.logger import logger

class SectorEngine:
    """Institutional Sector Comparative Analysis Engine."""

    def __init__(self):
        # Updated Sector Median Proxies (PE, ROE targets)
        self.sector_benchmarks = {
            "Bankacılık": {"pe": 6.5, "roe": 0.35},
            "Holding": {"pe": 8.0, "roe": 0.25},
            "Ulaştırma": {"pe": 12.0, "roe": 0.22},
            "Otomotiv": {"pe": 14.0, "roe": 0.40},
            "Kimya": {"pe": 18.0, "roe": 0.30},
            "Enerji": {"pe": 20.0, "roe": 0.18},
            "Gıda ve İçecek": {"pe": 18.0, "roe": 0.25},
            "Perakende": {"pe": 22.0, "roe": 0.30},
            "Teknoloji": {"pe": 35.0, "roe": 0.20},
            "Metal Ana": {"pe": 10.0, "roe": 0.15},
            "Çimento": {"pe": 15.0, "roe": 0.25},
            "Sigorta": {"pe": 7.0, "roe": 0.45},
            "Gayrimenkul": {"pe": 9.0, "roe": 0.20}
        }

    def calculate_metrics(self, info: Dict) -> Dict[str, Any]:
        """Normalizes stock metrics relative to its sector median."""
        try:
            sector = info.get('sector', 'Genel')
            bench = self.sector_benchmarks.get(sector, {"pe": 15.0, "roe": 0.20})

            pe = info.get('trailingPE', info.get('forwardPE', 25.0)) or 25.0
            roe = info.get('returnOnEquity', 0.1) or 0.1

            # --- Sector Score (0-100) ---
            score = 50

            # PE Comparison (Lower than benchmark is good)
            if pe < bench['pe']:
                diff_pct = (bench['pe'] - pe) / bench['pe']
                score += min(diff_pct * 25, 25)
            else:
                score -= 10

            # ROE Comparison (Higher than benchmark is good)
            if roe > bench['roe']:
                diff_pct = (roe - bench['roe']) / bench['roe']
                score += min(diff_pct * 25, 25)
            else:
                score -= 10

            metrics = {
                "sector": sector,
                "sector_score": int(min(max(score, 0), 100))
            }
            return metrics

        except Exception as e:
            logger.error(f"[SECTOR ENGINE ERROR] {str(e)}")
            return {"sector_score": 50}

sector_engine = SectorEngine()
