from datetime import datetime

from pydantic import BaseModel


class DistributionOverviewOut(BaseModel):
    invite_code: str
    direct_count: int
    indirect_count: int
    commission_balance_cents: int
    commission_total_cents: int
    direct_rate_percent: int
    indirect_rate_percent: int


class TeamMemberOut(BaseModel):
    id: int
    nickname: str
    phone: str
    level: int
    joined_at: datetime


class CommissionLogOut(BaseModel):
    id: int
    level: int
    source_amount_cents: int
    commission_cents: int
    order_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class WithdrawAccountOut(BaseModel):
    account_type: str
    real_name: str
    account_no: str
    bank_name: str
    qr_image: str

    class Config:
        from_attributes = True


class WithdrawAccountUpdateRequest(BaseModel):
    account_type: str
    real_name: str
    account_no: str = ""
    bank_name: str = ""
    qr_image: str = ""


class WithdrawRuleOut(BaseModel):
    min_withdraw_cents: int
    max_withdraw_cents: int
    service_fee_percent: int


class WithdrawApplyRequest(BaseModel):
    amount_cents: int


class WithdrawApplyOut(BaseModel):
    order_no: str
    amount_cents: int
    fee_cents: int
    actual_cents: int
    account_type: str
    status: str
    reject_reason: str
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True
