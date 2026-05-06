from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["user"])

class UserProfile(BaseModel):
    user_id: str
    phone: str = ""
    nickname: str = ""
    avatar: str = ""
    gender: int = 0
    birthday: str = ""
    bio: str = ""
    location: str = ""
    verified: bool = False
    vip_expire: str = ""

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    return {"code": 0, "data": {"user_id": user_id, "nickname": "用户" + user_id[:4], "avatar": "", "gender": 0}}

@router.post("/profile/update")
async def update_profile(nickname: str = "", avatar: str = "", gender: int = 0, birthday: str = "", bio: str = "", location: str = ""):
    return {"code": 0, "message": "更新成功"}
