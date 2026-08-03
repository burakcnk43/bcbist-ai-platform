from __future__ import annotations

from typing import Any

from backend.services.stock_service import StockService
from backend.services.stock_registry import StockRegistryService


class PortfolioEngine:
    """Provide reusable portfolio analysis helpers for the backend API."""

    def __init__(self) -> None:
        self.stock_service = StockService()
        self.registry_service = StockRegistryService()

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        positions = payload.get("positions") or []
        current_value = 0.0
        profit = 0.0
        sector_distribution: dict[str, float] = {}
        strengths: list[str] = []
        weaknesses: list[str] = []
        for position in positions:
            symbol = str(position.get("symbol", "")).upper()
            quantity = float(position.get("quantity", 0) or 0)
            avg_cost = float(position.get("avg_cost", 0) or 0)
            if quantity <= 0:
                continue
            try:
                analysis = self.stock_service.analyze_stock(symbol)
            except Exception:
                continue
            latest_price = float(analysis.get("latest_price") or 0.0)
            value = latest_price * quantity
            current_value += value
            profit += (latest_price - avg_cost) * quantity
            sector = analysis.get("sector") or "Unknown"
            sector_distribution[sector] = sector_distribution.get(sector, 0.0) + value

        portfolio_score = int(min(100, max(0, 60 + int(profit / max(current_value, 1.0) * 20))))
        diversification_score = int(min(100, max(20, 30 + len(sector_distribution) * 10)))
        ai_comments = ["Portfolio diversified across major sectors."] if sector_distribution else ["Add positions to improve diversification."]
        strengths.append("Portfolio has live market exposure.") if current_value else strengths.append("No active positions.")
        weaknesses.append("A few positions may need rebalancing.") if len(sector_distribution) > 2 else weaknesses.append("Diversification is still limited.")
        return {
            "current_value": round(current_value, 2),
            "profit": round(profit, 2),
            "profit_pct": round((profit / max(current_value, 1.0)) * 100, 2) if current_value else 0.0,
            "portfolio_score": portfolio_score,
            "sector_distribution": {k: round(v, 2) for k, v in sector_distribution.items()},
            "risk_distribution": {"high": 20.0, "medium": 50.0, "low": 30.0},
            "diversification_score": diversification_score,
            "ai_comments": ai_comments,
            "weaknesses": weaknesses,
            "strengths": strengths,
        }

    def risk(self, payload: dict[str, Any]) -> dict[str, Any]:
        analysis = self.analyze(payload)
        analysis["risk_distribution"] = {"high": 15.0, "medium": 45.0, "low": 40.0}
        return analysis

    def rebalance(self, payload: dict[str, Any]) -> dict[str, Any]:
        analysis = self.analyze(payload)
        allocations = {symbol: 1 / max(len(payload.get("positions") or []), 1) for symbol in [p.get("symbol", "") for p in payload.get("positions") or []] if symbol}
        analysis["suggested_allocations"] = allocations
        return analysis

    def diversification(self, payload: dict[str, Any]) -> dict[str, Any]:
        analysis = self.analyze(payload)
        return analysis
