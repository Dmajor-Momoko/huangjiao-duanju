import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.distribution import CommissionLog, DistributionConfig
from app.models.mixins import utcnow
from app.models.order import AdFreeOrder, AdFreePlan, RechargeOrder, VideoUnlock, VipOrder, VipPlan, WalletLog
from app.models.user import User
from app.models.video import Video
from app.schemas.order import (
    AdFreePlanOut,
    CreateAdFreeOrderRequest,
    CreateRechargeOrderRequest,
    CreateVipOrderRequest,
    OrderOut,
    UnlockVideoRequest,
    VipPlanOut,
)
from app.services.payment import get_payment_provider

router = APIRouter(prefix="/orders", tags=["订单/支付"])


def _new_order_no(prefix: str) -> str:
    return f"{prefix}{utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"


async def _award_commission(db: AsyncSession, buyer: User, amount_cents: int, order_type: str, order_no: str):
    """下级用户付款成功后，给其推荐人（一级）和推荐人的推荐人（二级）各记一笔佣金。"""
    if not buyer.referred_by_id or amount_cents <= 0:
        return
    config = await db.scalar(select(DistributionConfig).limit(1))
    if not config:
        return

    level1 = await db.get(User, buyer.referred_by_id)
    if level1 and config.direct_rate_percent > 0:
        commission = amount_cents * config.direct_rate_percent // 100
        if commission > 0:
            level1.commission_balance_cents += commission
            level1.commission_total_cents += commission
            db.add(level1)
            db.add(
                CommissionLog(
                    user_id=level1.id,
                    from_user_id=buyer.id,
                    level=1,
                    source_amount_cents=amount_cents,
                    commission_cents=commission,
                    order_type=order_type,
                    order_no=order_no,
                )
            )

        if level1.referred_by_id and config.indirect_rate_percent > 0:
            level2 = await db.get(User, level1.referred_by_id)
            if level2:
                commission2 = amount_cents * config.indirect_rate_percent // 100
                if commission2 > 0:
                    level2.commission_balance_cents += commission2
                    level2.commission_total_cents += commission2
                    db.add(level2)
                    db.add(
                        CommissionLog(
                            user_id=level2.id,
                            from_user_id=buyer.id,
                            level=2,
                            source_amount_cents=amount_cents,
                            commission_cents=commission2,
                            order_type=order_type,
                            order_no=order_no,
                        )
                    )


@router.get("/vip-plans", response_model=list[VipPlanOut])
async def list_vip_plans(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(VipPlan).order_by(VipPlan.sort))
    return rows.scalars().all()


@router.post("/vip", response_model=OrderOut)
async def create_vip_order(
    payload: CreateVipOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = await db.get(VipPlan, payload.plan_id)
    if not plan:
        raise HTTPException(404, "会员套餐不存在")

    order = VipOrder(
        order_no=_new_order_no("VIP"),
        user_id=current_user.id,
        plan_id=plan.id,
        amount_cents=plan.price_cents,
    )
    db.add(order)
    await db.flush()

    result = await get_payment_provider().charge(order.order_no, order.amount_cents)
    if result.success:
        order.status = "paid"
        order.paid_at = utcnow()
        base = current_user.vip_expire_at if current_user.vip_active() else utcnow()
        current_user.vip_expire_at = base + timedelta(days=plan.duration_days)
        current_user.is_vip = True
        db.add(current_user)
        await _award_commission(db, current_user, order.amount_cents, "vip", order.order_no)

    await db.commit()
    await db.refresh(order)
    return order


@router.get("/ad-free-plans", response_model=list[AdFreePlanOut])
async def list_ad_free_plans(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(AdFreePlan).order_by(AdFreePlan.sort))
    return rows.scalars().all()


@router.post("/ad-free", response_model=OrderOut)
async def create_ad_free_order(
    payload: CreateAdFreeOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = await db.get(AdFreePlan, payload.plan_id)
    if not plan:
        raise HTTPException(404, "免广告套餐不存在")

    order = AdFreeOrder(
        order_no=_new_order_no("ADF"),
        user_id=current_user.id,
        plan_id=plan.id,
        amount_cents=plan.price_cents,
    )
    db.add(order)
    await db.flush()

    result = await get_payment_provider().charge(order.order_no, order.amount_cents)
    if result.success:
        order.status = "paid"
        order.paid_at = utcnow()
        base = current_user.ad_free_expire_at if current_user.ad_free_active() else utcnow()
        current_user.ad_free_expire_at = base + timedelta(days=plan.duration_days)
        current_user.is_ad_free = True
        db.add(current_user)
        await _award_commission(db, current_user, order.amount_cents, "ad_free", order.order_no)

    await db.commit()
    await db.refresh(order)
    return order


@router.post("/recharge", response_model=OrderOut)
async def create_recharge_order(
    payload: CreateRechargeOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = RechargeOrder(
        order_no=_new_order_no("RC"),
        user_id=current_user.id,
        amount_cents=payload.amount_cents,
        coins=payload.coins,
    )
    db.add(order)
    await db.flush()

    result = await get_payment_provider().charge(order.order_no, order.amount_cents)
    if result.success:
        order.status = "paid"
        order.paid_at = utcnow()
        current_user.coins += payload.coins
        db.add(current_user)
        db.add(
            WalletLog(
                user_id=current_user.id,
                type="recharge",
                amount=payload.coins,
                balance_after=current_user.coins,
                remark=f"充值订单 {order.order_no}",
            )
        )
        await _award_commission(db, current_user, order.amount_cents, "recharge", order.order_no)

    await db.commit()
    await db.refresh(order)
    return order


@router.post("/unlock-video")
async def unlock_video(
    payload: UnlockVideoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = await db.get(Video, payload.video_id)
    if not video:
        raise HTTPException(404, "短剧不存在")
    if video.unlock_price_coins <= 0:
        raise HTTPException(400, "该短剧不支持单独解锁，请开通 VIP 观看")

    existing = await db.scalar(
        select(VideoUnlock).where(VideoUnlock.user_id == current_user.id, VideoUnlock.video_id == video.id)
    )
    if existing:
        return {"message": "已解锁"}

    if current_user.coins < video.unlock_price_coins:
        raise HTTPException(400, "余额不足，请先充值")

    current_user.coins -= video.unlock_price_coins
    db.add(current_user)
    db.add(VideoUnlock(user_id=current_user.id, video_id=video.id))
    db.add(
        WalletLog(
            user_id=current_user.id,
            type="consume",
            amount=-video.unlock_price_coins,
            balance_after=current_user.coins,
            remark=f"解锁短剧《{video.title}》",
        )
    )
    await db.commit()
    return {"message": "解锁成功"}
