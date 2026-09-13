from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.content import Feedback
from app.models.user import User
from app.schemas.content import FeedbackCreateRequest, FeedbackOut
from app.services.content_filter import find_banned_words

router = APIRouter(prefix="/feedback", tags=["意见反馈"])


def _to_out(fb: Feedback) -> FeedbackOut:
    return FeedbackOut(
        id=fb.id,
        content=fb.content,
        contact=fb.contact,
        images=[u for u in fb.images.split(",") if u],
        status=fb.status,
        admin_reply=fb.admin_reply,
        created_at=fb.created_at,
    )


@router.post("", response_model=FeedbackOut)
async def create_feedback(
    payload: FeedbackCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hits = await find_banned_words(db, payload.content)
    if hits:
        raise HTTPException(400, f"内容包含违禁词：{'、'.join(hits)}")

    fb = Feedback(
        user_id=current_user.id,
        content=payload.content,
        contact=payload.contact,
        images=",".join(payload.images),
    )
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return _to_out(fb)


@router.get("/mine", response_model=list[FeedbackOut])
async def my_feedback(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = await db.execute(
        select(Feedback).where(Feedback.user_id == current_user.id).order_by(Feedback.created_at.desc())
    )
    return [_to_out(fb) for fb in rows.scalars().all()]
