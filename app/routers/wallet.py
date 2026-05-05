from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth import get_current_user_id
from app.models.transaction import VirtualCurrency, RechargeOrder
from app.database import get_db
import uuid

router = APIRouter(prefix="/api/wallet", tags=["钱包"])

@router.get("/balance")
async def get_balance(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    vc = db.query(VirtualCurrency).filter(VirtualCurrency.user_id == user_id).first()
    balance = vc.balance if vc else 0
    return {"code": 0, "data": {"balance": balance}}

class RechargeRequest(BaseModel):
    amount: float
    coins: int

@router.post("/recharge")
async def create_recharge(req: RechargeRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = RechargeOrder(user_id=user_id, amount=req.amount, coins=req.coins)
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"code": 0, "data": {"orderId": str(order.id), "amount": float(order.amount), "coins": order.coins}}

@router.post("/recharge/notify")
async def recharge_notify(order_id: str, trade_no: str = None, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    order = db.query(RechargeOrder).filter(RechargeOrder.id == order_id).first()
    if not order or order.status != 0:
        return {"code": 1, "message": "订单异常"}
    order.status = 1
    order.trade_no = trade_no
    vc = db.query(VirtualCurrency).filter(VirtualCurrency.user_id == user_id).first()
    if not vc:
        vc = VirtualCurrency(user_id=user_id, balance=0)
        db.add(vc)
    vc.balance += order.coins
    db.commit()
    return {"code": 0}
