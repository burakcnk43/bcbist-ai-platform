from __future__ import annotations

from typing import Any


class PortfolioService:
    """Provide lightweight portfolio state storage for the backend API."""

    def __init__(self) -> None:
        """Initialize dependencies for portfolio services."""
        self._portfolio: dict[str, Any] | None = None

    def upsert_portfolio(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Store a portfolio payload and return a normalized version."""
        positions = payload.get("positions") or []
        normalized_positions = [
            {
                "symbol": str(position.get("symbol", "")).upper(),
                "quantity": float(position.get("quantity", 0) or 0),
                "avg_cost": float(position.get("avg_cost", 0) or 0),
            }
            for position in positions
        ]
        self._portfolio = {
            "name": payload.get("name") or "My Portfolio",
            "positions": normalized_positions,
        }
        return self._portfolio

    def get_portfolio_summary(self) -> dict[str, Any]:
        """Return the latest portfolio summary."""
        if self._portfolio is None:
            return {"name": "My Portfolio", "position_count": 0, "positions": []}
        return {
            "name": self._portfolio["name"],
            "position_count": len(self._portfolio.get("positions", [])),
            "positions": self._portfolio.get("positions", []),
        }
