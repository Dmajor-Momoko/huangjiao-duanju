from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.invite import generate_invite_code
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse
from app.services.sms import get_sms_provider

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/sms-code")
async def send_sms_code(phone: str):
    """发送短信验证码（mock 模式下验证码会打印在后端日志中，不会真实发送）"""
    provider = get_sms_provider()
    await provider.send(phone)
    return {"message": "发送成功" if settings.sms_provider != "mock" else "已发送（mock，看后端日志）"}


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if settings.sms_provider != "mock" and not payload.sms_code:
        raise HTTPException(400, "请填写短信验证码")

    exists = await db.scalar(select(User).where(User.phone == payload.phone))
    if exists:
        raise HTTPException(400, "该手机号已注册")

    referred_by_id = None
    if payload.invite_code:
        referrer = await db.scalar(select(User).where(User.invite_code == payload.invite_code.upper()))
        if not referrer:
            raise HTTPException(400, "邀请码无效")
        referred_by_id = referrer.id

    invite_code = await generate_invite_code(db)
    user = User(
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        invite_code=invite_code,
        referred_by_id=referred_by_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.phone == payload.phone))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(400, "手机号或密码错误")

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
