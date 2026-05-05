from sqlalchemy import Column, Boolean, DateTime, SmallInteger, Float, ForeignKey
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_a = Column(GUID, nullable=False)
    user_b = Column(GUID, nullable=False)
    user_a_liked = Column(Boolean, nullable=True)
    user_b_liked = Column(Boolean, nullable=True)
    match_score = Column(Float, default=0)
    matched_at = Column(DateTime)
    status = Column(SmallInteger, default=0)
    created_at = Column(DateTime, server_default=func.now())
