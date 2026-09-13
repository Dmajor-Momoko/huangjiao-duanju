from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(128))
    cover: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    is_online: Mapped[bool] = mapped_column(Boolean, default=True)

    # 前 N 集免费，超出部分需要 VIP 或解锁全剧
    free_episodes: Mapped[int] = mapped_column(Integer, default=3)
    # 解锁全剧所需币数（0 表示只能靠 VIP 观看，不能单独购买）
    unlock_price_coins: Mapped[int] = mapped_column(Integer, default=0)

    episodes: Mapped[list["VideoEpisode"]] = relationship(
        back_populates="video", order_by="VideoEpisode.episode_no", cascade="all, delete-orphan"
    )
    performers: Mapped[list["VideoPerformer"]] = relationship(
        back_populates="video", order_by="VideoPerformer.sort", cascade="all, delete-orphan"
    )
    images: Mapped[list["VideoImage"]] = relationship(
        back_populates="video", order_by="VideoImage.sort", cascade="all, delete-orphan"
    )
    category: Mapped[Category | None] = relationship()


class VideoEpisode(Base, TimestampMixin):
    __tablename__ = "video_episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    episode_no: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(128), default="")
    video_url: Mapped[str] = mapped_column(String(255), default="")
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 秒

    video: Mapped[Video] = relationship(back_populates="episodes")


class VideoPerformer(Base, TimestampMixin):
    __tablename__ = "video_performers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    type: Mapped[str] = mapped_column(String(16), default="performer")  # director / performer
    name: Mapped[str] = mapped_column(String(32))
    avatar: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[str] = mapped_column(String(64), default="")  # 饰演角色，导演可留空
    bio: Mapped[str] = mapped_column(Text, default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)

    video: Mapped[Video] = relationship(back_populates="performers")


class VideoImage(Base, TimestampMixin):
    """剧集壁纸/剧照图集"""

    __tablename__ = "video_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    name: Mapped[str] = mapped_column(String(64), default="")
    image_url: Mapped[str] = mapped_column(String(255))
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)

    video: Mapped[Video] = relationship(back_populates="images")
