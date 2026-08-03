from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import yfinance as yf

from src.domain.services.confidence_engine import ConfidenceEngine
from src.domain.services.graham_valuation import GrahamValuationService
from src.domain.services.market_analysis import calculate_technicals, score_opportunity
from src.domain.services.ratio_analyzer import RatioAnalyzer

from backend.services.stock_registry import StockRegistryService

logger = logging.getLogger(__name__)


class StockService:
    """Expose reusable single-stock analysis logic for the FastAPI endpoint."""

    def __init__(self) -> None:
        """Initialize the stock analysis service."""
        self.ratio_analyzer = RatioAnalyzer()
        self.graham_service = GrahamValuationService()
        self.confidence_engine = ConfidenceEngine()
        self.registry_service = StockRegistryService()

    def analyze_stock(self, symbol: str) -> dict[str, Any]:
        """Build the complete single-stock analysis payload for the API."""
        normalized_symbol = symbol.strip().upper().replace(".IS", "")
        registry_entry = self.registry_service.get_symbol(normalized_symbol)
        if registry_entry is None:
            raise ValueError(f"{normalized_symbol} için desteklenmeyen Borsa İstanbul sembolü.")

        provider_symbol = f"{normalized_symbol}.IS"

        ticker = yf.Ticker(provider_symbol)
        history = ticker.history(period="2y", auto_adjust=True)
        if history.empty:
            raise ValueError(f"{normalized_symbol} için fiyat verisi alınamadı.")

        try:
            info = ticker.info
        except Exception as exc:
            logger.warning("Unable to fetch ticker info for %s: %s", normalized_symbol, exc)
            info = {}

        try:
            income = ticker.financials
            balance = ticker.balance_sheet
            cashflow = ticker.cashflow
        except Exception as exc:
            logger.warning("Unable to fetch financial statements for %s: %s", normalized_symbol, exc)
            income, balance, cashflow = None, None, None

        try:
            raw_news = ticker.news or []
        except Exception as exc:
            logger.warning("Unable to fetch news for %s: %s", normalized_symbol, exc)
            raw_news = []

        summary = calculate_technicals(history)
        latest_price = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else latest_price
        daily_change_pct = ((latest_price / previous_close) - 1) * 100 if previous_close else 0.0

        technical_metrics = self._build_technical_metrics(history, summary)
        volume_metrics = self._build_volume_metrics(history)
        financial_metrics = self._build_financial_metrics(income, balance, cashflow)
        valuation_metrics = self._build_valuation_metrics(
            latest_price=latest_price,
            balance=balance,
            income=income,
            info=info,
            financial_metrics=financial_metrics,
        )
        analysis_sections = self._build_analysis_sections(
            history=history,
            summary=summary,
            financial_metrics=financial_metrics,
            valuation_metrics=valuation_metrics,
            info=info,
            income=income,
            balance=balance,
            cashflow=cashflow,
            latest_price=latest_price,
        )
        news = self._build_news_payload(raw_news)
        score, reasons = score_opportunity(summary)

        return {
            "ticker": normalized_symbol,
            "symbol": normalized_symbol,
            "company_name": info.get("longName") or registry_entry["company_name"],
            "sector": info.get("sector") or registry_entry["sector"],
            "industry": info.get("industry") or "Bilinmiyor",
            "live_price": latest_price,
            "latest_price": latest_price,
            "previous_close": previous_close,
            "daily_change_pct": daily_change_pct,
            "weekly_change_pct": self._compute_change_pct(history, periods=5),
            "monthly_change_pct": self._compute_change_pct(history, periods=20),
            "yearly_change_pct": self._compute_change_pct(history, periods=252),
            "technical": technical_metrics,
            "technical_explanations": summary.explanations,
            "volume": volume_metrics,
            "financial": financial_metrics,
            "valuation": valuation_metrics,
            "analysis": analysis_sections,
            "news": news,
            "conclusion": {
                "score": score,
                "reasons": reasons,
            },
        }

    def _build_technical_metrics(self, history: pd.DataFrame, summary: Any) -> dict[str, Any]:
        """Build the technical metrics payload for the API."""
        close = history["Close"].astype(float)
        high = history["High"].astype(float)
        low = history["Low"].astype(float)

        ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
        ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
        ema_200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1]

        previous_close = close.shift(1)
        true_range = pd.concat([high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
        atr = true_range.ewm(span=14, adjust=False).mean().iloc[-1]

        return {
            "rsi": summary.rsi,
            "macd": summary.macd,
            "ema_20": float(ema_20),
            "ema_50": float(ema_50),
            "ema_200": float(ema_200),
            "sma_20": float(sma_20),
            "sma_50": float(sma_50),
            "sma_200": float(sma_200),
            "atr": float(atr),
            "support": summary.support,
            "resistance": summary.resistance,
            "trend": summary.trend,
        }

    def _build_volume_metrics(self, history: pd.DataFrame) -> dict[str, Any]:
        """Build the volume metrics payload for the API."""
        volumes = history["Volume"].astype(float)
        average_volume = float(volumes.tail(20).mean()) if not volumes.empty else None
        todays_volume = float(volumes.iloc[-1]) if not volumes.empty else None
        relative_volume = None if average_volume in (None, 0) else todays_volume / average_volume if todays_volume is not None else None

        return {
            "today_volume": todays_volume,
            "average_volume": average_volume,
            "relative_volume": relative_volume,
        }

    def _build_financial_metrics(self, income: Any, balance: Any, cashflow: Any) -> dict[str, Any]:
        """Build the financial metrics payload for the API."""
        revenue = self._latest_value(income, ["Total Revenue", "Operating Revenue"])
        net_income = self._latest_value(income, ["Net Income", "Net Income Common Stockholders"])
        ebitda = self._latest_value(income, ["EBITDA", "Normalized EBITDA"])
        debt = self._latest_value(balance, ["Total Debt", "Long Term Debt And Capital Lease Obligation", "Total Debt And Capital Lease Obligation"])
        equity = self._latest_value(balance, ["Stockholders Equity", "Total Stockholder Equity"])
        operating_cashflow = self._latest_value(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        capex = self._latest_value(cashflow, ["Capital Expenditure", "Capital Expenditures", "Capital Expenditures"])
        free_cash_flow = None
        if operating_cashflow is not None:
            if capex is None:
                free_cash_flow = operating_cashflow
            else:
                free_cash_flow = operating_cashflow - capex

        return {
            "revenue": revenue,
            "net_income": net_income,
            "ebitda": ebitda,
            "equity": equity,
            "debt": debt,
            "operating_cash_flow": operating_cashflow,
            "free_cash_flow": free_cash_flow,
        }

    def _build_valuation_metrics(self, latest_price: float, balance: Any, income: Any, info: dict[str, Any], financial_metrics: dict[str, Any]) -> dict[str, Any]:
        """Build the valuation metrics payload for the API."""
        shares_outstanding = self._coerce_float(info.get("sharesOutstanding"))
        if shares_outstanding in (None, 0):
            shares_outstanding = 1.0

        net_income = financial_metrics.get("net_income")
        pe_ratio = self.ratio_analyzer.calculate_pe_ratio(latest_price, net_income or 0.0, int(shares_outstanding)) if net_income is not None else None

        equity = financial_metrics.get("equity")
        pb_ratio = self.ratio_analyzer.calculate_pb_ratio(latest_price, equity or 0.0, int(shares_outstanding)) if equity is not None else None

        market_cap = self._coerce_float(info.get("marketCap"))
        debt = financial_metrics.get("debt")
        cash = self._latest_value(balance, ["Cash And Cash Equivalents", "Cash", "Cash And Short Term Investments"])
        ev = None
        if market_cap is not None and debt is not None:
            ev = market_cap + debt - (cash or 0.0)

        ebitda = financial_metrics.get("ebitda")
        ev_ebitda = None if ev is None or ebitda in (None, 0) else ev / ebitda

        graham = None
        try:
            donen_varliklar = self._latest_value(balance, ["Total Current Assets", "Current Assets"])
            kvyk = self._latest_value(balance, ["Current Liabilities", "Total Current Liabilities"])
            uvyk = self._latest_value(balance, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
            if donen_varliklar is not None and kvyk is not None and uvyk is not None:
                graham = self.graham_service.margin_of_safety_analysis(
                    ticker="",
                    current_price=latest_price,
                    donen_varliklar=donen_varliklar,
                    kisa_vadeli_yukumlulukler=kvyk,
                    uzun_vadeli_yukumlulukler=uvyk,
                    hisse_sayisi=int(shares_outstanding),
                )
        except Exception as exc:
            logger.warning("Unable to compute Graham valuation: %s", exc)

        return {
            "pe": pe_ratio,
            "pb": pb_ratio,
            "ev_ebitda": ev_ebitda,
            "graham": graham,
        }

    def _build_analysis_sections(
        self,
        history: pd.DataFrame,
        summary: Any,
        financial_metrics: dict[str, Any],
        valuation_metrics: dict[str, Any],
        info: dict[str, Any],
        income: Any,
        balance: Any,
        cashflow: Any,
        latest_price: float,
    ) -> dict[str, Any]:
        """Assemble the secondary analysis sections for the API response."""
        net_income = financial_metrics.get("net_income")
        equity = financial_metrics.get("equity")
        debt = financial_metrics.get("debt")
        operating_cash_flow = financial_metrics.get("operating_cash_flow")
        shares_outstanding = self._coerce_float(info.get("sharesOutstanding")) or 1.0
        market_cap = self._coerce_float(info.get("marketCap"))
        revenue = financial_metrics.get("revenue")
        ebitda = financial_metrics.get("ebitda")
        current_assets = self._latest_value(balance, ["Total Current Assets", "Current Assets"])
        current_liabilities = self._latest_value(balance, ["Current Liabilities", "Total Current Liabilities"])
        long_term_debt = self._latest_value(balance, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
        retained_earnings = self._latest_value(balance, ["Retained Earnings", "Retained Earnings (Accumulated Deficit)"])
        total_assets = self._latest_value(balance, ["Total Assets", "Total Assets, Total"])
        total_liabilities = self._latest_value(balance, ["Total Liabilities", "Total Liabilities And Stockholders Equity"])

        piotroski_score = self._build_piotroski_score(
            net_income=net_income,
            operating_cash_flow=operating_cash_flow,
            equity=equity,
            debt=debt,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            retained_earnings=retained_earnings,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
        )
        altman_z = self._build_altman_z_score(
            market_cap=market_cap,
            debt=debt,
            equity=equity,
            revenue=revenue,
            ebitda=ebitda,
            operating_cash_flow=operating_cash_flow,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
        )
        risk_metrics = self._build_risk_metrics(history, latest_price, valuation_metrics)
        confidence_score = self._build_confidence_score(
            latest_price=latest_price,
            financial_metrics=financial_metrics,
            valuation_metrics=valuation_metrics,
            balance=balance,
            summary=summary,
            info=info,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            long_term_debt=long_term_debt,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
        )
        ai_summary = self._build_ai_summary(summary, valuation_metrics, piotroski_score, altman_z, risk_metrics, confidence_score)
        overall_score = self._build_overall_score(summary, valuation_metrics, piotroski_score, altman_z, risk_metrics, confidence_score)

        return {
            "piotroski": piotroski_score,
            "altman_z": altman_z,
            "peter_lynch": {
                "estimated_value": self._estimate_peter_lynch_value(net_income, shares_outstanding, revenue),
                "method": "EPS × P/E proxy",
            },
            "trend_analysis": {
                "trend": summary.trend,
                "rsi": summary.rsi,
                "momentum_20d": getattr(summary, "momentum_20d", None),
            },
            "volume_analysis": {
                "today_volume": self._coerce_float(history["Volume"].iloc[-1]) if not history.empty else None,
                "average_volume": self._coerce_float(history["Volume"].tail(20).mean()) if not history.empty else None,
                "relative_volume": self._coerce_float((history["Volume"].iloc[-1] / history["Volume"].tail(20).mean())) if not history.empty else None,
            },
            "support_resistance": {
                "support": summary.support,
                "resistance": summary.resistance,
            },
            "risk_metrics": risk_metrics,
            "ai_summary": ai_summary,
            "overall_score": overall_score,
        }

    def _build_piotroski_score(self, **values: Any) -> dict[str, Any]:
        """Re-use the Piotroski F-score heuristic with a compact payload."""
        score = 0
        conditions = []
        if values.get("net_income", 0) is not None and values.get("net_income", 0) > 0:
            score += 1
            conditions.append("Net income positive")
        if values.get("operating_cash_flow", 0) is not None and values.get("operating_cash_flow", 0) > 0:
            score += 1
            conditions.append("Operating cash flow positive")
        if values.get("net_income", 0) is not None and values.get("operating_cash_flow", 0) is not None and values.get("net_income", 0) > values.get("operating_cash_flow", 0):
            score += 1
            conditions.append("Net income > CFO")
        if values.get("equity", 0) is not None and values.get("equity", 0) > 0:
            score += 1
            conditions.append("Equity positive")
        if values.get("debt", 0) is not None and values.get("debt", 0) <= 0:
            score += 1
            conditions.append("Debt not increasing")
        if values.get("current_assets", 0) is not None and values.get("current_liabilities", 0) is not None and values.get("current_assets", 0) > values.get("current_liabilities", 0):
            score += 1
            conditions.append("Current ratio > 1")
        if values.get("retained_earnings", 0) is not None and values.get("retained_earnings", 0) > 0:
            score += 1
            conditions.append("Retained earnings positive")
        if values.get("total_assets", 0) is not None and values.get("total_liabilities", 0) is not None and values.get("total_assets", 0) > values.get("total_liabilities", 0):
            score += 1
            conditions.append("Assets > liabilities")
        return {"score": score, "conditions": conditions}

    def _build_altman_z_score(self, **values: Any) -> dict[str, Any]:
        """Return a lightweight Altman Z proxy based on common financial ratios."""
        total_assets = values.get("total_assets")
        total_liabilities = values.get("total_liabilities")
        equity = values.get("equity")
        revenue = values.get("revenue")
        ebitda = values.get("ebitda")
        operating_cash_flow = values.get("operating_cash_flow")
        market_cap = values.get("market_cap")
        debt = values.get("debt")
        if total_assets in (None, 0):
            return {"score": 0, "label": "Veri yetersiz", "components": {}}
        working_capital = (total_assets or 0) - (total_liabilities or 0)
        retained_earnings = equity or 0
        ebit = ebitda or 0
        z_score = (1.2 * (working_capital / total_assets)) + (1.4 * (retained_earnings / total_assets)) + (3.3 * (ebit / total_assets)) + (0.6 * ((market_cap or 0) / (debt or 0 if debt not in (None, 0) else 1.0))) + (1.0 * ((revenue or 0) / total_assets))
        if z_score > 2.99:
            label = "Güçlü"
        elif z_score > 1.81:
            label = "İşaretli"
        else:
            label = "Riskli"
        return {"score": round(z_score, 2), "label": label, "components": {"working_capital": working_capital}}

    def _build_risk_metrics(self, history: pd.DataFrame, latest_price: float, valuation_metrics: dict[str, Any]) -> dict[str, Any]:
        """Create normalized risk metrics from history and valuation context."""
        returns = history["Close"].pct_change().dropna().tail(60)
        if returns.empty:
            annualized_volatility = None
        else:
            annualized_volatility = float(returns.std() * (252 ** 0.5) * 100)
        if annualized_volatility is None:
            volatility_label = "Veri yetersiz"
        elif annualized_volatility < 25:
            volatility_label = "Düşük"
        elif annualized_volatility < 45:
            volatility_label = "Orta"
        else:
            volatility_label = "Yüksek"
        pe = valuation_metrics.get("pe")
        pb = valuation_metrics.get("pb")
        return {
            "volatility_label": volatility_label,
            "annualized_volatility": annualized_volatility,
            "price_to_earnings": pe,
            "price_to_book": pb,
            "latest_price": latest_price,
        }

    def _build_confidence_score(self, latest_price: float, financial_metrics: dict[str, Any], valuation_metrics: dict[str, Any], balance: Any, summary: Any, info: dict[str, Any], current_assets: Any, current_liabilities: Any, long_term_debt: Any, total_assets: Any, total_liabilities: Any) -> Any:
        """Reuse the existing confidence engine for a consistent overall score."""
        net_income = financial_metrics.get("net_income") or 0.0
        operating_cash_flow = financial_metrics.get("operating_cash_flow") or 0.0
        equity = financial_metrics.get("equity") or 0.0
        debt = financial_metrics.get("debt") or 0.0
        revenue = financial_metrics.get("revenue") or 0.0
        shares_outstanding = self._coerce_float(info.get("sharesOutstanding")) or 1.0

        trend = "bullish" if summary.trend == "Yukarı yönlü" else "bearish" if summary.trend == "Aşağı yönlü" else "neutral"
        try:
            return self.confidence_engine.analyze(
                ticker=info.get("symbol") or "",
                current_price=latest_price,
                donen_varliklar=current_assets or 0.0,
                kisa_vadeli_yukumlulukler=current_liabilities or 0.0,
                uzun_vadeli_yukumlulukler=long_term_debt or 0.0,
                oz_sermaye=equity,
                net_kar=net_income,
                hisse_sayisi=int(shares_outstanding),
                isletme_nakit_akisi=operating_cash_flow,
                sector=info.get("sector") or "Genel",
                rsi=summary.rsi or 50,
                trend=trend,
            )
        except Exception:
            return None

    def _build_ai_summary(self, summary: Any, valuation_metrics: dict[str, Any], piotroski_score: dict[str, Any], altman_z: dict[str, Any], risk_metrics: dict[str, Any], confidence_score: Any) -> dict[str, Any]:
        """Create a compact AI-style summary from existing indicators."""
        trend = summary.trend
        valuation = valuation_metrics.get("graham", {}) if isinstance(valuation_metrics.get("graham"), dict) else {}
        graham_recommendation = valuation.get("graham_recommendation") or "Belirsiz"
        commentary = confidence_score.commentary if confidence_score is not None else f"{trend} görünüm, Piotroski {piotroski_score['score']}/8, Altman Z {altman_z['score']}, risk {risk_metrics['volatility_label']}, Graham {graham_recommendation}."
        return {
            "summary": commentary,
            "trend": trend,
            "valuation_note": graham_recommendation,
        }

    def _build_overall_score(self, summary: Any, valuation_metrics: dict[str, Any], piotroski_score: dict[str, Any], altman_z: dict[str, Any], risk_metrics: dict[str, Any], confidence_score: Any) -> dict[str, Any]:
        """Create an overall score by blending existing signals."""
        if confidence_score is not None:
            score = int(round(confidence_score.total_score))
            return {"score": score, "band": "Yüksek" if score >= 75 else "Orta" if score >= 45 else "Düşük"}

        score = 0
        if summary.trend == "Yukarı yönlü":
            score += 30
        elif summary.trend == "Aşağı yönlü":
            score -= 15
        if summary.rsi is not None and 45 <= summary.rsi <= 65:
            score += 20
        elif summary.rsi is not None and summary.rsi >= 75:
            score -= 10
        if piotroski_score.get("score", 0) >= 6:
            score += 18
        elif piotroski_score.get("score", 0) >= 4:
            score += 10
        if altman_z.get("score", 0) > 2.0:
            score += 18
        elif altman_z.get("score", 0) > 1.0:
            score += 8
        if risk_metrics.get("volatility_label") == "Düşük":
            score += 10
        elif risk_metrics.get("volatility_label") == "Orta":
            score += 5
        if valuation_metrics.get("pe") is not None and valuation_metrics.get("pe") <= 20:
            score += 10
        if valuation_metrics.get("pb") is not None and valuation_metrics.get("pb") <= 2:
            score += 10
        score = max(0, min(100, score))
        return {"score": score, "band": "Yüksek" if score >= 75 else "Orta" if score >= 45 else "Düşük"}

    def _estimate_peter_lynch_value(self, net_income: Any, shares_outstanding: Any, revenue: Any) -> float | None:
        """Estimate a Peter Lynch style value based on earnings and revenue."""
        if net_income in (None, 0) or shares_outstanding in (None, 0):
            return None
        eps = net_income / shares_outstanding
        if revenue in (None, 0):
            return None
        return round(eps * (revenue / max(net_income, 1.0)), 2)

    def _build_news_payload(self, raw_news: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Build the news payload used by the API."""
        news_items: list[dict[str, Any]] = []
        for item in raw_news[:8]:
            content = item.get("content", item)
            title = content.get("title") or item.get("title") or "Başlıksız içerik"
            provider = content.get("provider", {}).get("displayName") or content.get("publisher") or "Kaynak belirtilmemiş"
            url = content.get("canonicalUrl", {}).get("url") or content.get("clickThroughUrl", {}).get("url") or item.get("link")
            news_items.append({
                "title": title,
                "provider": provider,
                "url": url,
            })
        return news_items

    def _compute_change_pct(self, history: pd.DataFrame, periods: int) -> float | None:
        """Compute percentage change versus a prior close window."""
        closes = history["Close"].astype(float).dropna()
        if closes.empty:
            return None
        if len(closes) <= periods:
            reference = closes.iloc[0]
        else:
            reference = closes.iloc[-periods - 1]
        current = closes.iloc[-1]
        if reference in (None, 0):
            return None
        return ((current / reference) - 1) * 100

    def _coerce_float(self, value: Any) -> float | None:
        """Convert a value to float when possible."""
        if value is None or pd.isna(value):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _latest_value(self, frame: Any, labels: list[str]) -> float | None:
        """Return the first available value from a financial statement frame."""
        if frame is None or getattr(frame, "empty", True):
            return None
        for label in labels:
            if label in frame.index:
                values = frame.loc[label].dropna()
                if not values.empty:
                    return self._coerce_float(values.iloc[0])
            if label in frame.columns:
                values = frame[label].dropna()
                if not values.empty:
                    return self._coerce_float(values.iloc[0])
        return None

