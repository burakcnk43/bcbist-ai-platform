from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    ai_score: Optional[int] = None

class StockData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    symbol: str
    history: Optional[Any] = None
    info: Optional[Dict[str, Any]] = None
    income_stmt: Optional[Dict[str, Any]] = None
    balance_sheet: Optional[Dict[str, Any]] = None
    cash_flow: Optional[Dict[str, Any]] = None
