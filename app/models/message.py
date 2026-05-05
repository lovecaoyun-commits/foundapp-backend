from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, SmallInteger, ForeignKey
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    sender_id = Column(GUID, nullable=False, index=True)
    receiver_id = Column(GUID, nullable=False, index=True)
    content = Column(Text, nullable=False)
    msg_type = Column(SmallInteger, default=1)
    attachment_url = Column(String(512), default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
