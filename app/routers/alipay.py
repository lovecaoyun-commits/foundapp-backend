"""
支付宝 APP 支付 API
POST /v1/alipay/create - 创建订单，返回 order_string（可调起支付宝 SDK）
POST /v1/alipay/notify  - 支付宝异步回调通知
GET  /v1/alipay/query   - 查询订单状态
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
import time

from app.auth import get_current_user_id_optional
from app.services.alipay_service import create_alipay_order_string, query_order

router = APIRouter(prefix="/v1/alipay", tags=["支付宝"])


class AlipayCreateRequest(BaseModel):
    out_trade_no: str          # 商户订单号
    total_amount: float         # 金额（元）
    subject: str               # 商品标题
    plan_id: Optional[str] = None  # 会员计划 ID（可选，用于记录）


class AlipayCreateResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]


@router.post("/create", response_model=AlipayCreateResponse)
async def alipay_create(
    req: AlipayCreateRequest,
    user_id: str = Depends(get_current_user_id_optional)
):
    """
    创建支付宝订单，返回 order_string。
    前端用 PayTask.payV2(order_string, callback) 调起支付宝。
    """
    order_string = create_alipay_order_string(
        out_trade_no=req.out_trade_no,
        total_amount=req.total_amount,
        subject=req.subject,
    )

    if order_string is None:
        return AlipayCreateResponse(
            code=1,
            message="创建订单失败",
            data=None
        )

    return AlipayCreateResponse(
        code=0,
        message="success",
        data={
            "order_string": order_string,
            "out_trade_no": req.out_trade_no,
        }
    )


@router.get("/query", response_model=AlipayCreateResponse)
async def alipay_query(
    out_trade_no: str = Query(..., description="商户订单号"),
    user_id: str = Depends(get_current_user_id_optional)
):
    """查询订单状态（沙箱模式直接返回成功）"""
    result = query_order(out_trade_no)
    if result is None:
        return AlipayCreateResponse(code=1, message="查询失败", data=None)

    return AlipayCreateResponse(
        code=0,
        message="success",
        data=result
    )


@router.post("/notify")
async def alipay_notify():
    """
    支付宝异步回调。
    注意：生产环境必须验签，本实现为沙箱/演示版本。
    """
    # TODO: 生产环境需要：
    # 1. 解析 POST body（application/x-www-form-urlencoded）
    # 2. 提取 sign 参数并验证签名（verify_alipay_callback）
    # 3. 验证 out_trade_no、total_amount 等
    # 4. 根据 trade_status 更新订单状态
    # 5. 返回 "success" + "end" 格式给支付宝
    return {"code": "success", "msg": "ok"}
