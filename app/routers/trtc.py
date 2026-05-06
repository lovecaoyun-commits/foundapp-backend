from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import hmac, hashlib, base64, json, time

router = APIRouter(prefix="/v1/trtc", tags=["TRTC"])

# Tencent TRTC credentials - from user provided SDKAppID + SecretKey
TRTC_APP_ID = "1600137968"
TRTC_SECRET_KEY = "5d4ca7c35966f76ab37177e706efff3a8265bea24137d32d06bcc047524751bc"

def gen_user_sig(user_id: str, expire: int = 86400 * 7) -> str:
    """Generate TRTC UserSig using HMAC-SHA256"""
    curr = int(time.time())
    expire_time = curr + expire
    obj = {"ver": 1, "appId": int(TRTC_APP_ID), "userId": user_id,
           "curr": curr, "expire": expire_time, "nonce": curr % 999999}
    raw = json.dumps(obj, separators=(",", ":"))
    sig = hmac.new(TRTC_SECRET_KEY.encode("latin1"), raw.encode("latin1"), hashlib.sha256).digest()
    return base64.b64encode(sig + raw.encode("latin1")).decode("latin1")

class UserSigRequest(BaseModel):
    userId: str

@router.get("/sign")
async def get_trtc_sign(
    room_id: str = Query(..., description="TRTC room ID"),
    user_id: str = Query(..., description="User ID")
):
    """Generate real TRTC UserSig for video call"""
    sig = gen_user_sig(user_id)
    return {"code": 0, "data": {"signature": sig, "appId": int(TRTC_APP_ID)}}

@router.get("/userSig/public")
async def get_user_sig_public(
    user_id: str = Query(..., description="用户ID"),
    expire: int = Query(86400 * 7, description="有效期秒")
):
    """公开获取UserSig，无需登录（通话签名不含敏感信息）"""
    sig = gen_user_sig(user_id, expire)
    return {"code": 0, "data": {"userSig": sig, "appId": int(TRTC_APP_ID), "expireTime": int(time.time()) + expire}}

@router.get("/userSig")
async def get_user_sig(user_id: str = Query(...)):
    sig = gen_user_sig(user_id)
    return {"code": 0, "data": {"userSig": sig, "appId": TRTC_APP_ID}}

@router.post("/userSig")
async def post_user_sig(req: UserSigRequest):
    sig = gen_user_sig(req.userId)
    return {"code": 0, "data": {"userSig": sig, "appId": TRTC_APP_ID}}
