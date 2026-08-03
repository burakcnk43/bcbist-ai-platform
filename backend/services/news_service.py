from __future__ import annotations

from typing import Any

from src.data.news import get_news


class NewsService:
    """Provide simple market-news data for the backend API."""

    def __init__(self) -> None:
        """Initialize dependencies for news services."""
        pass

    def get_news(self, symbol: str, limit: int = 8) -> list[dict[str, Any]]:
        """Fetch and normalize news items for a given symbol."""
        items = get_news(symbol, limit=limit)
        return [
            {
                "title": item.get("title") or "Başlıksız içerik",
                "provider": "Google News",
                "url": item.get("link"),
            }
            for item in items
        ]
