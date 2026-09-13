from datetime import date

from pydantic import BaseModel


class SignInRuleOut(BaseModel):
    day: int
    coins: int

    class Config:
        from_attributes = True


class SignInDayStatus(BaseModel):
    date: date
    signed: bool
    coins: int | None = None


class SignInStatusOut(BaseModel):
    today_signed: bool
    streak_days: int
    next_cycle_day: int
    rules: list[SignInRuleOut]
    calendar: list[SignInDayStatus]


class SignInResultOut(BaseModel):
    coins_awarded: int
    streak_days: int
    balance: int
