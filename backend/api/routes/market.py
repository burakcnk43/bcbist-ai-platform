from fastapi import APIRouter

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/status")
async def get_market_status():
    return {"status": "open", "indices": {"XU100": 10000.0, "XU030": 11000.0}}
