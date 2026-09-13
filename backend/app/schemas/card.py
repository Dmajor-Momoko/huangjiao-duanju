from datetime import datetime

from pydantic import BaseModel


class CardRedeemRequest(BaseModel):
    code: str


class CardRedeemResult(BaseModel):
    card_type: str
    vip_days: int
    coins: int
    balance: int
    vip_expire_at: datetime | None
