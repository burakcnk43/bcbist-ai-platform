import pandas as pd
import numpy as np
import ta
from typing import Dict, Any
from ..core.logger import logger

class TechnicalEngine:
    """Professional Technical Analysis Engine calculating 40+ indicators."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        if history is None or history.empty or len(history) < 50:
            return {"technical_score": 50}

        try:
            close = history['Close']
            high = history['High']
            low = history['Low']
            volume = history['Volume']

            metrics = {}

            # --- Trend Indicators (15+) ---
            for p in [9, 20, 34, 50, 100, 150, 200]:
                metrics[f'ema_{p}'] = ta.trend.ema_indicator(close, window=p).iloc[-1]
            for p in [20, 50, 200]:
                metrics[f'sma_{p}'] = ta.trend.sma_indicator(close, window=p).iloc[-1]

            metrics['macd_obj'] = ta.trend.MACD(close)
            metrics['macd'] = metrics['macd_obj'].macd().iloc[-1]
            metrics['macd_signal'] = metrics['macd_obj'].macd_signal().iloc[-1]
            metrics['macd_diff'] = metrics['macd_obj'].macd_diff().iloc[-1]

            adx_obj = ta.trend.ADXIndicator(high, low, close)
            metrics['adx'] = adx_obj.adx().iloc[-1]
            metrics['di_plus'] = adx_obj.adx_pos().iloc[-1]
            metrics['di_minus'] = adx_obj.adx_neg().iloc[-1]

            metrics['cci'] = ta.trend.cci(high, low, close, window=20).iloc[-1]
            metrics['ichimoku_a'] = ta.trend.ichimoku_a(high, low).iloc[-1]
            metrics['ichimoku_b'] = ta.trend.ichimoku_b(high, low).iloc[-1]
            metrics['psar'] = ta.trend.psar_down(high, low, close).iloc[-1] # Simplification

            # --- Momentum Indicators (10+) ---
            metrics['rsi'] = ta.momentum.rsi(close, window=14).iloc[-1]
            stoch = ta.momentum.StochasticOscillator(high, low, close)
            metrics['stoch_k'] = stoch.stoch().iloc[-1]
            metrics['stoch_d'] = stoch.stoch_signal().iloc[-1]
            metrics['williams_r'] = ta.momentum.williams_r(high, low, close).iloc[-1]
            metrics['mfi'] = ta.volume.money_flow_index(high, low, close, volume).iloc[-1]
            metrics['roc'] = ta.momentum.roc(close).iloc[-1]
            metrics['tsi'] = ta.momentum.tsi(close).iloc[-1]

            # --- Volatility Indicators (5+) ---
            bb = ta.volatility.BollingerBands(close)
            metrics['bb_h'] = bb.bollinger_hband().iloc[-1]
            metrics['bb_l'] = bb.bollinger_lband().iloc[-1]
            metrics['bb_m'] = bb.bollinger_mavg().iloc[-1]
            metrics['atr'] = ta.volatility.average_true_range(high, low, close).iloc[-1]
            metrics['dc_h'] = ta.volatility.donchian_channel_hband(high, low, close).iloc[-1]
            metrics['dc_l'] = ta.volatility.donchian_channel_lband(high, low, close).iloc[-1]

            # --- Volume Indicators (5+) ---
            metrics['obv'] = ta.volume.on_balance_volume(close, volume).iloc[-1]
            metrics['cmf'] = ta.volume.chaikin_money_flow(high, low, close, volume).iloc[-1]
            metrics['vpt'] = ta.volume.volume_price_trend(close, volume).iloc[-1]
            metrics['em'] = ta.volume.ease_of_movement(high, low, volume).iloc[-1]

            # --- Custom Logic: Support/Resistance & Fibonacci ---
            max_p = history['High'].max()
            min_p = history['Low'].min()
            diff = max_p - min_p
            metrics['fib_236'] = max_p - 0.236 * diff
            metrics['fib_382'] = max_p - 0.382 * diff
            metrics['fib_500'] = max_p - 0.500 * diff
            metrics['fib_618'] = max_p - 0.618 * diff

            # Pivot Points (Standard)
            prev_day = history.iloc[-2]
            p_p = (prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3
            metrics['pivot'] = p_p
            metrics['r1'] = (2 * p_p) - prev_day['Low']
            metrics['s1'] = (2 * p_p) - prev_day['High']

            # --- Final Technical Score (0-100) ---
            last_price = close.iloc[-1]
            score = 0

            # Trend following (40 pts)
            if last_price > metrics['ema_20']: score += 10
            if last_price > metrics['ema_50']: score += 10
            if last_price > metrics['ema_200']: score += 10
            if metrics['macd_diff'] > 0: score += 10

            # Momentum (30 pts)
            if 40 < metrics['rsi'] < 70: score += 10
            if metrics['stoch_k'] > metrics['stoch_d']: score += 10
            if metrics['adx'] > 25: score += 10

            # Volatility & Volume (30 pts)
            if last_price < metrics['bb_h'] and last_price > metrics['bb_m']: score += 15
            if metrics['cmf'] > 0: score += 15

            metrics['technical_score'] = min(score, 100)
            logger.info(f"[TECHNICAL] Final Score: {metrics['technical_score']}")
            return metrics

        except Exception as e:
            logger.error(f"[ERROR] Technical Engine Detail: {str(e)}")
            return {"technical_score": 50}

technical_engine = TechnicalEngine()
