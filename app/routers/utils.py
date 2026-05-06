from fastapi import APIRouter, HTTPException
import hmac, hashlib, base64, json, time, uuid
import os
from datetime import datetime

router = APIRouter(prefix="/v1", tags=["utils"])

# Aliyun OSS credentials - from environment variables
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET", "")
OSS_BUCKET = os.getenv("OSS_BUCKET", "found-app-2026")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")

def gen_upload_token(filename: str) -> dict:
    if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET:
        return {"token": "", "upload_url": ""}
    
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    key = f"uploads/{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    expire = int(time.time()) + 1800
    
    policy_dict = {
        "expiration": datetime.utcfromtimestamp(expire).isoformat() + "Z",
        "conditions": [["content-length-range", 0, 10485760]]
    }
    policy = base64.b64encode(json.dumps(policy_dict).encode()).decode()
    signature = base64.b64encode(hmac.new(
        OSS_ACCESS_KEY_SECRET.encode(), policy.encode(), hashlib.sha1
    ).digest()).decode()
    
    upload_url = f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{key}"
    
    return {
        "token": json.dumps({"key": key, "policy": policy, "signature": signature, "OSSAccessKeyId": OSS_ACCESS_KEY_ID, "success_action_status": "200"}),
        "upload_url": upload_url, "key": key
    }

@router.get("/upload_token")
async def get_upload_token(filename: str = ""):
    result = gen_upload_token(filename)
    return {"code": 0, "data": {"token": result["token"], "upload_url": result["upload_url"], "key": result["key"]}}

PRIVACY_POLICY = "# 方糖Found 隐私政策更新日期：2026年5月5日"

@router.get("/privacy")
async def privacy_policy():
    return {"code": 0, "data": {"title": "方糖Found 隐私政策", "content": PRIVACY_POLICY, "updatedAt": "2026-05-05"}}

@router.get("/terms")
async def terms_of_service():
    return {"code": 0, "data": {"title": "方糖Found 服务条款", "content": "欢迎使用方糖Found！", "updatedAt": "2026-05-05"}}
