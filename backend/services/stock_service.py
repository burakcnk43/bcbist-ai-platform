import yfinance as yf
import pandas as pd
from typing import Optional

# Absolute Package Imports
from backend.core.logger import logger
from backend.core.cache import get_cached, set_cached
from backend.schemas.stock import StockData

class StockService:
    """Professional Data Fetching Service (V4) with error shielding and Pydantic safety."""

    def analyze_stock(self, symbol: str) -> Optional[StockData]:
        """Fetches comprehensive stock data with local caching and stringified keys for Pydantic."""
        cache_key = f"stock_data_v4_{symbol}"
        cached = get_cached(cache_key)
        if cached is not None: return cached

        try:
            full_symbol = f"{symbol}.IS" if not symbol.endswith(".IS") else symbol
            ticker = yf.Ticker(full_symbol)

            # Price History
            history = ticker.history(period="2y", auto_adjust=True)
            if history is None or history.empty:
                logger.warning(f"[V4] No history for {symbol}")
                return None

            # Financials (Safe extraction with string keys)
            info = ticker.info or {}

            def safe_stmt(df):
                if df is None or df.empty: return {}
                # Convert columns (Timestamps) to strings to satisfy Pydantic/JSON
                df_copy = df.copy()
                df_copy.columns = [str(c) for c in df_copy.columns]
                return df_copy.to_dict()

            income = safe_stmt(ticker.quarterly_income_stmt)
            balance = safe_stmt(ticker.quarterly_balance_sheet)
            cash = safe_stmt(ticker.quarterly_cashflow)

            stock_data = StockData(
                symbol=symbol,
                history=history,
                info=info,
                income_stmt=income,
                balance_sheet=balance,
                cash_flow=cash
            )

            set_cached(cache_key, stock_data, expire=1800)
            return stock_data

        except Exception as e:
            logger.error(f"[V4 STOCK SERVICE ERROR] {symbol}: {str(e)}")
            return None

stock_service = StockService()
