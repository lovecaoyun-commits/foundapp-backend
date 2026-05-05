from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, SmallInteger
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(128))
    nickname = Column(String(50), nullable=False)
    avatar = Column(String(512), default="")
    gender = Column(SmallInteger, default=0)
    city = Column(String(50), default="")
    bio = Column(Text, default="")
    tags = Column(Text, default=[])
    is_vip = Column(Boolean, default=False)
    vip_expire = Column(DateTime, nullable=True)
    last_active = Column(DateTime, server_default=func.now())
    invite_code = Column(String(32), default="")
    created_at = Column(DateTime, server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, unique=True)
    prefer_gender = Column(SmallInteger, default=0)
    prefer_age_min = Column(SmallInteger, default=18)
    prefer_age_max = Column(SmallInteger, default=50)
    prefer_city = Column(String(50), default="")
    prefer_tags = Column(Text, default=[])
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
