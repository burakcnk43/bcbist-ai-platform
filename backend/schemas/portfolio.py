from __future__ import annotations

from typing import Any

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


class PortfolioAnalyzeRequest(BaseModel):
    """Portfolio analysis request payload."""
    name: str = Field(default="My Portfolio")
    positions: list[PortfolioPosition] = Field(default_factory=list)


class PortfolioAnalysisResponse(BaseModel):
    """Portfolio analysis response payload."""
    current_value: float
    profit: float
    profit_pct: float
    portfolio_score: int
    sector_distribution: dict[str, float] = Field(default_factory=dict)
    risk_distribution: dict[str, float] = Field(default_factory=dict)
    diversification_score: int
    ai_comments: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class PortfolioRiskResponse(BaseModel):
    """Portfolio risk response payload."""
    portfolio_score: int
    risk_distribution: dict[str, float] = Field(default_factory=dict)
    ai_comments: list[str] = Field(default_factory=list)


class PortfolioRebalanceResponse(BaseModel):
    """Portfolio rebalance response payload."""
    portfolio_score: int
    suggested_allocations: dict[str, float] = Field(default_factory=dict)
    ai_comments: list[str] = Field(default_factory=list)


class PortfolioDiversificationResponse(BaseModel):
    """Portfolio diversification response payload."""
    diversification_score: int
    sector_distribution: dict[str, float] = Field(default_factory=dict)
    ai_comments: list[str] = Field(default_factory=list)
