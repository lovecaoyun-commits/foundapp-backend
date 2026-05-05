from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user_id
from app.models.user import User, UserPreference
from app.database import get_db
from sqlalchemy.orm import Session
import uuid

router = APIRouter(prefix="/api/user", tags=["用户"])

def public_user(u: User) -> dict:
    return {
        "userId": str(u.id),
        "nickname": u.nickname,
        "avatar": u.avatar or "",
        "gender": u.gender,
        "city": u.city or "",
        "bio": u.bio or "",
        "tags": u.tags or [],
        "isVip": u.is_vip,
        "createdAt": str(u.created_at) if u.created_at else ""
    }

class UpdateProfileRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: int = None
    city: str = None
    bio: str = None
    tags: list = None

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 0, "data": public_user(user)}

@router.put("/profile")
async def update_profile(req: UpdateProfileRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if req.nickname is not None: user.nickname = req.nickname
    if req.avatar is not None: user.avatar = req.avatar
    if req.gender is not None: user.gender = req.gender
    if req.city is not None: user.city = req.city
    if req.bio is not None: user.bio = req.bio
    if req.tags is not None: user.tags = req.tags
    db.commit()
    return {"code": 0, "data": public_user(user)}

@router.get("/invite-code")
async def get_my_invite_code(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.invite_code:
        user.invite_code = uuid.uuid4().hex[:8].upper()
        db.commit()
    invite_link = f"https://found.app/invite/{user.invite_code}"
    return {"code": 0, "data": {"inviteCode": user.invite_code, "inviteLink": invite_link}}

@router.get("/invite-stats")
async def get_my_invite_stats(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 0,
        "data": {"inviteCount": 0, "totalRewards": 0, "remainingUses": 5}
    }
