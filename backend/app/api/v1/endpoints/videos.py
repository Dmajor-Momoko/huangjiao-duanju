from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.interaction import Favorite, WatchHistory
from app.models.order import VideoUnlock
from app.models.user import User
from app.models.video import Category, Video, VideoImage
from app.schemas.video import CategoryOut, EpisodeOut, VideoDetailOut, VideoImageOut, VideoListItem

router = APIRouter(prefix="/videos", tags=["短剧"])


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Category).order_by(Category.sort))
    return rows.scalars().all()


@router.get("", response_model=list[VideoListItem])
async def list_videos(
    category_id: int | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Video).where(Video.is_online.is_(True)).options(selectinload(Video.episodes))
    if category_id:
        stmt = stmt.where(Video.category_id == category_id)
    if keyword:
        stmt = stmt.where(Video.title.contains(keyword))
    rows = await db.execute(stmt.order_by(Video.created_at.desc()))
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


async def _is_unlocked(db: AsyncSession, user: User | None, video: Video) -> bool:
    if user is None:
        return False
    if user.vip_active():
        return True
    unlock = await db.scalar(
        select(VideoUnlock).where(VideoUnlock.user_id == user.id, VideoUnlock.video_id == video.id)
    )
    return unlock is not None


@router.get("/{video_id}", response_model=VideoDetailOut)
async def get_video_detail(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    video = await db.get(
        Video,
        video_id,
        options=[selectinload(Video.episodes), selectinload(Video.category), selectinload(Video.performers)],
    )
    if not video or not video.is_online:
        raise HTTPException(404, "短剧不存在")

    unlocked = await _is_unlocked(db, current_user, video)
    is_favorite = False
    if current_user:
        fav = await db.scalar(
            select(Favorite).where(Favorite.user_id == current_user.id, Favorite.video_id == video.id)
        )
        is_favorite = fav is not None

    episodes = []
    for ep in video.episodes:
        locked = ep.episode_no > video.free_episodes and not unlocked
        episodes.append(
            EpisodeOut(
                id=ep.id,
                episode_no=ep.episode_no,
                title=ep.title,
                duration=ep.duration,
                locked=locked,
                video_url=None if locked else ep.video_url,
            )
        )

    return VideoDetailOut(
        id=video.id,
        title=video.title,
        cover=video.cover,
        description=video.description,
        category=video.category,
        free_episodes=video.free_episodes,
        unlock_price_coins=video.unlock_price_coins,
        is_unlocked=unlocked,
        is_favorite=is_favorite,
        episodes=episodes,
        performers=video.performers,
    )


@router.get("/{video_id}/images", response_model=list[VideoImageOut])
async def list_video_images(video_id: int, db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(VideoImage).where(VideoImage.video_id == video_id).order_by(VideoImage.sort)
    )
    return rows.scalars().all()


@router.post("/{video_id}/images/{image_id}/download")
async def download_video_image(video_id: int, image_id: int, db: AsyncSession = Depends(get_db)):
    image = await db.scalar(
        select(VideoImage).where(VideoImage.id == image_id, VideoImage.video_id == video_id)
    )
    if not image:
        raise HTTPException(404, "图片不存在")
    image.downloads += 1
    db.add(image)
    await db.commit()
    return {"downloads": image.downloads}


@router.post("/{video_id}/favorite")
async def toggle_favorite(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")

    fav = await db.scalar(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.video_id == video_id)
    )
    if fav:
        await db.delete(fav)
        await db.commit()
        return {"is_favorite": False}

    db.add(Favorite(user_id=current_user.id, video_id=video_id))
    await db.commit()
    return {"is_favorite": True}


@router.post("/{video_id}/episodes/{episode_no}/progress")
async def report_progress(
    video_id: int,
    episode_no: int,
    progress_seconds: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """播放页周期上报观看进度，用于「追剧」页的观看记录"""
    history = await db.scalar(
        select(WatchHistory).where(WatchHistory.user_id == current_user.id, WatchHistory.video_id == video_id)
    )
    if history:
        history.episode_no = episode_no
        history.progress_seconds = progress_seconds
    else:
        history = WatchHistory(
            user_id=current_user.id,
            video_id=video_id,
            episode_no=episode_no,
            progress_seconds=progress_seconds,
        )
    db.add(history)
    await db.commit()
    return {"message": "ok"}
