from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class DistributionConfig(Base, TimestampMixin):
    """分销全局配置，只有一行数据（不设 site 维度，单站点 MVP）。"""

    __tablename__ = "distribution_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    direct_rate_percent: Mapped[int] = mapped_column(Integer, default=20)  # 一级（直推）返佣比例
    indirect_rate_percent: Mapped[int] = mapped_column(Integer, default=5)  # 二级（间推）返佣比例
    min_withdraw_cents: Mapped[int] = mapped_column(Integer, default=1000)  # 最低提现金额（分）
    max_withdraw_cents: Mapped[int] = mapped_column(Integer, default=500000)  # 单笔最高提现金额（分）
    service_fee_percent: Mapped[int] = mapped_column(Integer, default=0)  # 提现手续费比例


class CommissionLog(Base, TimestampMixin):
    """下级用户支付 VIP/充值订单时，给上级记一笔佣金。"""

    __tablename__ = "commission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # 拿到佣金的分销商
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # 触发消费的下级用户
    level: Mapped[int] = mapped_column(Integer)  # 1=直推 2=间推
    source_amount_cents: Mapped[int] = mapped_column(Integer)  # 触发的订单金额
    commission_cents: Mapped[int] = mapped_column(Integer)  # 本次获得的佣金
    order_type: Mapped[str] = mapped_column(String(20))  # vip / recharge
    order_no: Mapped[str] = mapped_column(String(64))


class WithdrawAccount(Base, TimestampMixin):
    """用户绑定的提现收款账户，一人一条，更新覆盖。"""

    __tablename__ = "withdraw_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    account_type: Mapped[str] = mapped_column(String(10))  # alipay / wechat / bank
    real_name: Mapped[str] = mapped_column(String(64), default="")
    account_no: Mapped[str] = mapped_column(String(64), default="")  # 支付宝账号/银行卡号
    bank_name: Mapped[str] = mapped_column(String(64), default="")  # 开户行，仅 bank 需要
    qr_image: Mapped[str] = mapped_column(String(255), default="")  # 收款码，微信必填


class WithdrawApply(Base, TimestampMixin):
    __tablename__ = "withdraw_applies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)  # 申请提现金额（已从佣金余额扣除）
    fee_cents: Mapped[int] = mapped_column(Integer, default=0)
    actual_cents: Mapped[int] = mapped_column(Integer)  # 实际到账 = amount - fee
    account_type: Mapped[str] = mapped_column(String(10))
    account_snapshot: Mapped[str] = mapped_column(Text)  # 申请时的收款账户信息快照（JSON 字符串）
    status: Mapped[str] = mapped_column(String(10), default="pending")  # pending/paid/rejected
    reject_reason: Mapped[str] = mapped_column(String(255), default="")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
