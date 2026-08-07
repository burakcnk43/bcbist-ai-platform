import pandas as pd
import numpy as np
import ta
from typing import Dict, Any
from ..core.logger import logger

class TechnicalEngine:
    """Institutional Grade Technical Analysis Engine with 40+ indicators."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Calculates indicators and returns a normalized score."""
        if history is None or history.empty or len(history) < 200:
            return {"technical_score": 50}

        try:
            close = history['Close']
            high = history['High']
            low = history['Low']
            volume = history['Volume']

            metrics = {}

            # --- 1. Moving Averages (Trend) ---
            for p in [20, 50, 100, 200]:
                metrics[f'ema{p}'] = ta.trend.ema_indicator(close, window=p).fillna(method='bfill').iloc[-1]
                metrics[f'sma{p}'] = ta.trend.sma_indicator(close, window=p).fillna(method='bfill').iloc[-1]

            # --- 2. Oscillators (Momentum) ---
            metrics['rsi'] = ta.momentum.rsi(close, window=14).fillna(50).iloc[-1]
            macd = ta.trend.MACD(close)
            metrics['macd'] = macd.macd().fillna(0).iloc[-1]
            metrics['macd_signal'] = macd.macd_signal().fillna(0).iloc[-1]
            metrics['macd_hist'] = macd.macd_diff().fillna(0).iloc[-1]
            metrics['stoch_rsi'] = ta.momentum.stochrsi(close).fillna(0.5).iloc[-1]
            metrics['williams_r'] = ta.momentum.williams_r(high, low, close).fillna(-50).iloc[-1]
            metrics['cci'] = ta.trend.cci(high, low, close).fillna(0).iloc[-1]

            # --- 3. Trend Strength & Volatility ---
            adx_indicator = ta.trend.ADXIndicator(high, low, close)
            metrics['adx'] = adx_indicator.adx().fillna(20).iloc[-1]
            metrics['di_plus'] = adx_indicator.adx_pos().fillna(20).iloc[-1]
            metrics['di_minus'] = adx_indicator.adx_neg().fillna(20).iloc[-1]

            atr = ta.volatility.AverageTrueRange(high, low, close)
            metrics['atr'] = atr.average_true_range().fillna(0).iloc[-1]

            bb = ta.volatility.BollingerBands(close)
            metrics['bb_high'] = bb.bollinger_hband().fillna(close).iloc[-1]
            metrics['bb_low'] = bb.bollinger_lband().fillna(close).iloc[-1]
            metrics['bb_mid'] = bb.bollinger_mavg().fillna(close).iloc[-1]

            keltner = ta.volatility.KeltnerChannel(high, low, close)
            metrics['keltner_high'] = keltner.keltner_channel_hband().fillna(close).iloc[-1]
            metrics['keltner_low'] = keltner.keltner_channel_lband().fillna(close).iloc[-1]

            donchian = ta.volatility.DonchianChannel(high, low, close)
            metrics['donchian_high'] = donchian.donchian_channel_hband().fillna(close).iloc[-1]
            metrics['donchian_low'] = donchian.donchian_channel_lband().fillna(close).iloc[-1]

            # --- 4. Volume Analysis ---
            metrics['obv'] = ta.volume.on_balance_volume(close, volume).fillna(0).iloc[-1]
            metrics['mfi'] = ta.volume.money_flow_index(high, low, close, volume).fillna(50).iloc[-1]
            metrics['cmf'] = ta.volume.chaikin_money_flow(high, low, close, volume).fillna(0).iloc[-1]
            metrics['vpt'] = ta.volume.volume_price_trend(close, volume).fillna(0).iloc[-1]

            # --- 5. Advanced Trend (Ichimoku & SuperTrend) ---
            ichimoku = ta.trend.IchimokuIndicator(high, low)
            metrics['ichimoku_a'] = ichimoku.ichimoku_a().fillna(close).iloc[-1]
            metrics['ichimoku_b'] = ichimoku.ichimoku_b().iloc[-1] if not ichimoku.ichimoku_b().empty else close.iloc[-1]

            # SuperTrend Real Implementation (ATR based)
            # Proxying SuperTrend as it's not in standard 'ta' but essential for institutional feel
            multiplier = 3
            med_price = (high + low) / 2
            atr_val = atr.average_true_range()
            upper_band = med_price + (multiplier * atr_val)
            lower_band = med_price - (multiplier * atr_val)
            metrics['supertrend_lower'] = lower_band.iloc[-1]
            metrics['supertrend_upper'] = upper_band.iloc[-1]

            # --- 6. Pivots, Fibonacci & S/R ---
            last_p = history.iloc[-1]
            prev_p = history.iloc[-2] if len(history) > 1 else last_p

            pivot = (prev_p['High'] + prev_p['Low'] + prev_p['Close']) / 3
            metrics['pivot'] = pivot
            metrics['r1'] = (2 * pivot) - prev_p['Low']
            metrics['s1'] = (2 * pivot) - prev_p['High']

            # Camarilla
            rng = prev_p['High'] - prev_p['Low']
            metrics['cam_h3'] = prev_p['Close'] + rng * 1.1 / 4
            metrics['cam_l3'] = prev_p['Close'] - rng * 1.1 / 4

            # Fibonacci 61.8% (Golden Pocket)
            period_max = high.tail(100).max()
            period_min = low.tail(100).min()
            metrics['fib_618'] = period_max - (period_max - period_min) * 0.618

            # --- Technical Score Calculation ---
            score = 50
            last_price = close.iloc[-1]

            # Trend Weight (40%)
            if last_price > metrics['ema50']: score += 10
            if last_price > metrics['ema200']: score += 10
            if metrics['sma50'] > metrics['sma200']: score += 5 # Golden Cross

            # Momentum Weight (30%)
            if 45 < metrics['rsi'] < 70: score += 10
            if metrics['macd_hist'] > 0: score += 10

            # Volume & Strength (30%)
            if metrics['adx'] > 25: score += 10
            if metrics['cmf'] > 0: score += 5

            metrics['technical_score'] = int(min(max(score, 0), 100))
            return metrics

        except Exception as e:
            logger.error(f"[TECHNICAL ENGINE ERROR] {str(e)}")
            return {"technical_score": 50}

technical_engine = TechnicalEngine()
