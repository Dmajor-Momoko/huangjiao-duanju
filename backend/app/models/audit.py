from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class AdminActionLog(Base, TimestampMixin):
    """管理员敏感操作审计日志：账号权限变更、资金相关操作（余额调整/提现审核/卡密批量生成）。
    不记录常规内容 CRUD（短剧/分集等），那些已有 updated_at 时间戳可追溯，逐条记录价值有限。"""

    __tablename__ = "admin_action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    admin_phone: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text, default="")
