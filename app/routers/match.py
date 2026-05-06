from fastapi import APIRouter

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/recommendations")
async def get_recommendations():
    return {
        "code": 0,
        "data": []
    }

@router.post("/like")
async def like_user(target_id: str):
    return {"code": 0, "message": "已喜欢"}

@router.post("/dislike")
async def dislike_user(target_id: str):
    return {"code": 0, "message": "不喜欢"}
