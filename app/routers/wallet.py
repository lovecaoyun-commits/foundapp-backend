from fastapi import APIRouter

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/balance")
async def get_balance():
    return {"code": 0, "data": {"coins": 100, "vip_expire": None}}

@router.get("/recharge/packages")
async def get_packages():
    return {"code": 0, "data": []}
