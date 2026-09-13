from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class StaticPage(Base, TimestampMixin):
    """固定 slug 的富文本页面（用户协议/隐私政策等），管理后台只能编辑内容，不能新增/删除 slug。"""

    __tablename__ = "static_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text, default="")


class Feedback(Base, TimestampMixin):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    contact: Mapped[str] = mapped_column(String(64), default="")
    images: Mapped[str] = mapped_column(Text, default="")  # 逗号分隔的图片 URL
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/replied
    admin_reply: Mapped[str] = mapped_column(Text, default="")
