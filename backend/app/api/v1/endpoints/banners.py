from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.banner import Banner
from app.schemas.banner import BannerOut

router = APIRouter(prefix="/banners", tags=["首页焦点图"])


@router.get("", response_model=list[BannerOut])
async def list_banners(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(Banner).where(Banner.is_active.is_(True)).order_by(Banner.sort)
    )
    return rows.scalars().all()
