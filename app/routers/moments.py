from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth import get_current_user_id
from app.models.moment import Moment
from app.models.liked_moment import UserLikeMoment
from app.models.user import User
from app.database import get_db

router = APIRouter(prefix="/api/moments", tags=["动态"])

@router.get("/feed")
async def get_feed(page: int = 1, size: int = 20, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    offset = (page - 1) * size
    moments = db.query(Moment).filter(Moment.status == 0).order_by(Moment.created_at.desc()).offset(offset).limit(size).all()
    
    liked_ids = set()
    if moments:
        moment_ids = [m.id for m in moments]
        liked = db.query(UserLikeMoment).filter(UserLikeMoment.user_id == user_id, UserLikeMoment.moment_id.in_(moment_ids)).all()
        liked_ids = {l.moment_id for l in liked}
    
    result = []
    for m in moments:
        author = db.query(User).filter(User.id == m.user_id).first()
        if author:
            result.append({
                "id": str(m.id),
                "userId": str(m.user_id),
                "nickname": author.nickname,
                "avatar": author.avatar or "",
                "content": m.content,
                "images": m.images or [],
                "likesCount": m.likes_count,
                "commentsCount": m.comments_count,
                "isLiked": m.id in liked_ids,
                "createdAt": str(m.created_at)
            })
    return {"code": 0, "data": result}

class PublishRequest(BaseModel):
    content: str
    images: list = []

@router.post("")
async def publish(req: PublishRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    moment = Moment(user_id=user_id, content=req.content, images=req.images)
    db.add(moment)
    db.commit()
    db.refresh(moment)
    return {"code": 0, "data": {"id": str(moment.id)}}

@router.post("/{moment_id}/like")
async def like_moment(moment_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    moment = db.query(Moment).filter(Moment.id == moment_id, Moment.status == 0).first()
    if not moment:
        raise HTTPException(status_code=404, detail="动态不存在")
    existing = db.query(UserLikeMoment).filter(UserLikeMoment.user_id == user_id, UserLikeMoment.moment_id == moment_id).first()
    if not existing:
        like = UserLikeMoment(user_id=user_id, moment_id=moment_id)
        db.add(like)
        moment.likes_count = moment.likes_count + 1
        db.commit()
    return {"code": 0}

@router.delete("/{moment_id}/like")
async def unlike_moment(moment_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing = db.query(UserLikeMoment).filter(UserLikeMoment.user_id == user_id, UserLikeMoment.moment_id == moment_id).first()
    if existing:
        db.delete(existing)
        moment = db.query(Moment).filter(Moment.id == moment_id, Moment.status == 0).first()
        if moment and moment.likes_count > 0:
            moment.likes_count = moment.likes_count - 1
        db.commit()
    return {"code": 0}

@router.delete("/{moment_id}")
async def delete_moment(moment_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    moment = db.query(Moment).filter(Moment.id == moment_id, Moment.user_id == user_id).first()
    if not moment:
        raise HTTPException(status_code=404, detail="动态不存在或无权删除")
    moment.status = 2
    db.commit()
    return {"code": 0}
