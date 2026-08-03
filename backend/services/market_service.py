from __future__ import annotations

from typing import Any

from src.data.bist_universe import BIST100_TICKERS
from src.data.sources.financial_data import get_bist100_index
from src.data.sources.kap_client import KAPClient


class MarketService:
    """Provide market data helpers for the backend API."""

    def __init__(self) -> None:
        """Initialize dependencies for market services."""
        self._kap_client = KAPClient()

    async def get_bist100_universe(self) -> list[dict[str, Any]]:
        """Return a BIST 100 universe list, using the KAP client when possible."""
        try:
            async with self._kap_client as client:
                return await client.get_bist100_list()
        except Exception:
            return [
                {
                    "ticker": ticker,
                    "name": ticker,
                    "sector": "Genel",
                    "weight": 0.0,
                }
                for ticker in list(BIST100_TICKERS[:100])
            ]

    async def get_hot_stocks(self) -> list[dict[str, Any]]:
        """Return a lightweight hot-stocks payload for the API."""
        universe = await self.get_bist100_universe()
        return [
            {
                "ticker": item.get("ticker"),
                "name": item.get("name") or item.get("ticker"),
                "sector": item.get("sector") or "Genel",
            }
            for item in universe[:12]
        ]

    def get_bist100_index(self) -> dict[str, Any]:
        """Return the latest BIST 100 index snapshot."""
        return get_bist100_index()
