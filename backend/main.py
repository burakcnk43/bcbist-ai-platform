import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logger import logger
from .api.routes import recommendations, market, stocks, portfolio

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="3.0.0", # V3
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url="/docs"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers (Consolidated V3)
app.include_router(recommendations.router, prefix=settings.API_STR)
app.include_router(market.router, prefix=settings.API_STR)
app.include_router(stocks.router, prefix=settings.API_STR)
app.include_router(portfolio.router, prefix=settings.API_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("[STARTUP] BCBIST V3 PRO is starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("[SHUTDOWN] BCBIST V3 PRO is shutting down...")

@app.get("/")
async def root():
    return {"message": "BCBIST V3 PRO API is active", "version": "3.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
