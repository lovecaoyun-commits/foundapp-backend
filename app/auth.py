from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import DecodeError as JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

def create_access_token(user_id: str, phone: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "phone": phone, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效或已过期")

async def get_current_user_id(cred: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = decode_token(cred.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="token不匹配")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="token失效")
    return user_id

def require_auth(user_id: str = Depends(get_current_user_id)) -> str:
    return user_id

async def get_current_user_id_optional(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> str:
    """Optional version: returns empty string if no token provided."""
    if cred is None:
        return ""
    try:
        payload = decode_token(cred.credentials)
        return payload.get("sub", "")
    except Exception:
        return ""
