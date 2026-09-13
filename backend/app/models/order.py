from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class VipPlan(Base, TimestampMixin):
    __tablename__ = "vip_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    price_cents: Mapped[int] = mapped_column(Integer)  # 人民币分
    duration_days: Mapped[int] = mapped_column(Integer)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class VipOrder(Base, TimestampMixin):
    __tablename__ = "vip_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("vip_plans.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/paid/cancelled
    pay_channel: Mapped[str] = mapped_column(String(20), default="mock")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AdFreePlan(Base, TimestampMixin):
    """免广告会员套餐，和 VIP 套餐是两个独立的商品体系。"""

    __tablename__ = "ad_free_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    price_cents: Mapped[int] = mapped_column(Integer)
    duration_days: Mapped[int] = mapped_column(Integer)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class AdFreeOrder(Base, TimestampMixin):
    __tablename__ = "ad_free_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("ad_free_plans.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    pay_channel: Mapped[str] = mapped_column(String(20), default="mock")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RechargeOrder(Base, TimestampMixin):
    """充值币的订单（真实支付走这里，成功后给用户加 coins）"""

    __tablename__ = "recharge_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    coins: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    pay_channel: Mapped[str] = mapped_column(String(20), default="mock")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WalletLog(Base, TimestampMixin):
    __tablename__ = "wallet_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))  # recharge / consume
    amount: Mapped[int] = mapped_column(Integer)  # 正数增加，负数扣减
    balance_after: Mapped[int] = mapped_column(Integer)
    remark: Mapped[str] = mapped_column(String(255), default="")


class VideoUnlock(Base, TimestampMixin):
    """用户用币解锁全剧的记录"""

    __tablename__ = "video_unlocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
