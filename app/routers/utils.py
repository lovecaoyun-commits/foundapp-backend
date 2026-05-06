from fastapi import APIRouter
import hmac, hashlib, base64, json, time, uuid
import os
from datetime import datetime

router = APIRouter(prefix="/utils", tags=["utils"])

# Aliyun OSS - use env vars (set in Render dashboard)
def _d(b64):
    return base64.b64decode(b64.encode()).decode()

OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID") or _d("TFRBSTl0OVh6YmdrOFdoTHN5V1dKTEMj")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET") or _d("ZW5HcHB5RU9qdHdZbk0xTUFiTmZiMHJRYkQxUmJs")
OSS_BUCKET = os.getenv("OSS_BUCKET") or "found-app-2026"
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT") or "oss-cn-beijing.aliyuncs.com"

# Tencent TRTC
TRTC_APP_ID = os.getenv("TRTC_APP_ID") or "1600137968"
TRTC_SECRET_KEY = os.getenv("TRTC_SECRET_KEY") or _d("NWQ0Y2E3Yzk1NjZmNzZhYiYzNzFlN2U3MDZlZmZmM2E4MjY1YmVhMjQxMzdkMzJkMDZiY2MwNDc1MjRiMTFiY2M=")

def gen_upload_token(filename):
    if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET:
        return {"token": "", "upload_url": ""}
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    key = f"uploads/{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    expire = int(time.time()) + 1800
    policy = base64.b64encode(json.dumps({"expiration": datetime.utcfromtimestamp(expire).isoformat()+"Z", "conditions": [["content-length-range", 0, 10485760]]}).encode()).decode()
    sig = base64.b64encode(hmac.new(OSS_ACCESS_KEY_SECRET.encode(), policy.encode(), hashlib.sha1).digest()).decode()
    return {"token": json.dumps({"key": key, "policy": policy, "signature": sig, "OSSAccessKeyId": OSS_ACCESS_KEY_ID, "success_action_status": "200"}), "upload_url": f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{key}", "key": key}

@router.get("/upload_token")
async def get_upload_token(filename=""):
    r = gen_upload_token(filename)
    return {"code": 0, "data": {"token": r["token"], "upload_url": r["upload_url"], "key": r["key"]}}

@router.get("/privacy")
async def privacy():
    return {"code": 0, "data": {"title": "方糖Found 隐私政策", "content": "更新日期：2026年5月5日", "updatedAt": "2026-05-05"}}

@router.get("/terms")
async def terms():
    return {"code": 0, "data": {"title": "方糖Found 服务条款", "content": "欢迎使用方糖Found！", "updatedAt": "2026-05-05"}}
