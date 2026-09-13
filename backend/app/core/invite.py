import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 去掉易混淆的 0/O/1/I/L


async def generate_invite_code(db: AsyncSession) -> str:
    for _ in range(20):
        code = "".join(random.choices(_ALPHABET, k=6))
        exists = await db.scalar(select(User.id).where(User.invite_code == code))
        if not exists:
            return code
    raise RuntimeError("生成邀请码失败，请重试")
