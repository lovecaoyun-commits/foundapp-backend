from sqlalchemy import Column, BigInteger, DateTime, String, DECIMAL, SmallInteger, ForeignKey
from app.models.types import GUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class VirtualCurrency(Base):
    __tablename__ = "virtual_currency"
    user_id = Column(GUID, primary_key=True)
    balance = Column(BigInteger, default=0)

class RechargeOrder(Base):
    __tablename__ = "recharge_orders"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, nullable=False)
    amount = Column(DECIMAL(10,2), nullable=False)
    coins = Column(BigInteger, nullable=False)
    status = Column(SmallInteger, default=0)
    pay_channel = Column(String(20))
    trade_no = Column(String(64))
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime)
