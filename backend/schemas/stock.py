from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class StockRegistryEntrySchema(BaseModel):
    """Metadata payload for a Borsa Istanbul company."""
    symbol: str
    company_name: str
    sector: Optional[str] = None
    sub_sector: Optional[str] = None
    market: Optional[str] = None
    market_segment: Optional[str] = None
    index_memberships: list[str] = Field(default_factory=list)
    listing_status: Optional[str] = None
    listing_date: Optional[str] = None


class StockRegistryResponse(BaseModel):
    """Collection response for the stock registry."""
    count: int
    stocks: list[StockRegistryEntrySchema] = Field(default_factory=list)


class StockAnalysisRequest(BaseModel):
    """Request payload for single-stock analysis."""
    symbol: str


class TechnicalSummarySchema(BaseModel):
    """Technical metrics returned for a single stock."""
    rsi: Optional[float] = None
    macd: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    atr: Optional[float] = None
    support: Optional[float] = None
    resistance: Optional[float] = None
    trend: Optional[str] = None


class VolumeSummarySchema(BaseModel):
    """Volume metrics returned for a single stock."""
    today_volume: Optional[float] = None
    average_volume: Optional[float] = None
    relative_volume: Optional[float] = None


class FinancialSummarySchema(BaseModel):
    """Financial metrics returned for a single stock."""
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None
    equity: Optional[float] = None
    debt: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None


class ValuationSummarySchema(BaseModel):
    """Valuation metrics returned for a single stock."""
    pe: Optional[float] = None
    pb: Optional[float] = None
    ev_ebitda: Optional[float] = None
    graham: Optional[dict[str, Any]] = None


class NewsItemSchema(BaseModel):
    """News item returned for a single stock."""
    title: str
    provider: str
    url: Optional[str] = None


class ConclusionSchema(BaseModel):
    """Conclusion summary for the analysis result."""
    score: Optional[int] = None
    reasons: list[str] = Field(default_factory=list)


class PiotroskiSchema(BaseModel):
    """Compact Piotroski F-score payload."""
    score: int
    conditions: list[str] = Field(default_factory=list)


class AltmanZSchema(BaseModel):
    """Compact Altman Z payload."""
    score: float
    label: str
    components: dict[str, Any] = Field(default_factory=dict)


class PeterLynchSchema(BaseModel):
    """Peter Lynch-style valuation view."""
    estimated_value: Optional[float] = None
    method: str


class TrendAnalysisSchema(BaseModel):
    """Trend-focused analysis slice."""
    trend: Optional[str] = None
    rsi: Optional[float] = None
    momentum_20d: Optional[float] = None


class VolumeAnalysisSchema(BaseModel):
    """Volume-focused analysis slice."""
    today_volume: Optional[float] = None
    average_volume: Optional[float] = None
    relative_volume: Optional[float] = None


class SupportResistanceSchema(BaseModel):
    """Support and resistance view."""
    support: Optional[float] = None
    resistance: Optional[float] = None


class RiskMetricsSchema(BaseModel):
    """Risk metrics for the analysis payload."""
    volatility_label: Optional[str] = None
    annualized_volatility: Optional[float] = None
    price_to_earnings: Optional[float] = None
    price_to_book: Optional[float] = None
    latest_price: Optional[float] = None


class AiSummarySchema(BaseModel):
    """AI-style summary payload."""
    summary: str
    trend: Optional[str] = None
    valuation_note: Optional[str] = None


class OverallScoreSchema(BaseModel):
    """Final score summary."""
    score: int
    band: str


class AnalysisSectionSchema(BaseModel):
    """Standardized collection of additional analysis sections."""
    piotroski: PiotroskiSchema
    altman_z: AltmanZSchema
    peter_lynch: PeterLynchSchema
    trend_analysis: TrendAnalysisSchema
    volume_analysis: VolumeAnalysisSchema
    support_resistance: SupportResistanceSchema
    risk_metrics: RiskMetricsSchema
    ai_summary: AiSummarySchema
    overall_score: OverallScoreSchema


class StockAnalysisResponse(BaseModel):
    """Response payload for single-stock analysis."""
    ticker: str
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    live_price: Optional[float] = None
    latest_price: Optional[float] = None
    previous_close: Optional[float] = None
    daily_change_pct: Optional[float] = None
    weekly_change_pct: Optional[float] = None
    monthly_change_pct: Optional[float] = None
    yearly_change_pct: Optional[float] = None
    technical: TechnicalSummarySchema
    technical_explanations: list[str] = Field(default_factory=list)
    volume: VolumeSummarySchema
    financial: FinancialSummarySchema
    fundamental: dict[str, Any] = Field(default_factory=dict)
    valuation: ValuationSummarySchema
    analysis: AnalysisSectionSchema
    news: list[NewsItemSchema] = Field(default_factory=list)
    conclusion: ConclusionSchema
