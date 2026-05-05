from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.config import settings
import hmac, hashlib, base64, json, time

router = APIRouter(prefix="/api/trtc", tags=["TRTC"])

def gen_user_sig(user_id: str, expire: int = 86400 * 7) -> str:
    if not settings.TRTC_APP_KEY:
        raise HTTPException(status_code=500, detail="TRTC未配置")
    curr = int(time.time())
    expire_time = curr + expire
    obj = {"ver": 1, "appId": int(settings.TRTC_APP_ID), "userId": user_id,
           "curr": curr, "expire": expire_time, "nonce": curr % 999999}
    raw = json.dumps(obj, separators=(",", ":"))
    sig = hmac.new(settings.TRTC_APP_KEY.encode("latin1"), raw.encode("latin1"), hashlib.sha256).digest()
    return base64.b64encode(sig + raw.encode("latin1")).decode("latin1")

class UserSigRequest(BaseModel):
    userId: str

@router.get("/userSig/public")
async def get_user_sig_public(user_id: str = Query(...), expire: int = Query(86400 * 7)):
    sig = gen_user_sig(user_id, expire)
    return {"code": 0, "data": {"userSig": sig, "appId": int(settings.TRTC_APP_ID), "expireTime": int(time.time()) + expire}}

@router.get("/userSig")
async def get_user_sig(req: UserSigRequest = None, user_id: str = Query(None)):
    uid = req.userId if req and req.userId else user_id
    sig = gen_user_sig(uid)
    return {"code": 0, "data": {"userSig": sig, "appId": settings.TRTC_APP_ID}}

@router.post("/userSig")
async def post_user_sig(req: UserSigRequest):
    sig = gen_user_sig(req.userId)
    return {"code": 0, "data": {"userSig": sig, "appId": settings.TRTC_APP_ID}}
