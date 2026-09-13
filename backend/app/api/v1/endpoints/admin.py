import random
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_admin
from app.core.invite import generate_invite_code
from app.core.security import hash_password
from app.db.session import get_db
from app.models.audit import AdminActionLog
from app.models.banned_word import BannedWord
from app.models.banner import Banner
from app.models.card import CardCode
from app.models.content import Feedback, StaticPage
from app.models.distribution import DistributionConfig, WithdrawApply
from app.models.interaction import Favorite, WatchHistory
from app.models.mixins import utcnow
from app.models.order import AdFreeOrder, AdFreePlan, RechargeOrder, VipOrder, VipPlan, WalletLog
from app.models.signin import SignInRule
from app.models.task import TaskDefinition
from app.models.user import User
from app.models.video import Category, Video, VideoEpisode, VideoImage, VideoPerformer
from app.schemas.admin import (
    ActionLogOut,
    AdFreeOrderAdminOut,
    AdFreePlanAdminOut,
    AdFreePlanCreateRequest,
    AdFreePlanUpdateRequest,
    AdminAccountOut,
    AdminCreateRequest,
    AdminPromoteRequest,
    BannedWordCreateRequest,
    BannedWordOut,
    BannerAdminOut,
    BannerCreateRequest,
    BannerUpdateRequest,
    CardBatchCreateRequest,
    CardCodeAdminOut,
    CategoryCreateRequest,
    CategoryUpdateRequest,
    ContentCheckRequest,
    ContentCheckResult,
    DashboardStats,
    DistributionConfigOut,
    DistributionConfigUpdateRequest,
    EpisodeAdminOut,
    EpisodeCreateRequest,
    EpisodeUpdateRequest,
    FavoriteAdminOut,
    FeedbackAdminOut,
    FeedbackReplyRequest,
    PerformerAdminOut,
    PerformerCreateRequest,
    PerformerUpdateRequest,
    RechargeOrderAdminOut,
    SignInRuleAdminOut,
    SignInRuleUpdateRequest,
    StaticPageAdminOut,
    StaticPageUpdateRequest,
    TaskAdminOut,
    TaskCreateRequest,
    TaskUpdateRequest,
    UserAdjustRequest,
    UserAdminOut,
    VideoAdminOut,
    VideoCreateRequest,
    VideoImageAdminOut,
    VideoImageCreateRequest,
    VideoImageUpdateRequest,
    VideoListAdminOut,
    VideoUpdateRequest,
    VipOrderAdminOut,
    VipPlanAdminOut,
    VipPlanCreateRequest,
    VipPlanUpdateRequest,
    WatchHistoryAdminOut,
    WithdrawApplyAdminOut,
    WithdrawRejectRequest,
)
from app.schemas.video import CategoryOut
from app.services.content_filter import find_banned_words

router = APIRouter(prefix="/admin", tags=["管理后台"], dependencies=[Depends(get_current_admin)])


async def _log_action(db: AsyncSession, admin: User, action: str, detail: str = ""):
    db.add(AdminActionLog(admin_user_id=admin.id, admin_phone=admin.phone, action=action, detail=detail))


# ---------------- 数据看板 ----------------
@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(db: AsyncSession = Depends(get_db)):
    total_users = await db.scalar(select(func.count(User.id))) or 0
    total_videos = await db.scalar(select(func.count(Video.id))) or 0
    total_vip_orders_paid = await db.scalar(
        select(func.count(VipOrder.id)).where(VipOrder.status == "paid")
    ) or 0
    total_recharge_orders_paid = await db.scalar(
        select(func.count(RechargeOrder.id)).where(RechargeOrder.status == "paid")
    ) or 0
    vip_revenue = await db.scalar(
        select(func.coalesce(func.sum(VipOrder.amount_cents), 0)).where(VipOrder.status == "paid")
    ) or 0
    recharge_revenue = await db.scalar(
        select(func.coalesce(func.sum(RechargeOrder.amount_cents), 0)).where(RechargeOrder.status == "paid")
    ) or 0
    today_start = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= today_start)
    ) or 0

    return DashboardStats(
        total_users=total_users,
        total_videos=total_videos,
        total_vip_orders_paid=total_vip_orders_paid,
        total_recharge_orders_paid=total_recharge_orders_paid,
        revenue_cents=vip_revenue + recharge_revenue,
        new_users_today=new_users_today,
    )


# ---------------- 分类 ----------------
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Category).order_by(Category.sort))
    return rows.scalars().all()


@router.post("/categories", response_model=CategoryOut)
async def create_category(payload: CategoryCreateRequest, db: AsyncSession = Depends(get_db)):
    category = Category(name=payload.name, sort=payload.sort)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryOut)
async def update_category(category_id: int, payload: CategoryUpdateRequest, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "分类不存在")
    if payload.name is not None:
        category.name = payload.name
    if payload.sort is not None:
        category.sort = payload.sort
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "分类不存在")
    await db.delete(category)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 短剧 ----------------
@router.get("/videos", response_model=list[VideoListAdminOut])
async def list_videos(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(Video).options(selectinload(Video.episodes)).order_by(Video.created_at.desc())
    )
    videos = rows.scalars().all()
    return [
        VideoListAdminOut(
            id=v.id,
            title=v.title,
            cover=v.cover,
            category_id=v.category_id,
            is_online=v.is_online,
            episode_count=len(v.episodes),
        )
        for v in videos
    ]


@router.post("/videos", response_model=VideoAdminOut)
async def create_video(payload: VideoCreateRequest, db: AsyncSession = Depends(get_db)):
    video = Video(**payload.model_dump())
    db.add(video)
    await db.commit()
    await db.refresh(video, attribute_names=["episodes", "performers", "images"])
    return video


@router.get("/videos/{video_id}", response_model=VideoAdminOut)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await db.get(
        Video,
        video_id,
        options=[selectinload(Video.episodes), selectinload(Video.performers), selectinload(Video.images)],
    )
    if not video:
        raise HTTPException(404, "短剧不存在")
    return video


@router.put("/videos/{video_id}", response_model=VideoAdminOut)
async def update_video(video_id: int, payload: VideoUpdateRequest, db: AsyncSession = Depends(get_db)):
    video = await db.get(
        Video,
        video_id,
        options=[selectinload(Video.episodes), selectinload(Video.performers), selectinload(Video.images)],
    )
    if not video:
        raise HTTPException(404, "短剧不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(video, key, value)
    db.add(video)
    await db.commit()
    await db.refresh(video, attribute_names=["episodes", "performers", "images"])
    return video


@router.delete("/videos/{video_id}")
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")
    await db.delete(video)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 分集 ----------------
@router.post("/videos/{video_id}/episodes", response_model=EpisodeAdminOut)
async def create_episode(video_id: int, payload: EpisodeCreateRequest, db: AsyncSession = Depends(get_db)):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")
    episode = VideoEpisode(video_id=video_id, **payload.model_dump())
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode


@router.put("/episodes/{episode_id}", response_model=EpisodeAdminOut)
async def update_episode(episode_id: int, payload: EpisodeUpdateRequest, db: AsyncSession = Depends(get_db)):
    episode = await db.get(VideoEpisode, episode_id)
    if not episode:
        raise HTTPException(404, "分集不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(episode, key, value)
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode


@router.delete("/episodes/{episode_id}")
async def delete_episode(episode_id: int, db: AsyncSession = Depends(get_db)):
    episode = await db.get(VideoEpisode, episode_id)
    if not episode:
        raise HTTPException(404, "分集不存在")
    await db.delete(episode)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 演员/演职员 ----------------
@router.post("/videos/{video_id}/performers", response_model=PerformerAdminOut)
async def create_performer(video_id: int, payload: PerformerCreateRequest, db: AsyncSession = Depends(get_db)):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")
    performer = VideoPerformer(video_id=video_id, **payload.model_dump())
    db.add(performer)
    await db.commit()
    await db.refresh(performer)
    return performer


@router.put("/performers/{performer_id}", response_model=PerformerAdminOut)
async def update_performer(performer_id: int, payload: PerformerUpdateRequest, db: AsyncSession = Depends(get_db)):
    performer = await db.get(VideoPerformer, performer_id)
    if not performer:
        raise HTTPException(404, "演职员不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(performer, key, value)
    db.add(performer)
    await db.commit()
    await db.refresh(performer)
    return performer


@router.delete("/performers/{performer_id}")
async def delete_performer(performer_id: int, db: AsyncSession = Depends(get_db)):
    performer = await db.get(VideoPerformer, performer_id)
    if not performer:
        raise HTTPException(404, "演职员不存在")
    await db.delete(performer)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 壁纸图集 ----------------
@router.post("/videos/{video_id}/images", response_model=VideoImageAdminOut)
async def create_video_image(video_id: int, payload: VideoImageCreateRequest, db: AsyncSession = Depends(get_db)):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")
    image = VideoImage(video_id=video_id, **payload.model_dump())
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@router.put("/images/{image_id}", response_model=VideoImageAdminOut)
async def update_video_image(image_id: int, payload: VideoImageUpdateRequest, db: AsyncSession = Depends(get_db)):
    image = await db.get(VideoImage, image_id)
    if not image:
        raise HTTPException(404, "图片不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(image, key, value)
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@router.delete("/images/{image_id}")
async def delete_video_image(image_id: int, db: AsyncSession = Depends(get_db)):
    image = await db.get(VideoImage, image_id)
    if not image:
        raise HTTPException(404, "图片不存在")
    await db.delete(image)
    await db.commit()
    return {"message": "已删除"}


# ---------------- VIP 套餐 ----------------
@router.get("/vip-plans", response_model=list[VipPlanAdminOut])
async def list_vip_plans_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(VipPlan).order_by(VipPlan.sort))
    return rows.scalars().all()


@router.post("/vip-plans", response_model=VipPlanAdminOut)
async def create_vip_plan(payload: VipPlanCreateRequest, db: AsyncSession = Depends(get_db)):
    plan = VipPlan(**payload.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.put("/vip-plans/{plan_id}", response_model=VipPlanAdminOut)
async def update_vip_plan(plan_id: int, payload: VipPlanUpdateRequest, db: AsyncSession = Depends(get_db)):
    plan = await db.get(VipPlan, plan_id)
    if not plan:
        raise HTTPException(404, "套餐不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/vip-plans/{plan_id}")
async def delete_vip_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    plan = await db.get(VipPlan, plan_id)
    if not plan:
        raise HTTPException(404, "套餐不存在")
    await db.delete(plan)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 免广告套餐 ----------------
@router.get("/ad-free-plans", response_model=list[AdFreePlanAdminOut])
async def list_ad_free_plans_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(AdFreePlan).order_by(AdFreePlan.sort))
    return rows.scalars().all()


@router.post("/ad-free-plans", response_model=AdFreePlanAdminOut)
async def create_ad_free_plan(payload: AdFreePlanCreateRequest, db: AsyncSession = Depends(get_db)):
    plan = AdFreePlan(**payload.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.put("/ad-free-plans/{plan_id}", response_model=AdFreePlanAdminOut)
async def update_ad_free_plan(plan_id: int, payload: AdFreePlanUpdateRequest, db: AsyncSession = Depends(get_db)):
    plan = await db.get(AdFreePlan, plan_id)
    if not plan:
        raise HTTPException(404, "套餐不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/ad-free-plans/{plan_id}")
async def delete_ad_free_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    plan = await db.get(AdFreePlan, plan_id)
    if not plan:
        raise HTTPException(404, "套餐不存在")
    await db.delete(plan)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 首页焦点图 ----------------
@router.get("/banners", response_model=list[BannerAdminOut])
async def list_banners_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Banner).order_by(Banner.sort))
    return rows.scalars().all()


@router.post("/banners", response_model=BannerAdminOut)
async def create_banner(payload: BannerCreateRequest, db: AsyncSession = Depends(get_db)):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


@router.put("/banners/{banner_id}", response_model=BannerAdminOut)
async def update_banner(banner_id: int, payload: BannerUpdateRequest, db: AsyncSession = Depends(get_db)):
    banner = await db.get(Banner, banner_id)
    if not banner:
        raise HTTPException(404, "焦点图不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


@router.delete("/banners/{banner_id}")
async def delete_banner(banner_id: int, db: AsyncSession = Depends(get_db)):
    banner = await db.get(Banner, banner_id)
    if not banner:
        raise HTTPException(404, "焦点图不存在")
    await db.delete(banner)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 用户 ----------------
@router.get("/users", response_model=list[UserAdminOut])
async def list_users(keyword: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(User).order_by(User.created_at.desc())
    if keyword:
        stmt = stmt.where(User.phone.contains(keyword))
    rows = await db.execute(stmt)
    return rows.scalars().all()


@router.post("/users/{user_id}/adjust", response_model=UserAdminOut)
async def adjust_user(
    user_id: int,
    payload: UserAdjustRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")

    if payload.coins_delta:
        user.coins += payload.coins_delta
        db.add(
            WalletLog(
                user_id=user.id,
                type="recharge" if payload.coins_delta > 0 else "consume",
                amount=payload.coins_delta,
                balance_after=user.coins,
                remark=payload.remark,
            )
        )

    if payload.extend_vip_days:
        base = user.vip_expire_at if user.vip_active() else utcnow()
        user.vip_expire_at = base + timedelta(days=payload.extend_vip_days)
        user.is_vip = True

    if payload.extend_ad_free_days:
        base = user.ad_free_expire_at if user.ad_free_active() else utcnow()
        user.ad_free_expire_at = base + timedelta(days=payload.extend_ad_free_days)
        user.is_ad_free = True

    db.add(user)
    await _log_action(
        db,
        current_admin,
        "user.adjust",
        f"调整用户 {user.phone}：币{payload.coins_delta:+d}，VIP+{payload.extend_vip_days}天，"
        f"免广告+{payload.extend_ad_free_days}天，备注：{payload.remark}",
    )
    await db.commit()
    await db.refresh(user)
    return user


# ---------------- 签到规则 ----------------
@router.get("/signin-rules", response_model=list[SignInRuleAdminOut])
async def list_signin_rules(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(SignInRule).order_by(SignInRule.day))
    return rows.scalars().all()


@router.put("/signin-rules/{day}", response_model=SignInRuleAdminOut)
async def update_signin_rule(day: int, payload: SignInRuleUpdateRequest, db: AsyncSession = Depends(get_db)):
    rule = await db.scalar(select(SignInRule).where(SignInRule.day == day))
    if not rule:
        raise HTTPException(404, "签到规则不存在")
    rule.coins = payload.coins
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


# ---------------- 积分任务 ----------------
@router.get("/tasks", response_model=list[TaskAdminOut])
async def list_tasks_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(TaskDefinition).order_by(TaskDefinition.sort))
    return rows.scalars().all()


@router.post("/tasks", response_model=TaskAdminOut)
async def create_task(payload: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(TaskDefinition).where(TaskDefinition.code == payload.code))
    if existing:
        raise HTTPException(400, "任务代码已存在")
    task = TaskDefinition(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/tasks/{task_id}", response_model=TaskAdminOut)
async def update_task(task_id: int, payload: TaskUpdateRequest, db: AsyncSession = Depends(get_db)):
    task = await db.get(TaskDefinition, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(TaskDefinition, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    await db.delete(task)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 卡密 ----------------
_CARD_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 去掉易混淆的 0/O/1/I/L


async def _generate_unique_card_code(db: AsyncSession) -> str:
    for _ in range(20):
        raw = "".join(random.choices(_CARD_ALPHABET, k=16))
        code = "-".join(raw[i : i + 4] for i in range(0, 16, 4))
        exists = await db.scalar(select(CardCode.id).where(CardCode.code == code))
        if not exists:
            return code
    raise HTTPException(500, "生成卡密失败，请重试")


@router.get("/card-codes", response_model=list[CardCodeAdminOut])
async def list_card_codes(
    batch_no: str | None = None, status: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(CardCode, User.phone).outerjoin(User, User.id == CardCode.used_by_user_id)
    if batch_no:
        stmt = stmt.where(CardCode.batch_no == batch_no)
    if status:
        stmt = stmt.where(CardCode.status == status)
    rows = await db.execute(stmt.order_by(CardCode.created_at.desc()))
    return [
        CardCodeAdminOut(
            id=c.id,
            code=c.code,
            batch_no=c.batch_no,
            card_type=c.card_type,
            vip_days=c.vip_days,
            coins=c.coins,
            status=c.status,
            expire_at=c.expire_at,
            remark=c.remark,
            used_by_phone=phone,
            used_at=c.used_at,
            created_at=c.created_at,
        )
        for c, phone in rows.all()
    ]


@router.post("/card-codes/batch", response_model=list[CardCodeAdminOut])
async def create_card_codes(
    payload: CardBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    if payload.card_type not in ("vip", "coins"):
        raise HTTPException(400, "卡密类型必须是 vip 或 coins")
    if payload.card_type == "vip" and payload.vip_days <= 0:
        raise HTTPException(400, "VIP 卡密需要设置天数")
    if payload.card_type == "coins" and payload.coins <= 0:
        raise HTTPException(400, "币卡密需要设置币数")
    if not 1 <= payload.count <= 500:
        raise HTTPException(400, "单次生成数量需在 1~500 之间")

    batch_no = utcnow().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:4].upper()
    cards = []
    for _ in range(payload.count):
        code = await _generate_unique_card_code(db)
        card = CardCode(
            code=code,
            batch_no=batch_no,
            card_type=payload.card_type,
            vip_days=payload.vip_days,
            coins=payload.coins,
            expire_at=payload.expire_at,
            remark=payload.remark,
        )
        db.add(card)
        cards.append(card)
    await _log_action(
        db,
        current_admin,
        "card.batch_create",
        f"生成 {payload.count} 张 {payload.card_type} 卡密，批次 {batch_no}",
    )
    await db.commit()
    for card in cards:
        await db.refresh(card)

    return [
        CardCodeAdminOut(
            id=c.id,
            code=c.code,
            batch_no=c.batch_no,
            card_type=c.card_type,
            vip_days=c.vip_days,
            coins=c.coins,
            status=c.status,
            expire_at=c.expire_at,
            remark=c.remark,
            used_by_phone=None,
            used_at=c.used_at,
            created_at=c.created_at,
        )
        for c in cards
    ]


@router.delete("/card-codes/{card_id}")
async def delete_card_code(card_id: int, db: AsyncSession = Depends(get_db)):
    card = await db.get(CardCode, card_id)
    if not card:
        raise HTTPException(404, "卡密不存在")
    if card.status != "unused":
        raise HTTPException(400, "已使用的卡密不能删除")
    await db.delete(card)
    await db.commit()
    return {"message": "已删除"}


# ---------------- 分销配置 ----------------
@router.get("/distribution-config", response_model=DistributionConfigOut)
async def get_distribution_config(db: AsyncSession = Depends(get_db)):
    config = await db.scalar(select(DistributionConfig).limit(1))
    if not config:
        config = DistributionConfig()
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.put("/distribution-config", response_model=DistributionConfigOut)
async def update_distribution_config(payload: DistributionConfigUpdateRequest, db: AsyncSession = Depends(get_db)):
    config = await db.scalar(select(DistributionConfig).limit(1))
    if not config:
        config = DistributionConfig()
        db.add(config)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, key, value)
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


# ---------------- 提现审核 ----------------
def _withdraw_admin_out(apply: WithdrawApply, phone: str) -> WithdrawApplyAdminOut:
    return WithdrawApplyAdminOut(
        id=apply.id,
        order_no=apply.order_no,
        user_phone=phone,
        amount_cents=apply.amount_cents,
        fee_cents=apply.fee_cents,
        actual_cents=apply.actual_cents,
        account_type=apply.account_type,
        account_snapshot=apply.account_snapshot,
        status=apply.status,
        reject_reason=apply.reject_reason,
        created_at=apply.created_at,
        processed_at=apply.processed_at,
    )


@router.get("/withdraw-applies", response_model=list[WithdrawApplyAdminOut])
async def list_withdraw_applies(status: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(WithdrawApply, User.phone).join(User, User.id == WithdrawApply.user_id)
    if status:
        stmt = stmt.where(WithdrawApply.status == status)
    rows = await db.execute(stmt.order_by(WithdrawApply.created_at.desc()))
    return [_withdraw_admin_out(w, phone) for w, phone in rows.all()]


@router.post("/withdraw-applies/{apply_id}/approve", response_model=WithdrawApplyAdminOut)
async def approve_withdraw(
    apply_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)
):
    apply = await db.get(WithdrawApply, apply_id)
    if not apply:
        raise HTTPException(404, "提现申请不存在")
    if apply.status != "pending":
        raise HTTPException(400, "该申请已处理，不能重复操作")
    apply.status = "paid"
    apply.processed_at = utcnow()
    db.add(apply)
    phone = await db.scalar(select(User.phone).where(User.id == apply.user_id))
    await _log_action(
        db, current_admin, "withdraw.approve", f"通过 {phone} 的提现申请 {apply.order_no}，¥{apply.amount_cents / 100:.2f}"
    )
    await db.commit()
    await db.refresh(apply)
    return _withdraw_admin_out(apply, phone)


@router.post("/withdraw-applies/{apply_id}/reject", response_model=WithdrawApplyAdminOut)
async def reject_withdraw(
    apply_id: int,
    payload: WithdrawRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    apply = await db.get(WithdrawApply, apply_id)
    if not apply:
        raise HTTPException(404, "提现申请不存在")
    if apply.status != "pending":
        raise HTTPException(400, "该申请已处理，不能重复操作")

    user = await db.get(User, apply.user_id)
    user.commission_balance_cents += apply.amount_cents
    db.add(user)

    apply.status = "rejected"
    apply.reject_reason = payload.reason
    apply.processed_at = utcnow()
    db.add(apply)
    await _log_action(
        db,
        current_admin,
        "withdraw.reject",
        f"驳回 {user.phone} 的提现申请 {apply.order_no}，¥{apply.amount_cents / 100:.2f}，原因：{payload.reason}",
    )
    await db.commit()
    await db.refresh(apply)
    return _withdraw_admin_out(apply, user.phone)


# ---------------- 订单 ----------------
@router.get("/orders/vip", response_model=list[VipOrderAdminOut])
async def list_vip_orders(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(VipOrder, User.phone, VipPlan.name)
        .join(User, User.id == VipOrder.user_id)
        .join(VipPlan, VipPlan.id == VipOrder.plan_id)
        .order_by(VipOrder.created_at.desc())
    )
    return [
        VipOrderAdminOut(
            order_no=order.order_no,
            user_phone=phone,
            plan_name=plan_name,
            amount_cents=order.amount_cents,
            status=order.status,
            paid_at=order.paid_at,
            created_at=order.created_at,
        )
        for order, phone, plan_name in rows.all()
    ]


@router.get("/orders/ad-free", response_model=list[AdFreeOrderAdminOut])
async def list_ad_free_orders(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(AdFreeOrder, User.phone, AdFreePlan.name)
        .join(User, User.id == AdFreeOrder.user_id)
        .join(AdFreePlan, AdFreePlan.id == AdFreeOrder.plan_id)
        .order_by(AdFreeOrder.created_at.desc())
    )
    return [
        AdFreeOrderAdminOut(
            order_no=order.order_no,
            user_phone=phone,
            plan_name=plan_name,
            amount_cents=order.amount_cents,
            status=order.status,
            paid_at=order.paid_at,
            created_at=order.created_at,
        )
        for order, phone, plan_name in rows.all()
    ]


@router.get("/orders/recharge", response_model=list[RechargeOrderAdminOut])
async def list_recharge_orders(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(RechargeOrder, User.phone)
        .join(User, User.id == RechargeOrder.user_id)
        .order_by(RechargeOrder.created_at.desc())
    )
    return [
        RechargeOrderAdminOut(
            order_no=order.order_no,
            user_phone=phone,
            amount_cents=order.amount_cents,
            coins=order.coins,
            status=order.status,
            paid_at=order.paid_at,
            created_at=order.created_at,
        )
        for order, phone in rows.all()
    ]


# ---------------- 静态页面 ----------------
@router.get("/static-pages", response_model=list[StaticPageAdminOut])
async def list_static_pages(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(StaticPage).order_by(StaticPage.id))
    return rows.scalars().all()


@router.put("/static-pages/{slug}", response_model=StaticPageAdminOut)
async def update_static_page(slug: str, payload: StaticPageUpdateRequest, db: AsyncSession = Depends(get_db)):
    page = await db.scalar(select(StaticPage).where(StaticPage.slug == slug))
    if not page:
        raise HTTPException(404, "页面不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(page, key, value)
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


# ---------------- 意见反馈 ----------------
def _feedback_admin_out(fb: Feedback, phone: str) -> FeedbackAdminOut:
    return FeedbackAdminOut(
        id=fb.id,
        user_phone=phone,
        content=fb.content,
        contact=fb.contact,
        images=[u for u in fb.images.split(",") if u],
        status=fb.status,
        admin_reply=fb.admin_reply,
        created_at=fb.created_at,
    )


@router.get("/feedbacks", response_model=list[FeedbackAdminOut])
async def list_feedbacks(status: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Feedback, User.phone).join(User, User.id == Feedback.user_id)
    if status:
        stmt = stmt.where(Feedback.status == status)
    rows = await db.execute(stmt.order_by(Feedback.created_at.desc()))
    return [_feedback_admin_out(fb, phone) for fb, phone in rows.all()]


@router.post("/feedbacks/{feedback_id}/reply", response_model=FeedbackAdminOut)
async def reply_feedback(feedback_id: int, payload: FeedbackReplyRequest, db: AsyncSession = Depends(get_db)):
    fb = await db.get(Feedback, feedback_id)
    if not fb:
        raise HTTPException(404, "反馈不存在")
    fb.admin_reply = payload.reply
    fb.status = "replied"
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    phone = await db.scalar(select(User.phone).where(User.id == fb.user_id))
    return _feedback_admin_out(fb, phone)


# ---------------- 管理员账号 ----------------
@router.get("/admins", response_model=list[AdminAccountOut])
async def list_admins(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(User).where(User.is_admin.is_(True)).order_by(User.created_at))
    return rows.scalars().all()


@router.post("/admins", response_model=AdminAccountOut)
async def create_admin_account(
    payload: AdminCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    exists = await db.scalar(select(User.id).where(User.phone == payload.phone))
    if exists:
        raise HTTPException(400, "该手机号已注册")
    invite_code = await generate_invite_code(db)
    user = User(
        phone=payload.phone,
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),
        invite_code=invite_code,
        is_admin=True,
    )
    db.add(user)
    await _log_action(db, current_admin, "admin.create", f"新增管理员账号 {payload.phone}")
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/admins/promote", response_model=AdminAccountOut)
async def promote_to_admin(
    payload: AdminPromoteRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = await db.scalar(select(User).where(User.phone == payload.phone))
    if not user:
        raise HTTPException(404, "用户不存在")
    if user.is_admin:
        raise HTTPException(400, "该用户已经是管理员")
    user.is_admin = True
    db.add(user)
    await _log_action(db, current_admin, "admin.promote", f"将用户 {user.phone} 提升为管理员")
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/admins/{user_id}/revoke")
async def revoke_admin(
    user_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)
):
    if user_id == current_admin.id:
        raise HTTPException(400, "不能取消自己的管理员权限")
    user = await db.get(User, user_id)
    if not user or not user.is_admin:
        raise HTTPException(404, "管理员不存在")
    user.is_admin = False
    db.add(user)
    await _log_action(db, current_admin, "admin.revoke", f"取消 {user.phone} 的管理员权限")
    await db.commit()
    return {"message": "已取消管理员权限"}


# ---------------- 操作日志 ----------------
@router.get("/action-logs", response_model=list[ActionLogOut])
async def list_action_logs(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(AdminActionLog).order_by(AdminActionLog.created_at.desc()))
    return rows.scalars().all()


# ---------------- 收藏/追剧后台查看 ----------------
@router.get("/favorites", response_model=list[FavoriteAdminOut])
async def list_favorites_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(Favorite, User.phone, Video.title)
        .join(User, User.id == Favorite.user_id)
        .join(Video, Video.id == Favorite.video_id)
        .order_by(Favorite.created_at.desc())
    )
    return [
        FavoriteAdminOut(user_phone=phone, video_title=title, created_at=fav.created_at)
        for fav, phone, title in rows.all()
    ]


@router.get("/watch-history", response_model=list[WatchHistoryAdminOut])
async def list_watch_history_admin(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(WatchHistory, User.phone, Video.title)
        .join(User, User.id == WatchHistory.user_id)
        .join(Video, Video.id == WatchHistory.video_id)
        .order_by(WatchHistory.updated_at.desc())
    )
    return [
        WatchHistoryAdminOut(
            user_phone=phone,
            video_title=title,
            episode_no=history.episode_no,
            progress_seconds=history.progress_seconds,
            updated_at=history.updated_at,
        )
        for history, phone, title in rows.all()
    ]


# ---------------- 违禁词 ----------------
@router.get("/banned-words", response_model=list[BannedWordOut])
async def list_banned_words(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(BannedWord).order_by(BannedWord.word))
    return rows.scalars().all()


@router.post("/banned-words", response_model=BannedWordOut)
async def create_banned_word(payload: BannedWordCreateRequest, db: AsyncSession = Depends(get_db)):
    word = payload.word.strip()
    if not word:
        raise HTTPException(400, "违禁词不能为空")
    exists = await db.scalar(select(BannedWord.id).where(BannedWord.word == word))
    if exists:
        raise HTTPException(400, "该违禁词已存在")
    banned_word = BannedWord(word=word)
    db.add(banned_word)
    await db.commit()
    await db.refresh(banned_word)
    return banned_word


@router.delete("/banned-words/{word_id}")
async def delete_banned_word(word_id: int, db: AsyncSession = Depends(get_db)):
    banned_word = await db.get(BannedWord, word_id)
    if not banned_word:
        raise HTTPException(404, "违禁词不存在")
    await db.delete(banned_word)
    await db.commit()
    return {"message": "已删除"}


@router.post("/content-check", response_model=ContentCheckResult)
async def check_content(payload: ContentCheckRequest, db: AsyncSession = Depends(get_db)):
    hits = await find_banned_words(db, payload.content)
    return ContentCheckResult(is_legal=len(hits) == 0, banned_words=hits)
