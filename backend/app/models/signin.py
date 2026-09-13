from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class SignInRule(Base, TimestampMixin):
    """连续签到第 N 天奖励币数，固定 7 天一个周期，第 8 天起从第 1 天重新计算。"""

    __tablename__ = "signin_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[int] = mapped_column(Integer, unique=True)  # 周期内第几天，1~7
    coins: Mapped[int] = mapped_column(Integer, default=0)


class SignInRecord(Base, TimestampMixin):
    __tablename__ = "signin_records"
    __table_args__ = (UniqueConstraint("user_id", "sign_date", name="uq_signin_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sign_date: Mapped[date] = mapped_column(Date)
    streak_no: Mapped[int] = mapped_column(Integer)  # 累计连续签到天数（不封顶）
    cycle_day: Mapped[int] = mapped_column(Integer)  # 对应 7 天周期中的第几天
    coins_awarded: Mapped[int] = mapped_column(Integer)
