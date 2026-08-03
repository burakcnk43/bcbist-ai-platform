from __future__ import annotations

from pydantic import BaseModel, Field


class PortfolioPosition(BaseModel):
    """A single position inside a portfolio."""
    symbol: str = Field(..., min_length=1)
    quantity: float = Field(default=0.0)
    avg_cost: float = Field(default=0.0)


class PortfolioBase(BaseModel):
    """Portfolio request payload for the FastAPI route."""
    name: str = Field(default="My Portfolio")
    positions: list[PortfolioPosition] = Field(default_factory=list)
