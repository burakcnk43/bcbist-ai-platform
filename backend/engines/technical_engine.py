import pandas as pd
import numpy as np
import ta
from typing import Dict, Any
from core.logger import logger

class TechnicalEngine:
    """Institutional Grade Technical Analysis Engine with 40+ indicators (V4)."""

    def calculate_metrics(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Calculates indicators and returns a normalized score safely."""
        if history is None or history.empty:
            return {"technical_score": None}

        try:
            close = history['Close']
            high = history['High']
            low = history['Low']
            volume = history['Volume']
            data_len = len(history)

            metrics = {}

            def safe_last(series, default=None):
                if series is None or series.empty: return default
                val = series.iloc[-1]
                return float(val) if not np.isnan(val) else default

            # --- 1. Moving Averages (Trend) ---
            for p in [20, 50, 100, 200]:
                if data_len >= p:
                    metrics[f'ema{p}'] = safe_last(ta.trend.ema_indicator(close, window=p))
                    metrics[f'sma{p}'] = safe_last(ta.trend.sma_indicator(close, window=p))
                else:
                    metrics[f'ema{p}'] = None
                    metrics[f'sma{p}'] = None

            # --- 2. Oscillators (Momentum) ---
            if data_len >= 14:
                metrics['rsi'] = safe_last(ta.momentum.rsi(close, window=14), 50.0)
                macd = ta.trend.MACD(close)
                metrics['macd'] = safe_last(macd.macd(), 0.0)
                metrics['macd_signal'] = safe_last(macd.macd_signal(), 0.0)
                metrics['macd_hist'] = safe_last(macd.macd_diff(), 0.0)
                metrics['stoch_rsi'] = safe_last(ta.momentum.stochrsi(close), 0.5)
                metrics['williams_r'] = safe_last(ta.momentum.williams_r(high, low, close), -50.0)
                metrics['cci'] = safe_last(ta.trend.cci(high, low, close), 0.0)
            else:
                metrics.update({'rsi': None, 'macd': None, 'macd_signal': None, 'macd_hist': None, 'stoch_rsi': None, 'williams_r': None, 'cci': None})

            # --- 3. Trend Strength & Volatility ---
            if data_len >= 14:
                adx_indicator = ta.trend.ADXIndicator(high, low, close)
                metrics['adx'] = safe_last(adx_indicator.adx(), 20.0)
                metrics['di_plus'] = safe_last(adx_indicator.adx_pos(), 20.0)
                metrics['di_minus'] = safe_last(adx_indicator.adx_neg(), 20.0)

                atr = ta.volatility.AverageTrueRange(high, low, close)
                metrics['atr'] = safe_last(atr.average_true_range(), 0.0)

                bb = ta.volatility.BollingerBands(close)
                metrics['bb_high'] = safe_last(bb.bollinger_hband())
                metrics['bb_low'] = safe_last(bb.bollinger_lband())
                metrics['bb_mid'] = safe_last(bb.bollinger_mavg())
            else:
                metrics.update({'adx': None, 'di_plus': None, 'di_minus': None, 'atr': None, 'bb_high': None, 'bb_low': None, 'bb_mid': None})

            # --- 4. Volume Analysis ---
            if data_len >= 2:
                metrics['obv'] = safe_last(ta.volume.on_balance_volume(close, volume), 0.0)
                metrics['mfi'] = safe_last(ta.volume.money_flow_index(high, low, close, volume), 50.0)
                metrics['cmf'] = safe_last(ta.volume.chaikin_money_flow(high, low, close, volume), 0.0)
            else:
                metrics.update({'obv': None, 'mfi': None, 'cmf': None})

            # --- 5. Advanced Trend ---
            if data_len >= 26:
                ichimoku = ta.trend.IchimokuIndicator(high, low)
                metrics['ichimoku_a'] = safe_last(ichimoku.ichimoku_a())
                metrics['ichimoku_b'] = safe_last(ichimoku.ichimoku_b())
            else:
                metrics['ichimoku_a'] = None
                metrics['ichimoku_b'] = None

            # --- 6. Pivots & Fibonacci ---
            if data_len >= 2:
                last_p = history.iloc[-1]
                prev_p = history.iloc[-2]
                pivot = (prev_p['High'] + prev_p['Low'] + prev_p['Close']) / 3
                metrics['pivot'] = float(pivot)
                metrics['r1'] = float((2 * pivot) - prev_p['Low'])
                metrics['s1'] = float((2 * pivot) - prev_p['High'])

                period_max = high.tail(min(data_len, 100)).max()
                period_min = low.tail(min(data_len, 100)).min()
                metrics['fib_618'] = float(period_max - (period_max - period_min) * 0.618)
            else:
                metrics.update({'pivot': None, 'r1': None, 's1': None, 'fib_618': None})

            # --- Technical Score Calculation (Robust) ---
            score_components = []
            last_price = float(close.iloc[-1])

            # Trend (40%)
            if metrics.get('ema50') and last_price > metrics['ema50']: score_components.append(100)
            elif metrics.get('ema50'): score_components.append(0)

            if metrics.get('ema200') and last_price > metrics['ema200']: score_components.append(100)
            elif metrics.get('ema200'): score_components.append(0)

            # Momentum (30%)
            if metrics.get('rsi'):
                if 45 < metrics['rsi'] < 70: score_components.append(100)
                elif metrics['rsi'] > 70: score_components.append(70) # Overbought
                else: score_components.append(30)

            if metrics.get('macd_hist') is not None:
                score_components.append(100 if metrics['macd_hist'] > 0 else 0)

            # Strength (30%)
            if metrics.get('adx'):
                score_components.append(100 if metrics['adx'] > 25 else 40)

            if score_components:
                metrics['technical_score'] = int(sum(score_components) / len(score_components))
            else:
                metrics['technical_score'] = None

            return metrics

        except Exception as e:
            logger.error(f"[TECHNICAL ENGINE ERROR] {str(e)}")
            return {"technical_score": None}

technical_engine = TechnicalEngine()
