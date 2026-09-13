from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Favorite(Base, TimestampMixin):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uq_favorite_user_video"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))


class WatchHistory(Base, TimestampMixin):
    __tablename__ = "watch_history"
    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uq_history_user_video"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    episode_no: Mapped[int] = mapped_column(Integer, default=1)
    progress_seconds: Mapped[int] = mapped_column(Integer, default=0)
