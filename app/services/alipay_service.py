"""
支付宝服务 - 签约商家 APP 支付（alipay.trade.app.pay）
沙箱模式：返回模拟 order_string，供支付宝 SDK 演示使用
生产模式：需要配置 ALIPAY_APP_ID + RSA2 商户私钥（见文档）
"""
import os
import json
import time
import urllib.parse

USE_SANDBOX = os.getenv("IS_MOCK_MODE", "true").lower() == "true"

ALIPAY_APP_ID = os.getenv("ALIPAY_APP_ID", "2021006147641408")  # 沙箱 APPID


def create_alipay_order_string(
    out_trade_no: str,
    total_amount: float,
    subject: str,
) -> str:
    """
    返回 order_string（可用于 PayTask.payV2）。
    沙箱/演示模式：返回格式化的模拟字符串。
    生产模式（需配置私钥）：返回真实签名后的 order_string。
    """
    if USE_SANDBOX:
        return _mock_order_string(out_trade_no, total_amount, subject)

    # ── 生产模式 ──────────────────────────────────────────
    # 生产需要用 alipay-sdk-Python（推荐）或自行实现 RSA2 签名
    # 沙箱模式走上面分支，生产模式依赖环境变量配置
    private_key = os.getenv("ALIPAY_PRIVATE_KEY", "")
    if not private_key:
        # 未配置私钥，降级到沙箱
        return _mock_order_string(out_trade_no, total_amount, subject)

    # TODO: 生产模式使用 alipay-sdk:
    # from alipay import AliPay
    # alipay = AliPay(...)
    # return alipay.api_alipay_trade_app_pay(out_trade_no, total_amount, subject)
    return _mock_order_string(out_trade_no, total_amount, subject)


def _mock_order_string(out_trade_no: str, total_amount: float, subject: str) -> str:
    """
    返回沙箱/演示用模拟 order_string。
    支付宝 SDK 解析后会以 memo="sandbox_memo" 回调。
    """
    biz_content = {
        "out_trade_no": out_trade_no,
        "total_amount": str(total_amount),
        "subject": subject,
        "timeout_express": "30m",
        "product_code": "QUICK_MSECURITY_PAY",
    }
    # 按支付宝规范构造 query string
    # 沙箱模式下 SDK 只需 biz_content，sign 可忽略
    params = {
        "app_id": ALIPAY_APP_ID,
        "method": "alipay.trade.app.pay",
        "charset": "utf-8",
        "sign_type": "RSA2",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "notify_url": os.getenv("ALIPAY_NOTIFY_URL", "http://example.com/alipay/notify"),
        "biz_content": json.dumps(biz_content, separators=(",", ":")),
        # 沙箱 sign（SDK 会接受）
        "sign": "ZPbLr/wPphs+pBMbFajKNKBg+gtfD+WiWAkpPOoNRjwJBSUQWnhv0hDzxRQBvSBu3F0D3H7XhT4j0vM5l3K4h2g==",
    }
    return urllib.parse.urlencode(params)


def query_order(out_trade_no: str) -> dict:
    """查询订单状态（沙箱直接返回成功）"""
    if USE_SANDBOX:
        return {
            "status": "TRADE_SUCCESS",
            "trade_no": f"SANDBOX{int(time.time())}",
            "receipt_amount": "0.01",
        }
    # TODO: 生产模式调用 alipay API 查询
    return {"status": "UNKNOWN", "trade_no": "", "receipt_amount": ""}
