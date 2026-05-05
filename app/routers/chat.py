from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth import get_current_user_id
from app.models.message import Message
from app.models.user import User
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["聊天"])

class SendMessageRequest(BaseModel):
    receiverId: str
    content: str
    msgType: int = 1
    attachmentUrl: str = ""

@router.get("/conversations")
async def get_conversations(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    sent = db.query(Message.receiver_id).filter(Message.sender_id == user_id).distinct()
    received = db.query(Message.sender_id).filter(Message.receiver_id == user_id).distinct()
    peer_ids = set([str(p[0]) for p in sent.union(received).all()])
    
    conversations = []
    for pid in peer_ids:
        last_msg = db.query(Message).filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == pid)) |
            ((Message.sender_id == pid) & (Message.receiver_id == user_id))
        ).order_by(Message.created_at.desc()).first()
        peer = db.query(User).filter(User.id == pid).first()
        if peer and last_msg:
            conversations.append({
                "peerId": pid,
                "nickname": peer.nickname,
                "avatar": peer.avatar or "",
                "lastMessage": last_msg.content,
                "lastTime": str(last_msg.created_at)
            })
    return {"code": 0, "data": conversations}

@router.get("/messages/{peer_id}")
async def get_messages(peer_id: str, limit: int = Query(50, le=100), before: str = None, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    q = db.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == peer_id)) |
        ((Message.sender_id == peer_id) & (Message.receiver_id == user_id))
    )
    if before:
        q = q.filter(Message.created_at < datetime.fromisoformat(before))
    msgs = q.order_by(Message.created_at.desc()).limit(limit).all()
    return {
        "code": 0,
        "data": [{
            "id": str(m.id),
            "senderId": str(m.sender_id),
            "receiverId": str(m.receiver_id),
            "content": m.content,
            "msgType": m.msg_type,
            "attachmentUrl": m.attachment_url or "",
            "createdAt": str(m.created_at)
        } for m in reversed(msgs)]
    }

@router.post("/messages/send")
async def send_message(req: SendMessageRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    msg = Message(sender_id=user_id, receiver_id=req.receiverId, content=req.content, msg_type=req.msgType, attachment_url=req.attachmentUrl)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "code": 0,
        "data": {
            "id": str(msg.id),
            "senderId": str(msg.sender_id),
            "receiverId": str(msg.receiver_id),
            "content": msg.content,
            "msgType": msg.msg_type,
            "attachmentUrl": msg.attachment_url or "",
            "createdAt": str(msg.created_at)
        }
    }
