from pydantic import BaseModel, Field
from typing import List

class RecommendationItem(BaseModel):
    symbol: str
    company: str
    ai_score: int
    technical_score: int
    fundamental_score: int
    risk_score: int
    recommendation_reason: str
    confidence: int

class RecommendationResponse(BaseModel):
    strategy: str
    count: int
    recommendations: List[RecommendationItem]
