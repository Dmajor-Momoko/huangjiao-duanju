from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=64)
    sms_code: str = Field(default="", description="预留短信验证码字段，mock 模式下任意值可通过")
    invite_code: str = Field(default="", description="邀请人的邀请码，选填")


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: str
    coins: int
    is_vip: bool
    vip_expire_at: datetime | None
    is_ad_free: bool
    ad_free_expire_at: datetime | None
    is_admin: bool

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
