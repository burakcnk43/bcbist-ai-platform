from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
import pandas as pd

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None

class StockData(BaseModel):
    symbol: str
    history: Optional[Any] = None  # DataFrame stored as dict or handled by service
    info: Optional[Dict[str, Any]] = None
    financials: Optional[Dict[str, Any]] = None
    income_stmt: Optional[Dict[str, Any]] = None
    balance_sheet: Optional[Dict[str, Any]] = None
    cash_flow: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
