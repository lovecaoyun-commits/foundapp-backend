from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["user"])

class UserProfile(BaseModel):
    user_id: str
    phone: str
    nickname: str = ""
    avatar: str = ""

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    return {
        "code": 0,
        "data": {
            "user_id": user_id,
            "phone": "***",
            "nickname": "User",
            "avatar": ""
        }
    }

@router.post("/profile/update")
async def update_profile(nickname: str = "", avatar: str = ""):
    return {"code": 0, "message": "更新成功"}
