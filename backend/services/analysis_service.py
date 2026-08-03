from __future__ import annotations

from typing import Any

from backend.services.stock_service import StockService
from backend.services.news_service import NewsService


class AnalysisService:
    """Expose reusable analysis helpers for the backend API."""

    def __init__(self) -> None:
        """Initialize dependencies for analysis services."""
        self.stock_service = StockService()
        self.news_service = NewsService()

    def analyze_symbol(self, symbol: str) -> dict[str, Any]:
        """Return the full stock analysis payload for the API."""
        return self.stock_service.analyze_stock(symbol)

    def get_analysis_news(self, symbol: str, limit: int = 8) -> list[dict[str, Any]]:
        """Return normalized analysis news items for the symbol."""
        return self.news_service.get_news(symbol, limit=limit)
