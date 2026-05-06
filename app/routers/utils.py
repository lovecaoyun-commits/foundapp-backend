from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/upload/token")
async def get_upload_token():
    return {"code": 0, "data": {"token": "", "upload_url": ""}}

@router.get("/areas")
async def get_areas():
    return {"code": 0, "data": []}
