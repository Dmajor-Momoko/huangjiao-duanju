"""
短信服务抽象层。MockSmsProvider 不会真实发送短信，只把验证码打印到后端日志里，
方便本地联调（注册接口 mock 模式下任意验证码都能通过校验）。

接入阿里云/腾讯云短信时，实现 AliyunSmsProvider / TencentSmsProvider 的 send()，
并把 SMS_PROVIDER 改成 aliyun / tencent，同时把 auth.py 里跳过验证码校验的逻辑替换为真实校验。
"""

import logging
import random
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger("sms")


class SmsProvider(ABC):
    @abstractmethod
    async def send(self, phone: str) -> str:
        """返回发送的验证码（真实服务商通常不会返回验证码本身，这里仅 mock 场景使用）"""
        raise NotImplementedError


class MockSmsProvider(SmsProvider):
    async def send(self, phone: str) -> str:
        code = f"{random.randint(0, 999999):06d}"
        logger.info("【mock短信】发送验证码 %s 给 %s（未真实发送）", code, phone)
        return code


class AliyunSmsProvider(SmsProvider):
    async def send(self, phone: str) -> str:
        raise NotImplementedError(
            "阿里云短信未接入：请在此调用阿里云 SDK，并配置 SMS_ACCESS_KEY_ID / SMS_ACCESS_KEY_SECRET / SMS_SIGN_NAME"
        )


class TencentSmsProvider(SmsProvider):
    async def send(self, phone: str) -> str:
        raise NotImplementedError("腾讯云短信未接入：请在此调用腾讯云 SDK")


def get_sms_provider() -> SmsProvider:
    provider = settings.sms_provider
    if provider == "aliyun":
        return AliyunSmsProvider()
    if provider == "tencent":
        return TencentSmsProvider()
    return MockSmsProvider()
