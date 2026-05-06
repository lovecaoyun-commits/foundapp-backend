from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/messages/{match_id}")
async def get_messages(match_id: str, page: int = 1, size: int = 20):
    return {"code": 0, "data": {"messages": [], "total": 0}}

@router.post("/messages/send")
async def send_message(match_id: str, content: str):
    return {"code": 0, "message": "发送成功"}
