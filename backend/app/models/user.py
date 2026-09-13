from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(64), default="短剧用户")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    password_hash: Mapped[str] = mapped_column(String(255))

    # 钱包余额，单位：币（充值/消费剧集用）
    coins: Mapped[int] = mapped_column(Integer, default=0)

    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 免广告会员：和 VIP 是两个独立的付费产品，VIP 到期后广告位可能重新出现
    is_ad_free: Mapped[bool] = mapped_column(Boolean, default=False)
    ad_free_expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---- 分销 ----
    invite_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    referred_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # 佣金余额（分），可提现；累计佣金（分）仅用于展示，提现不扣减
    commission_balance_cents: Mapped[int] = mapped_column(Integer, default=0)
    commission_total_cents: Mapped[int] = mapped_column(Integer, default=0)

    def vip_active(self) -> bool:
        from app.models.mixins import utcnow

        if not self.is_vip or self.vip_expire_at is None:
            return False
        return self.vip_expire_at > utcnow()

    def ad_free_active(self) -> bool:
        from app.models.mixins import utcnow

        if not self.is_ad_free or self.ad_free_expire_at is None:
            return False
        return self.ad_free_expire_at > utcnow()
