from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, SmallInteger, Text, ForeignKey, UniqueConstraint
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class UserLikeMoment(Base):
    __tablename__ = "user_like_moments"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, nullable=False, index=True)
    moment_id = Column(GUID, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        UniqueConstraint('user_id', 'moment_id', name='uix_user_moment_like'),
    )
