from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["utils"])

@router.get("/privacy")
async def privacy_policy():
    return {
        "code": 0,
        "data": {
            "title": "方糖Found 隐私政策",
            "content": "# 方糖Found 隐私政策\n\n更新日期：2026年5月5日\n\n## 1. 信息收集\n方糖Found会在您注册、使用服务时收集：身份信息（手机号码）、profile信息（昵称、头像、简介、兴趣标签）、聊天内容、媒体文件、位置信息、设备信息。\n\n## 2. 信息使用\n用于提供、维护和改进服务；昵称、头像、动态内容对其他用户可见；手机号用于账号安全。\n\n## 3. 信息共享\n不会出售个人信息，仅在获得同意/法律要求/保护权利时共享。\n\n## 4. 信息安全\n采用行业标准安全措施，HTTPS加密传输，符合等保要求。\n\n## 5. 您的权利\n随时查看编辑资料；注销后30天内删除数据；疑问联系：support@found.app\n\n## 6. 未成年人保护\n服务不对18岁以下未成年人提供。\n\n## 7. 政策变更\n更新后App内公告通知。\n\n联系：support@found.app",
            "updatedAt": "2026-05-05"
        }
    }

@router.get("/terms")
async def terms_of_service():
    return {
        "code": 0,
        "data": {
            "title": "方糖Found 服务条款",
            "content": "欢迎使用方糖Found！\n\n1. 须年满18岁方可使用\n2. 承诺个人信息真实有效\n3. 遵守法律，不进行违法活动\n4. 尊重他人，不骚扰/诈骗\n5. 方糖Found有权终止违规账号\n6. 风险由用户自行承担\n\n疑问联系：support@found.app",
            "updatedAt": "2026-05-05"
        }
    }
