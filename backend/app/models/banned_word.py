from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class BannedWord(Base, TimestampMixin):
    """违禁词表，管理员维护。用户提交昵称/反馈等文本时校验，短剧发布时提供人工检测工具。"""

    __tablename__ = "banned_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(64), unique=True, index=True)
