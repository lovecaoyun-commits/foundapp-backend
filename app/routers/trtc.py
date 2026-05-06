from fastapi import APIRouter

router = APIRouter(prefix="/trtc", tags=["trtc"])

@router.post("/sign")
async def get_sign(user_id: str, room_id: str):
    import hashlib
    import time
    sig = hashlib.md5(f"{user_id}:{room_id}:{int(time.time())}".encode()).hexdigest()
    return {"code": 0, "data": {"signature": sig}}
