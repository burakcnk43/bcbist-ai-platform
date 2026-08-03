import logging
import os
import sys
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.routes.analysis import router as analysis_router
from backend.routes.market import router as market_router
from backend.routes.portfolio import router as portfolio_router
from backend.routes.stocks import router as stocks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("bcbist_backend")

app = FastAPI(
    title="BCBIST AI Platform",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks_router)
app.include_router(market_router)
app.include_router(analysis_router)
app.include_router(portfolio_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Log backend startup without changing application behavior."""
    logger.info("BCBIST AI Platform startup completed")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log backend shutdown without changing application behavior."""
    logger.info("BCBIST AI Platform shutdown completed")


@app.get("/health", summary="Health check", description="Return backend availability")
async def health() -> dict[str, Any]:
    return {
        "status": "online",
        "service": "BCBIST AI Platform",
        "version": "1.0",
    }
