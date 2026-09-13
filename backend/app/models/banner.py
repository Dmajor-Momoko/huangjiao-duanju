from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Banner(Base, TimestampMixin):
    """首页焦点图轮播。link_url 为空则点击无反应；以 / 开头按站内路由跳转，否则当作外部链接新开页签。"""

    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), default="")
    image_url: Mapped[str] = mapped_column(String(255))
    link_url: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
