"""
支付服务抽象层。

当前仅实现 MockPaymentProvider：创建订单后立即视为支付成功，方便本地开发和联调，
不会产生任何真实资金变动。

接入真实微信支付/支付宝时，实现 WechatPayProvider / AlipayProvider 里的 charge()，
并在 .env 把 PAYMENT_PROVIDER 改成 wechat / alipay，同时补一个接收异步回调通知的路由。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    message: str = ""


class PaymentProvider(ABC):
    @abstractmethod
    async def charge(self, order_no: str, amount_cents: int) -> PaymentResult:
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    async def charge(self, order_no: str, amount_cents: int) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=f"MOCK-{order_no}", message="mock 支付自动成功")


class WechatPayProvider(PaymentProvider):
    async def charge(self, order_no: str, amount_cents: int) -> PaymentResult:
        raise NotImplementedError(
            "微信支付未接入：请在此实现统一下单 + 回调验签逻辑，并配置 WECHAT_PAY_MCH_ID / WECHAT_PAY_API_KEY"
        )


class AlipayProvider(PaymentProvider):
    async def charge(self, order_no: str, amount_cents: int) -> PaymentResult:
        raise NotImplementedError(
            "支付宝未接入：请在此实现统一下单 + 回调验签逻辑，并配置 ALIPAY_APP_ID / ALIPAY_PRIVATE_KEY"
        )


def get_payment_provider() -> PaymentProvider:
    provider = settings.payment_provider
    if provider == "wechat":
        return WechatPayProvider()
    if provider == "alipay":
        return AlipayProvider()
    return MockPaymentProvider()
