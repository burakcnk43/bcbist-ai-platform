from __future__ import annotations

from typing import Any

from src.data.bist_universe import BIST100_TICKERS, BIST_TICKERS


class StockRegistryService:
    """Reusable Borsa Istanbul stock registry for backend services."""

    def __init__(self) -> None:
        self._registry = self._build_registry()

    def _build_registry(self) -> list[dict[str, Any]]:
        symbols = list(BIST_TICKERS)
        registry: list[dict[str, Any]] = []
        for symbol in symbols:
            registry.append(
                {
                    "symbol": symbol,
                    "company_name": symbol,
                    "sector": "Genel",
                    "market": "Borsa İstanbul",
                    "index_membership": "BIST100" if symbol in BIST100_TICKERS else "Diğer",
                    "listing_status": "Listed",
                }
            )
        return registry

    def get_registry(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Return the registry as a list of stock metadata entries."""
        entries = list(self._registry)
        if limit is not None:
            return entries[:limit]
        return entries

    def get_symbol(self, symbol: str) -> dict[str, Any] | None:
        """Return the registry entry for a symbol, case-insensitive."""
        lookup = symbol.strip().upper().replace(".IS", "")
        for entry in self._registry:
            if entry["symbol"] == lookup:
                return entry
        return None

    def is_supported(self, symbol: str) -> bool:
        """Return True when the symbol is part of the Borsa Istanbul registry."""
        return self.get_symbol(symbol) is not None
