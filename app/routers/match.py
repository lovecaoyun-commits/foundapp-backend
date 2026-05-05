from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user_id
from app.models.user import User
from app.models.match import Match
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
import random

router = APIRouter(prefix="/api/match", tags=["匹配"])

@router.get("/recommend")
async def get_recommend(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id != user_id).limit(10).all()
    return {
        "code": 0,
        "data": [{"userId": str(u.id), "nickname": u.nickname, "avatar": u.avatar or "", "gender": u.gender} for u in users]
    }

@router.post("/like/{target_id}")
async def like_user(target_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing = db.query(Match).filter(
        Match.user_a == target_id,
        Match.user_b == user_id,
        Match.user_a_liked == True
    ).first()
    
    record = db.query(Match).filter(Match.user_a == user_id, Match.user_b == target_id).first()
    if not record:
        record = Match(user_a=user_id, user_b=target_id)
        db.add(record)
    
    record.user_a_liked = True
    is_match = False
    if existing or (record.user_b_liked == True):
        try:
            now = db.execute(text("SELECT now()")).fetchone()[0]
            record.matched_at = now
        except:
            pass
        record.status = 1
        is_match = True
    
    db.commit()
    return {"code": 0, "data": {"matched": is_match}}

@router.get("/matches")
async def get_matches(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    matches = db.query(Match).filter(
        ((Match.user_a == user_id) | (Match.user_b == user_id)),
        Match.status == 1
    ).all()
    result = []
    for m in matches:
        peer_id = m.user_b if m.user_a == user_id else m.user_a
        peer = db.query(User).filter(User.id == peer_id).first()
        if peer:
            result.append({"userId": str(peer.id), "nickname": peer.nickname, "avatar": peer.avatar or "", "matchedAt": str(m.matched_at) if m.matched_at else ""})
    return {"code": 0, "data": result}
