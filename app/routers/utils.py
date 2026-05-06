from fastapi import APIRouter, HTTPException
import hmac, hashlib, base64, json, time, uuid
from datetime import datetime

router = APIRouter(prefix="/v1", tags=["utils"])

PRIVACY_POLICY = """
# 方糖Found 隐私政策

更新日期：2026年5月5日

## 1. 信息收集
方糖Found会在您注册、使用服务时收集以下信息：
- **身份信息**：手机号码（用于注册和登录）
- **profile信息**：昵称、头像、个人简介、兴趣爱好标签
- **聊天内容**：您与他人的聊天记录（仅存储在加密服务器上）
- **媒体文件**：您上传的图片、语音、视频
- **位置信息**：附近的人功能需要位置权限（可选）
- **设备信息**：设备型号、操作系统版本、网络类型

## 2. 信息使用
- 提供、维护和改进我们的服务
- 您的昵称、头像、动态内容会对其他用户可见
- 手机号码用于账号安全和身份验证
- 分析用户行为以优化产品体验

## 3. 信息共享
- 不会出售您的个人信息
- 仅在以下情况下共享：（a）获得您同意；（b）法律法规要求；（c）保护方糖Found或用户的权利和安全

## 4. 信息安全
- 采用行业标准安全措施保护您的数据
- 数据传输全程加密（HTTPS）
- 服务器部署在国内主流云平台，符合等保要求

## 5. 您的权利
- 随时查看和编辑您的个人资料
- 注销账号后，我们会在30天内删除您的个人信息（法律法规另有规定的除外）
- 对隐私政策有任何疑问，请联系：support@found.app

## 6. 未成年人保护
- 方糖Found不向18岁以下未成年人提供服务
- 如果您未满18岁，请勿使用本服务

## 7. 政策变更
我们可能会不时更新本隐私政策。更新后会在App内公告或通过短信通知。

方糖Found 运营团队
联系方式：support@found.app
"""

@router.get("/privacy")
async def privacy_policy():
    return {
        "code": 0,
        "data": {
            "title": "方糖Found 隐私政策",
            "content": PRIVACY_POLICY,
            "updatedAt": "2026-05-05"
        }
    }

@router.get("/terms")
async def terms_of_service():
    return {
        "code": 0,
        "data": {
            "title": "方糖Found 服务条款",
            "content": """
方糖Found 服务条款

欢迎使用方糖Found！

使用本服务即表示您同意以下条款：

1. 您须年满18岁方可使用本服务
2. 您承诺提供的个人信息真实有效
3. 请遵守当地法律法规，不要在平台上进行任何违法活动
4. 尊重其他用户，不要进行骚扰、诈骗或其他不当行为
5. 方糖Found有权在不通知的情况下终止违规账号
6. 因使用本服务产生的任何风险由用户自行承担

如有疑问请联系：support@found.app
            """.strip(),
            "updatedAt": "2026-05-05"
        }
    }
