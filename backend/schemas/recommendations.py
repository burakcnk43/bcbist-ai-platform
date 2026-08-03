from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    symbol: str
    company: str
    ai_score: int
    technical_score: int
    fundamental_score: int
    risk_score: int
    recommendation_reason: str
    confidence: float


class RecommendationResponse(BaseModel):
    strategy: str
    count: int
    recommendations: list[RecommendationItem] = Field(default_factory=list)
