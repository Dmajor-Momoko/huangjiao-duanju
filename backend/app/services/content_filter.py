from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banned_word import BannedWord


async def find_banned_words(db: AsyncSession, text: str) -> list[str]:
    """简单子串匹配：违禁词表通常是运营手工维护的几十到几百条，子串扫描足够快，
    没必要为此引入 DFA 字典树。"""
    if not text:
        return []
    rows = await db.execute(select(BannedWord.word))
    words = [w for (w,) in rows.all()]
    return [w for w in words if w and w in text]
