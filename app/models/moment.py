from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, Text, SmallInteger, ForeignKey
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Moment(Base):
    __tablename__ = "moments"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, nullable=False, index=True)
    content = Column(Text, nullable=False)
    images = Column(Text, default=[])
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    status = Column(SmallInteger, default=0)
    created_at = Column(DateTime, server_default=func.now())
