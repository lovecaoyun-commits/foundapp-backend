from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import time

router = APIRouter(prefix="/auth", tags=["auth"])

def make_token(user_id: str) -> str:
    import base64
    payload = f"{user_id}:{int(time.time())}"
    return base64.b64encode(payload.encode()).decode()

class LoginRequest(BaseModel):
    phone: str
    code: str

@router.post("/login")
async def login(req: LoginRequest):
    # Simple mock login - in production, verify SMS code
    if len(req.code) == 6:
        user_id = hashlib.md5(req.phone.encode()).hexdigest()[:16]
        token = make_token(user_id)
        return {
            "code": 0,
            "data": {
                "user_id": user_id,
                "access_token": token,
                "expires_in": 86400
            }
        }
    raise HTTPException(status_code=400, detail="验证码错误")

@router.post("/send_code")
async def send_code(phone: str):
    # Mock - in production, use Aliyun SMS
    return {"code": 0, "message": "发送成功"}
