from __future__ import annotations

from typing import Any

from backend.services.stock_service import StockService
from backend.services.stock_registry import StockRegistryService


class RecommendationService:
    """Create ranked stock recommendations by reusing the existing analysis service."""

    def __init__(self) -> None:
        self.stock_service = StockService()
        self.registry_service = StockRegistryService()

    def get_recommendations(self, strategy: str, limit: int = 10) -> list[dict[str, Any]]:
        """Return ranked recommendations for the requested strategy."""
        symbols = [entry["symbol"] for entry in self.registry_service.get_registry(limit=max(limit, 20))]
        ranked: list[dict[str, Any]] = []
        for symbol in symbols:
            try:
                payload = self.stock_service.analyze_stock(symbol)
            except Exception:
                continue
            score = payload.get("conclusion", {}).get("score") or 0
            technical = payload.get("technical", {})
            financial = payload.get("financial", {})
            valuation = payload.get("valuation", {})
            risk_metrics = payload.get("analysis", {}).get("risk_metrics", {})
            recommendation_reason = self._build_reason(symbol, payload)
            ranked.append(
                {
                    "symbol": symbol,
                    "company": payload.get("company_name") or symbol,
                    "ai_score": score,
                    "technical_score": int(round((technical.get("rsi") or 0) / 2)) if technical.get("rsi") is not None else 0,
                    "fundamental_score": int(round((financial.get("net_income") or 0) / 1000000)) if financial.get("net_income") is not None else 0,
                    "risk_score": 100 - int(round((risk_metrics.get("annualized_volatility") or 0) / 2)) if risk_metrics.get("annualized_volatility") is not None else 50,
                    "recommendation_reason": recommendation_reason,
                    "confidence": self._confidence_for_strategy(strategy, payload),
                }
            )

        ranked.sort(key=lambda item: item["ai_score"], reverse=True)
        return ranked[:limit]

    def _build_reason(self, symbol: str, payload: dict[str, Any]) -> str:
        technical = payload.get("technical", {})
        valuation = payload.get("valuation", {})
        analysis = payload.get("analysis", {})
        graham = valuation.get("graham", {}) or {}
        summary = analysis.get("ai_summary", {}).get("summary") or "Balanced outlook"
        return f"{symbol}: {summary} Graham={graham.get('graham_recommendation', 'Belirsiz')}"

    def _confidence_for_strategy(self, strategy: str, payload: dict[str, Any]) -> float:
        base = float(payload.get("conclusion", {}).get("score") or 0)
        if strategy in {"value", "dividend"}:
            return round(min(100.0, base + 5.0), 1)
        if strategy in {"high-growth", "high-risk"}:
            return round(min(100.0, base + 2.0), 1)
        return round(min(100.0, base), 1)
