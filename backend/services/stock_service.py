import yfinance as yf
import pandas as pd
from typing import Optional
from ..core.logger import logger
from ..core.cache import get_cached, set_cached
from ..schemas.stock import StockData

class StockService:
    """Service for fetching comprehensive stock data from Yahoo Finance."""

    def analyze_stock(self, symbol: str) -> Optional[StockData]:
        """Fetch all data (History + Financials) for a single stock."""
        cache_key = f"stock_full_data_{symbol}"
        cached_data = get_cached(cache_key)
        if cached_data:
            return cached_data

        try:
            full_symbol = f"{symbol}.IS"
            ticker = yf.Ticker(full_symbol)

            # Fetch data with timeout control via yfinance parameters if available or handling
            history = ticker.history(period="2y") # 2 years for trend and long-term analysis
            if history.empty:
                logger.warning(f"[WARN] No history for {symbol}")
                return None

            stock_data = StockData(
                symbol=symbol,
                history=history,
                info=ticker.info,
                income_stmt=ticker.quarterly_income_stmt.to_dict() if not ticker.quarterly_income_stmt.empty else {},
                balance_sheet=ticker.quarterly_balance_sheet.to_dict() if not ticker.quarterly_balance_sheet.empty else {},
                cash_flow=ticker.quarterly_cashflow.to_dict() if not ticker.quarterly_cashflow.empty else {}
            )

            set_cached(cache_key, stock_data)
            return stock_data

        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch data for {symbol}: {str(e)}")
            return None

stock_service = StockService()
