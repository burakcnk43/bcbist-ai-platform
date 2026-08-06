# src/domain/services/confidence_engine.py
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from src.domain.services.graham_valuation import GrahamValuationService
from src.domain.services.ratio_analyzer import RatioAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceScore:
    """0-100 Güven Skoru Modeli"""
    ticker: str
    total_score: float
    breakdown: Dict[str, float]
    stars: Dict[str, int]
    short_term_rating: int
    long_term_rating: int
    strengths: List[str]
    risks: List[str]
    commentary: str
    timestamp: str


class ConfidenceEngine:
    """
    Advanced Multi-Factor Scoring Engine.
    
    Weights vary by strategy to ensure professional-grade recommendations.
    """
    
    STRATEGY_WEIGHTS = {
        "daily": {
            "technical": 0.50, # Momentum, RSI, Volume
            "financial": 0.30, # Basics
            "risk": 0.20
        },
        "weekly": {
            "technical": 0.40,
            "financial": 0.40,
            "risk": 0.20
        },
        "medium-term": {
            "technical": 0.30,
            "financial": 0.50, # Growth, ROE
            "risk": 0.20
        },
        "long-term": {
            "technical": 0.20, # Only major trends (EMA200)
            "financial": 0.60, # Solvency, Profitability, Growth
            "risk": 0.20
        }
    }
    
    def __init__(self):
        self.graham = GrahamValuationService()
        self.ratios = RatioAnalyzer()
    
    def analyze(
        self,
        ticker: str,
        current_price: float,
        donen_varliklar: float,
        kisa_vadeli_yukumlulukler: float,
        uzun_vadeli_yukumlulukler: float,
        oz_sermaye: float,
        net_kar: float,
        hisse_sayisi: int,
        isletme_nakit_akisi: float,
        sector: str = "Genel",
        rsi: float = 50,
        trend: str = "neutral",
        strategy: str = "daily",
        technical_summary: Any = None # TechnicalSummary object
    ) -> ConfidenceScore:
        """Full multi-factor confidence scoring aligned with specific strategies."""

        weights = self.STRATEGY_WEIGHTS.get(strategy, self.STRATEGY_WEIGHTS["daily"])
        
        breakdown = {}
        stars = {}
        strengths = []
        risks = []

        # 1. TECHNICAL SCORING (Max 100 base)
        tech_base = self._score_technical_advanced(technical_summary, strategy)
        breakdown["Teknik"] = tech_base * weights["technical"]
        
        # 2. FINANCIAL SCORING (Max 100 base)
        fin_base = self._score_financial_advanced(
            oz_sermaye, isletme_nakit_akisi, net_kar,
            donen_varliklar, kisa_vadeli_yukumlulukler,
            strategy
        )
        breakdown["Finansal"] = fin_base * weights["financial"]
        
        # 3. VALUATION & RISK (Max 100 base)
        risk_base = self._score_risk_advanced(
            ticker, current_price, donen_varliklar,
            kisa_vadeli_yukumlulukler, uzun_vadeli_yukumlulukler,
            hisse_sayisi, net_kar, oz_sermaye, technical_summary
        )
        breakdown["Risk/Değerleme"] = risk_base * weights["risk"]
        
        # TOTAL AI SCORE
        total_score = sum(breakdown.values())
        total_score = max(0.0, min(100.0, total_score))
        
        # Commentary & Metadata
        if oz_sermaye > 0: strengths.append("Güçlü Özsermaye")
        else: risks.append("Negatif Özsermaye")
        
        if isletme_nakit_akisi > 0: strengths.append("Pozitif Nakit Akışı")
        else: risks.append("Nakit Akışı Zayıf")

        short_term = 3 if trend in ["Boğa", "Güçlü Boğa"] else 2 if "Ayı" not in trend else 1
        long_term = 4 if total_score > 70 else 3 if total_score > 45 else 2
        
        return ConfidenceScore(
            ticker=ticker,
            total_score=round(total_score, 2),
            breakdown=breakdown,
            stars={"Teknik": int(tech_base/10), "Finansal": int(fin_base/10), "Risk": int(risk_base/10)},
            short_term_rating=short_term,
            long_term_rating=long_term,
            strengths=strengths,
            risks=risks,
            commentary=self._generate_commentary(ticker, total_score, strengths, risks, sector, strategy),
            timestamp=datetime.now().isoformat()
        )

    def _score_technical_advanced(self, summary: Any, strategy: str) -> float:
        """Evaluate ~10 technical factors."""
        if not summary: return 50.0
        score = 0
        
        # Trend (High impact)
        if "Boğa" in summary.trend: score += 30
        if "Güçlü Boğa" in summary.trend: score += 10
        
        # RSI
        if summary.rsi:
            if 45 <= summary.rsi <= 65: score += 20 # Ideal buy zone
            elif summary.rsi < 30: score += 15 # Oversold rebound
            elif summary.rsi > 75: score -= 10 # Overbought risk

        # Moving Averages
        if summary.sma_200 and summary.ema_50:
            if summary.ema_50 > summary.sma_200: score += 15 # Golden Cross proxy

        # Momentum & Volume
        if (summary.volume_ratio or 0) > 1.5: score += 15
        if (summary.momentum_20d or 0) > 5: score += 10
        
        # Volatility (Bollinger)
        if summary.bollinger_upper and summary.bollinger_lower:
            # Check if price is near bottom or top
            pass # Simplified for now

        return float(max(0, min(100, score)))

    def _score_financial_advanced(self, equity, cfo, net_income, cur_assets, cur_liab, strategy) -> float:
        """Evaluate core financial health."""
        score = 0
        if equity > 0: score += 30
        if cfo > 0: score += 20
        if net_income > 0: score += 20
        
        # Liquidity
        if cur_liab > 0:
            current_ratio = cur_assets / cur_liab
            if current_ratio > 1.5: score += 20
            elif current_ratio > 1.0: score += 10

        # Strategy specific
        if strategy == "long-term" and net_income > 0:
            score += 10 # Extra weight on profitability for long term

        return float(max(0, min(100, score)))

    def _score_risk_advanced(self, ticker, price, cur_a, cur_l, long_l, shares, net_kar, equity, summary) -> float:
        """Evaluate valuation (NCV/PE) and technical risk."""
        score = 50.0 # Start neutral
        
        # Graham NCV
        try:
            ncv = self.graham.margin_of_safety_analysis(ticker, price, cur_a, cur_l, long_l, shares)
            margin = ncv["margin_of_safety_pct"]
            if margin > 20: score += 25
            elif margin < -30: score -= 20
        except: pass
        
        # P/E Ratio
        pe = self.ratios.calculate_pe_ratio(price, net_kar, shares)
        pe_score = self.ratios.score_pe(pe)
        score += (pe_score - 5) * 2 # Map 0-10 score to risk impact
        
        return float(max(0, min(100, score)))
    
    def _generate_commentary(self, ticker, total_score, strengths, risks, sector, strategy) -> str:
        prefix = {
            "daily": "Günlük momentum analizi",
            "weekly": "Haftalık trend görünümü",
            "medium-term": "Orta vade büyüme odaklı analiz",
            "long-term": "Uzun vade değerleme raporu"
        }.get(strategy, "AI Analizi")

        if total_score >= 75: verdict = "Yüksek Potansiyel"
        elif total_score >= 50: verdict = "Dengeli/Pozitif"
        else: verdict = "Yüksek Risk/Zayıf"

        return f"{prefix}: {ticker} için {verdict} ({total_score:.1f}). {sector} sektöründe {' '.join(strengths[:1])}."
