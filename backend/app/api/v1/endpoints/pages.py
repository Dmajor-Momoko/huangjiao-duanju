from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.content import StaticPage
from app.schemas.content import StaticPageListItem, StaticPageOut

router = APIRouter(prefix="/pages", tags=["帮助页面"])


@router.get("", response_model=list[StaticPageListItem])
async def list_pages(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(StaticPage).order_by(StaticPage.id))
    return rows.scalars().all()


@router.get("/{slug}", response_model=StaticPageOut)
async def get_page(slug: str, db: AsyncSession = Depends(get_db)):
    page = await db.scalar(select(StaticPage).where(StaticPage.slug == slug))
    if not page:
        raise HTTPException(404, "页面不存在")
    return page
