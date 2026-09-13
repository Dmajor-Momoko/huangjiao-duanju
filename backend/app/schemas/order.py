from datetime import datetime

from pydantic import BaseModel


class VipPlanOut(BaseModel):
    id: int
    name: str
    price_cents: int
    duration_days: int

    class Config:
        from_attributes = True


class CreateVipOrderRequest(BaseModel):
    plan_id: int


class AdFreePlanOut(BaseModel):
    id: int
    name: str
    price_cents: int
    duration_days: int

    class Config:
        from_attributes = True


class CreateAdFreeOrderRequest(BaseModel):
    plan_id: int


class CreateRechargeOrderRequest(BaseModel):
    amount_cents: int
    coins: int


class OrderOut(BaseModel):
    order_no: str
    status: str
    amount_cents: int
    paid_at: datetime | None

    class Config:
        from_attributes = True


class UnlockVideoRequest(BaseModel):
    video_id: int


class WalletLogOut(BaseModel):
    id: int
    type: str
    amount: int
    balance_after: int
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True
