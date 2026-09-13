from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class CardCode(Base, TimestampMixin):
    """卡密：管理后台批量生成，用户输入兑换 VIP 天数或币，一码只能用一次。"""

    __tablename__ = "card_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    batch_no: Mapped[str] = mapped_column(String(32), index=True)
    card_type: Mapped[str] = mapped_column(String(10))  # vip / coins
    vip_days: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(10), default="unused")  # unused / used
    expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remark: Mapped[str] = mapped_column(String(255), default="")
    used_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
