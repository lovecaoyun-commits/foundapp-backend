from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.database import get_db
from sqlalchemy.orm import Session
import random, hashlib, time

router = APIRouter(prefix="/api/auth", tags=["认证"])

class SendCodeRequest(BaseModel):
    phone: str

class LoginRequest(BaseModel):
    phone: str
    code: str

def gen_mock_code() -> str:
    return str(random.randint(100000, 999999))

_mock_codes = {}

@router.post("/send-code")
async def send_code(req: SendCodeRequest, db: Session = Depends(get_db)):
    code = gen_mock_code()
    _mock_codes[req.phone] = code
    print(f"[MOCK SMS] phone={req.phone} code={code}")
    return {"code": 0, "message": "验证码已发送", "data": {"code": code}}

@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    real_code = _mock_codes.get(req.phone)
    if not real_code or real_code != req.code:
        raise HTTPException(status_code=400, detail="验证码错误")
    if req.phone in _mock_codes:
        del _mock_codes[req.phone]
    
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        user = User(phone=req.phone, nickname=f"用户{req.phone[-4:]}")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(str(user.id), user.phone)
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "code": 0,
        "data": {
            "userId": str(user.id),
            "nickname": user.nickname,
            "avatar": user.avatar or "",
            "accessToken": access_token,
            "refreshToken": refresh_token
        }
    }
