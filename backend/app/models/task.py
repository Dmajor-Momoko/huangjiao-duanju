from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class TaskDefinition(Base, TimestampMixin):
    """积分任务定义。当前完成方式都是前端点击「去完成」立即到账（mock），
    code 字段预留给以后接入真实行为（比如广告 SDK 回调、分享回调）时做匹配。"""

    __tablename__ = "task_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    reward_coins: Mapped[int] = mapped_column(Integer, default=0)
    task_type: Mapped[str] = mapped_column(String(10), default="daily")  # daily / once
    daily_limit: Mapped[int] = mapped_column(Integer, default=1)  # task_type=daily 时，每天最多可完成次数
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class TaskCompletion(Base, TimestampMixin):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("task_definitions.id"))
    completed_on: Mapped[date] = mapped_column(Date)
