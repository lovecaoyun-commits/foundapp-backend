from fastapi import APIRouter

router = APIRouter(prefix="/moments", tags=["moments"])

@router.get("/list")
async def get_moments(page: int = 1, size: int = 20):
    return {"code": 0, "data": {"moments": [], "total": 0}}

@router.post("/publish")
async def publish_moment(content: str = "", images: str = ""):
    return {"code": 0, "message": "发布成功"}
