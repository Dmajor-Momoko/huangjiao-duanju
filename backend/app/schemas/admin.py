from datetime import datetime

from pydantic import BaseModel


# ---- 分类 ----
class CategoryCreateRequest(BaseModel):
    name: str
    sort: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = None
    sort: int | None = None


# ---- 分集 ----
class EpisodeAdminOut(BaseModel):
    id: int
    episode_no: int
    title: str
    video_url: str
    duration: int

    class Config:
        from_attributes = True


class EpisodeCreateRequest(BaseModel):
    episode_no: int
    title: str = ""
    video_url: str = ""
    duration: int = 0


class EpisodeUpdateRequest(BaseModel):
    episode_no: int | None = None
    title: str | None = None
    video_url: str | None = None
    duration: int | None = None


# ---- 演员/演职员 ----
class PerformerAdminOut(BaseModel):
    id: int
    type: str
    name: str
    avatar: str
    role: str
    bio: str
    sort: int

    class Config:
        from_attributes = True


class PerformerCreateRequest(BaseModel):
    type: str = "performer"
    name: str
    avatar: str = ""
    role: str = ""
    bio: str = ""
    sort: int = 0


class PerformerUpdateRequest(BaseModel):
    type: str | None = None
    name: str | None = None
    avatar: str | None = None
    role: str | None = None
    bio: str | None = None
    sort: int | None = None


# ---- 壁纸图集 ----
class VideoImageAdminOut(BaseModel):
    id: int
    name: str
    image_url: str
    downloads: int
    sort: int

    class Config:
        from_attributes = True


class VideoImageCreateRequest(BaseModel):
    name: str = ""
    image_url: str
    sort: int = 0


class VideoImageUpdateRequest(BaseModel):
    name: str | None = None
    image_url: str | None = None
    sort: int | None = None


# ---- 短剧 ----
class VideoAdminOut(BaseModel):
    id: int
    title: str
    cover: str
    description: str
    category_id: int | None
    is_online: bool
    free_episodes: int
    unlock_price_coins: int
    episodes: list[EpisodeAdminOut]
    performers: list[PerformerAdminOut]
    images: list[VideoImageAdminOut]

    class Config:
        from_attributes = True


class VideoListAdminOut(BaseModel):
    id: int
    title: str
    cover: str
    category_id: int | None
    is_online: bool
    episode_count: int

    class Config:
        from_attributes = True


class VideoCreateRequest(BaseModel):
    title: str
    cover: str = ""
    description: str = ""
    category_id: int | None = None
    free_episodes: int = 3
    unlock_price_coins: int = 0
    is_online: bool = True


class VideoUpdateRequest(BaseModel):
    title: str | None = None
    cover: str | None = None
    description: str | None = None
    category_id: int | None = None
    free_episodes: int | None = None
    unlock_price_coins: int | None = None
    is_online: bool | None = None


# ---- VIP 套餐 ----
class VipPlanAdminOut(BaseModel):
    id: int
    name: str
    price_cents: int
    duration_days: int
    sort: int

    class Config:
        from_attributes = True


class VipPlanCreateRequest(BaseModel):
    name: str
    price_cents: int
    duration_days: int
    sort: int = 0


class VipPlanUpdateRequest(BaseModel):
    name: str | None = None
    price_cents: int | None = None
    duration_days: int | None = None
    sort: int | None = None


# ---- 免广告套餐 ----
class AdFreePlanAdminOut(BaseModel):
    id: int
    name: str
    price_cents: int
    duration_days: int
    sort: int

    class Config:
        from_attributes = True


class AdFreePlanCreateRequest(BaseModel):
    name: str
    price_cents: int
    duration_days: int
    sort: int = 0


class AdFreePlanUpdateRequest(BaseModel):
    name: str | None = None
    price_cents: int | None = None
    duration_days: int | None = None
    sort: int | None = None


class AdFreeOrderAdminOut(BaseModel):
    order_no: str
    user_phone: str
    plan_name: str
    amount_cents: int
    status: str
    paid_at: datetime | None
    created_at: datetime


# ---- 用户 ----
class UserAdminOut(BaseModel):
    id: int
    phone: str
    nickname: str
    coins: int
    is_vip: bool
    vip_expire_at: datetime | None
    is_ad_free: bool
    ad_free_expire_at: datetime | None
    is_admin: bool
    invite_code: str
    commission_balance_cents: int
    commission_total_cents: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserAdjustRequest(BaseModel):
    coins_delta: int = 0
    extend_vip_days: int = 0
    extend_ad_free_days: int = 0
    remark: str = "管理员调整"


# ---- 订单 ----
class VipOrderAdminOut(BaseModel):
    order_no: str
    user_phone: str
    plan_name: str
    amount_cents: int
    status: str
    paid_at: datetime | None
    created_at: datetime


class RechargeOrderAdminOut(BaseModel):
    order_no: str
    user_phone: str
    amount_cents: int
    coins: int
    status: str
    paid_at: datetime | None
    created_at: datetime


# ---- 签到规则 ----
class SignInRuleAdminOut(BaseModel):
    day: int
    coins: int

    class Config:
        from_attributes = True


class SignInRuleUpdateRequest(BaseModel):
    coins: int


# ---- 积分任务 ----
class TaskAdminOut(BaseModel):
    id: int
    code: str
    title: str
    description: str
    reward_coins: int
    task_type: str
    daily_limit: int
    is_active: bool
    sort: int

    class Config:
        from_attributes = True


class TaskCreateRequest(BaseModel):
    code: str
    title: str
    description: str = ""
    reward_coins: int = 0
    task_type: str = "daily"
    daily_limit: int = 1
    is_active: bool = True
    sort: int = 0


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    reward_coins: int | None = None
    task_type: str | None = None
    daily_limit: int | None = None
    is_active: bool | None = None
    sort: int | None = None


# ---- 卡密 ----
class CardCodeAdminOut(BaseModel):
    id: int
    code: str
    batch_no: str
    card_type: str
    vip_days: int
    coins: int
    status: str
    expire_at: datetime | None
    remark: str
    used_by_phone: str | None = None
    used_at: datetime | None
    created_at: datetime


class CardBatchCreateRequest(BaseModel):
    card_type: str  # vip / coins
    vip_days: int = 0
    coins: int = 0
    count: int = 1
    expire_at: datetime | None = None
    remark: str = ""


# ---- 分销配置 ----
class DistributionConfigOut(BaseModel):
    direct_rate_percent: int
    indirect_rate_percent: int
    min_withdraw_cents: int
    max_withdraw_cents: int
    service_fee_percent: int

    class Config:
        from_attributes = True


class DistributionConfigUpdateRequest(BaseModel):
    direct_rate_percent: int | None = None
    indirect_rate_percent: int | None = None
    min_withdraw_cents: int | None = None
    max_withdraw_cents: int | None = None
    service_fee_percent: int | None = None


# ---- 提现审核 ----
class WithdrawApplyAdminOut(BaseModel):
    id: int
    order_no: str
    user_phone: str
    amount_cents: int
    fee_cents: int
    actual_cents: int
    account_type: str
    account_snapshot: str
    status: str
    reject_reason: str
    created_at: datetime
    processed_at: datetime | None


class WithdrawRejectRequest(BaseModel):
    reason: str = "管理员驳回"


# ---- 静态页面 ----
class StaticPageAdminOut(BaseModel):
    slug: str
    title: str
    content: str
    updated_at: datetime

    class Config:
        from_attributes = True


class StaticPageUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None


# ---- 意见反馈 ----
class FeedbackAdminOut(BaseModel):
    id: int
    user_phone: str
    content: str
    contact: str
    images: list[str]
    status: str
    admin_reply: str
    created_at: datetime


class FeedbackReplyRequest(BaseModel):
    reply: str


# ---- 管理员账号 ----
class AdminAccountOut(BaseModel):
    id: int
    phone: str
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCreateRequest(BaseModel):
    phone: str
    password: str
    nickname: str = "管理员"


class AdminPromoteRequest(BaseModel):
    phone: str


# ---- 操作日志 ----
class ActionLogOut(BaseModel):
    id: int
    admin_phone: str
    action: str
    detail: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- 收藏/追剧后台查看 ----
class FavoriteAdminOut(BaseModel):
    user_phone: str
    video_title: str
    created_at: datetime


class WatchHistoryAdminOut(BaseModel):
    user_phone: str
    video_title: str
    episode_no: int
    progress_seconds: int
    updated_at: datetime


# ---- 首页焦点图 ----
class BannerAdminOut(BaseModel):
    id: int
    title: str
    image_url: str
    link_url: str
    sort: int
    is_active: bool

    class Config:
        from_attributes = True


class BannerCreateRequest(BaseModel):
    title: str = ""
    image_url: str
    link_url: str = ""
    sort: int = 0
    is_active: bool = True


class BannerUpdateRequest(BaseModel):
    title: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    sort: int | None = None
    is_active: bool | None = None


# ---- 违禁词 ----
class BannedWordOut(BaseModel):
    id: int
    word: str

    class Config:
        from_attributes = True


class BannedWordCreateRequest(BaseModel):
    word: str


class ContentCheckRequest(BaseModel):
    content: str


class ContentCheckResult(BaseModel):
    is_legal: bool
    banned_words: list[str]


# ---- 看板 ----
class DashboardStats(BaseModel):
    total_users: int
    total_videos: int
    total_vip_orders_paid: int
    total_recharge_orders_paid: int
    revenue_cents: int
    new_users_today: int
