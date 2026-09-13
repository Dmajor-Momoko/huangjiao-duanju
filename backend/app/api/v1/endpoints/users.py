from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.interaction import Favorite, WatchHistory
from app.models.order import WalletLog
from app.models.user import User
from app.models.video import Video
from app.schemas.order import WalletLogOut
from app.schemas.user import UserOut, UserUpdateRequest
from app.schemas.video import VideoListItem
from app.services.content_filter import find_banned_words

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.nickname is not None:
        hits = await find_banned_words(db, payload.nickname)
        if hits:
            raise HTTPException(400, f"昵称包含违禁词：{'、'.join(hits)}")
        current_user.nickname = payload.nickname
    if payload.avatar is not None:
        current_user.avatar = payload.avatar
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/favorites", response_model=list[VideoListItem])
async def my_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(Video)
        .join(Favorite, Favorite.video_id == Video.id)
        .where(Favorite.user_id == current_user.id)
        .options(selectinload(Video.episodes))
        .order_by(Favorite.created_at.desc())
    )
    videos = rows.scalars().all()
    return [
        VideoListItem(
            id=v.id,
            title=v.title,
            cover=v.cover,
            category_id=v.category_id,
            total_episodes=len(v.episodes),
        )
        for v in videos
    ]


@router.get("/me/history", response_model=list[VideoListItem])
async def my_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(Video)
        .join(WatchHistory, WatchHistory.video_id == Video.id)
        .where(WatchHistory.user_id == current_user.id)
        .options(selectinload(Video.episodes))
        .order_by(WatchHistory.updated_at.desc())
    )
    videos = rows.scalars().all()
    return [
        VideoListItem(
            id=v.id,
            title=v.title,
            cover=v.cover,
            category_id=v.category_id,
            total_episodes=len(v.episodes),
        )
        for v in videos
    ]


@router.get("/me/wallet-logs", response_model=list[WalletLogOut])
async def my_wallet_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(WalletLog).where(WalletLog.user_id == current_user.id).order_by(WalletLog.created_at.desc())
    )
    return rows.scalars().all()
