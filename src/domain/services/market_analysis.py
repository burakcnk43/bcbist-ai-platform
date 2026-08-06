"""Doğrulanabilir piyasa verisini teknik analiz özetine dönüştüren yardımcılar.

Bu modül yatırım tavsiyesi üretmez. Yorumlar yalnızca hesaplanan göstergelerin
durumunu açıklar; veri yoksa sonuç üretmek yerine bunu açıkça bildirir.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TechnicalSummary:
    trend: str
    rsi: float | None
    macd: float | None
    macd_signal: float | None
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    ema_20: float | None
    ema_50: float | None
    ema_200: float | None
    bollinger_upper: float | None
    bollinger_lower: float | None
    bollinger_mavg: float | None
    momentum_20d: float | None
    volume_ratio: float | None
    atr_14: float | None
    adx: float | None
    stoch_k: float | None
    stoch_d: float | None
    cci: float | None
    williams_r: float | None
    support: float | None
    resistance: float | None
    explanations: list[str]


def _number(value: Any) -> float | None:
    """Convert a pandas/numpy value to float without leaking NaN to the UI."""
    if value is None or pd.isna(value):
        return None
    try:
        val = float(value)
        return val if np.isfinite(val) else None
    except (ValueError, TypeError):
        return None


def _last(series: pd.Series) -> float | None:
    return _number(series.iloc[-1]) if not series.empty else None


def calculate_technicals(history: pd.DataFrame) -> TechnicalSummary:
    """Calculate professional-grade indicators from an OHLCV dataframe."""
    required = {"Close", "High", "Low", "Volume"}
    if history is None or history.empty or not required.issubset(history.columns):
        return TechnicalSummary(
            "Veri yetersiz", None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, ["Teknik analiz için yeterli fiyat verisi alınamadı."]
        )

    frame = history.copy().dropna(subset=["Close"])
    close = frame["Close"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    volume = frame["Volume"].astype(float)

    # 1. RSI (Wilder's)
    delta = close.diff()
    gains = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    losses = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = gains / losses.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # 2. MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()

    # 3. Moving Averages
    sma_20 = close.rolling(20, min_periods=20).mean()
    sma_50 = close.rolling(50, min_periods=50).mean()
    sma_200 = close.rolling(200, min_periods=200).mean()
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    ema_200 = close.ewm(span=200, adjust=False).mean()

    # 4. Bollinger Bands
    rolling_std = close.rolling(20, min_periods=20).std()
    boll_mid = sma_20
    boll_upper = boll_mid + (2 * rolling_std)
    boll_lower = boll_mid - (2 * rolling_std)

    # 5. ATR (Average True Range)
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/14, adjust=False).mean()

    # 6. ADX (Lightweight approximation)
    up_move = high.diff()
    down_move = low.diff().abs()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    tr_smooth = tr.ewm(alpha=1/14, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm).ewm(alpha=1/14, adjust=False).mean() / tr_smooth
    minus_di = 100 * pd.Series(minus_dm).ewm(alpha=1/14, adjust=False).mean() / tr_smooth
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False).mean()

    # 7. Stochastic Oscillator
    low_14 = low.rolling(14).min()
    high_14 = high.rolling(14).max()
    stoch_k = 100 * (close - low_14) / (high_14 - low_14).replace(0, np.nan)
    stoch_d = stoch_k.rolling(3).mean()

    # 8. Williams %R
    williams_r = -100 * (high_14 - close) / (high_14 - low_14).replace(0, np.nan)

    # 9. CCI (Commodity Channel Index)
    tp = (high + low + close) / 3
    cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).apply(lambda x: np.std(x)))

    # 10. Trend & Volume
    momentum = close.pct_change(20) * 100
    vol_avg = volume.rolling(20).mean()
    vol_ratio = volume / vol_avg.replace(0, np.nan)

    price = _last(close)
    l_sma20, l_sma50, l_sma200 = _last(sma_20), _last(sma_50), _last(sma_200)

    if price is None or l_sma20 is None:
        trend = "Veri yetersiz"
    elif l_sma200 is not None and price > l_sma200:
        trend = "Güçlü Boğa" if price > l_sma50 > l_sma200 else "Boğa"
    elif l_sma200 is not None and price < l_sma200:
        trend = "Güçlü Ayı" if price < l_sma50 < l_sma200 else "Ayı"
    else:
        trend = "Yatay"

    notes = [f"Ana Trend: {trend}"]
    l_rsi = _last(rsi)
    if l_rsi: notes.append(f"RSI {l_rsi:.1f} ({'Aşırı Alım' if l_rsi > 70 else 'Aşırı Satım' if l_rsi < 30 else 'Nötr'})")

    lookback = min(20, len(frame))
    return TechnicalSummary(
        trend=trend,
        rsi=l_rsi,
        macd=_last(macd_line),
        macd_signal=_last(macd_signal),
        sma_20=l_sma20,
        sma_50=l_sma50,
        sma_200=l_sma200,
        ema_20=_last(ema_20),
        ema_50=_last(ema_50),
        ema_200=_last(ema_200),
        bollinger_upper=_last(boll_upper),
        bollinger_lower=_last(boll_lower),
        bollinger_mavg=_last(boll_mid),
        momentum_20d=_last(momentum),
        volume_ratio=_last(vol_ratio),
        atr_14=_last(atr),
        adx=_last(adx),
        stoch_k=_last(stoch_k),
        stoch_d=_last(stoch_d),
        cci=_last(cci),
        williams_r=_last(williams_r),
        support=_number(low.tail(lookback).min()),
        resistance=_number(high.tail(lookback).max()),
        explanations=notes
    )
ef score_opportunity(summary: TechnicalSummary) -> tuple[int, list[str]]:
    """Return a transparent watch-list score, not an investment recommendation."""
    score = 0
    reasons: list[str] = []
    if summary.trend == "Yukarı yönlü":
        score += 35
        reasons.append("Fiyat kısa ve orta vadeli ortalamaların üzerinde.")
    if summary.rsi is not None and 55 <= summary.rsi < 68:
        score += 25
        reasons.append("RSI pozitif bölgede ve aşırı alım eşiğinin altında.")
    elif summary.rsi is not None and summary.rsi >= 75:
        score -= 10
        reasons.append("RSI çok yüksek; kısa vadeli aşırı alım riski puanı düşürdü.")
    if summary.macd is not None and summary.macd_signal is not None and summary.macd > summary.macd_signal:
        score += 20
        reasons.append("MACD sinyal çizgisinin üzerinde.")
    if summary.volume_ratio is not None and summary.volume_ratio >= 1.2:
        score += 20
        reasons.append("Hacim 20 günlük ortalamanın belirgin üzerinde.")
    return max(0, min(100, score)), reasons
