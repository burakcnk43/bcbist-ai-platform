import yfinance as yf
import pandas as pd
from typing import Optional
from ..core.logger import logger
from ..core.cache import get_cached, set_cached
from ..schemas.stock import StockData

class StockService:
    """Professional Data Fetching Service with robust error handling and caching."""

    def analyze_stock(self, symbol: str) -> Optional[StockData]:
        """Fetches comprehensive stock data with local caching."""
        cache_key = f"stock_full_v3_{symbol}"
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            full_symbol = f"{symbol}.IS"
            ticker = yf.Ticker(full_symbol)

            # --- 1. Price History ---
            # Using 2 years for trend and risk calculations
            history = ticker.history(period="2y", auto_adjust=True)
            if history.empty:
                logger.warning(f"[STOCK SERVICE] No history found for {symbol}")
                return None

            # --- 2. Financials ---
            # Fetching quarterly data for growth and stability analysis
            info = ticker.info or {}
            income = ticker.quarterly_income_stmt.to_dict() if not ticker.quarterly_income_stmt.empty else {}
            balance = ticker.quarterly_balance_sheet.to_dict() if not ticker.quarterly_balance_sheet.empty else {}
            cash = ticker.quarterly_cashflow.to_dict() if not ticker.quarterly_cashflow.empty else {}

            stock_data = StockData(
                symbol=symbol,
                history=history,
                info=info,
                income_stmt=income,
                balance_sheet=balance,
                cash_flow=cash
            )

            # Store in diskcache for 30 minutes
            set_cached(cache_key, stock_data, expire=1800)
            return stock_data

        except Exception as e:
            logger.error(f"[STOCK SERVICE ERROR] Failed to fetch {symbol}: {str(e)}")
            return None

stock_service = StockService()
