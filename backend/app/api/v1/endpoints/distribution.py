import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.distribution import CommissionLog, DistributionConfig, WithdrawAccount, WithdrawApply
from app.models.mixins import utcnow
from app.models.user import User
from app.schemas.distribution import (
    CommissionLogOut,
    DistributionOverviewOut,
    TeamMemberOut,
    WithdrawAccountOut,
    WithdrawAccountUpdateRequest,
    WithdrawApplyOut,
    WithdrawApplyRequest,
    WithdrawRuleOut,
)

router = APIRouter(prefix="/distribution", tags=["分销"])


def _mask_phone(phone: str) -> str:
    return phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone


async def _get_config(db: AsyncSession) -> DistributionConfig:
    config = await db.scalar(select(DistributionConfig).limit(1))
    if not config:
        config = DistributionConfig()
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.get("/overview", response_model=DistributionOverviewOut)
async def overview(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    config = await _get_config(db)
    direct_count = (
        await db.scalar(select(func.count(User.id)).where(User.referred_by_id == current_user.id))
    ) or 0
    direct_ids = select(User.id).where(User.referred_by_id == current_user.id).scalar_subquery()
    indirect_count = (
        await db.scalar(select(func.count(User.id)).where(User.referred_by_id.in_(direct_ids)))
    ) or 0

    return DistributionOverviewOut(
        invite_code=current_user.invite_code,
        direct_count=direct_count,
        indirect_count=indirect_count,
        commission_balance_cents=current_user.commission_balance_cents,
        commission_total_cents=current_user.commission_total_cents,
        direct_rate_percent=config.direct_rate_percent,
        indirect_rate_percent=config.indirect_rate_percent,
    )


@router.get("/team", response_model=list[TeamMemberOut])
async def team(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    direct_rows = (
        await db.execute(
            select(User).where(User.referred_by_id == current_user.id).order_by(User.created_at.desc())
        )
    ).scalars().all()

    result = [
        TeamMemberOut(id=u.id, nickname=u.nickname, phone=_mask_phone(u.phone), level=1, joined_at=u.created_at)
        for u in direct_rows
    ]

    direct_ids = [u.id for u in direct_rows]
    if direct_ids:
        indirect_rows = (
            await db.execute(
                select(User).where(User.referred_by_id.in_(direct_ids)).order_by(User.created_at.desc())
            )
        ).scalars().all()
        result += [
            TeamMemberOut(id=u.id, nickname=u.nickname, phone=_mask_phone(u.phone), level=2, joined_at=u.created_at)
            for u in indirect_rows
        ]
    return result


@router.get("/logs", response_model=list[CommissionLogOut])
async def commission_logs(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = await db.execute(
        select(CommissionLog).where(CommissionLog.user_id == current_user.id).order_by(CommissionLog.created_at.desc())
    )
    return rows.scalars().all()


@router.get("/account", response_model=WithdrawAccountOut | None)
async def get_account(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await db.scalar(select(WithdrawAccount).where(WithdrawAccount.user_id == current_user.id))


@router.put("/account", response_model=WithdrawAccountOut)
async def update_account(
    payload: WithdrawAccountUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.account_type not in ("alipay", "wechat", "bank"):
        raise HTTPException(400, "账户类型不支持")
    if payload.account_type == "wechat" and not payload.qr_image:
        raise HTTPException(400, "微信提现必须上传收款码")
    if payload.account_type == "alipay" and not payload.account_no and not payload.qr_image:
        raise HTTPException(400, "支付宝账号和收款码至少填一个")
    if payload.account_type == "bank" and (not payload.account_no or not payload.bank_name):
        raise HTTPException(400, "银行卡提现需要填写卡号和开户行")

    account = await db.scalar(select(WithdrawAccount).where(WithdrawAccount.user_id == current_user.id))
    if not account:
        account = WithdrawAccount(user_id=current_user.id)
    account.account_type = payload.account_type
    account.real_name = payload.real_name
    account.account_no = payload.account_no
    account.bank_name = payload.bank_name
    account.qr_image = payload.qr_image
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/withdraw-rules", response_model=WithdrawRuleOut)
async def withdraw_rules(db: AsyncSession = Depends(get_db)):
    config = await _get_config(db)
    return WithdrawRuleOut(
        min_withdraw_cents=config.min_withdraw_cents,
        max_withdraw_cents=config.max_withdraw_cents,
        service_fee_percent=config.service_fee_percent,
    )


@router.post("/withdraw", response_model=WithdrawApplyOut)
async def apply_withdraw(
    payload: WithdrawApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await db.scalar(select(WithdrawAccount).where(WithdrawAccount.user_id == current_user.id))
    if not account:
        raise HTTPException(400, "请先绑定提现账户")

    config = await _get_config(db)
    if payload.amount_cents < config.min_withdraw_cents:
        raise HTTPException(400, f"提现金额不能低于 {config.min_withdraw_cents / 100:.2f} 元")
    if payload.amount_cents > config.max_withdraw_cents:
        raise HTTPException(400, f"单笔提现金额不能超过 {config.max_withdraw_cents / 100:.2f} 元")
    if payload.amount_cents > current_user.commission_balance_cents:
        raise HTTPException(400, "佣金余额不足")

    fee_cents = payload.amount_cents * config.service_fee_percent // 100
    actual_cents = payload.amount_cents - fee_cents

    current_user.commission_balance_cents -= payload.amount_cents
    db.add(current_user)

    apply = WithdrawApply(
        order_no=f"WD{utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}",
        user_id=current_user.id,
        amount_cents=payload.amount_cents,
        fee_cents=fee_cents,
        actual_cents=actual_cents,
        account_type=account.account_type,
        account_snapshot=json.dumps(
            {
                "account_type": account.account_type,
                "real_name": account.real_name,
                "account_no": account.account_no,
                "bank_name": account.bank_name,
                "qr_image": account.qr_image,
            },
            ensure_ascii=False,
        ),
    )
    db.add(apply)
    await db.commit()
    await db.refresh(apply)
    return apply


@router.get("/withdraw", response_model=list[WithdrawApplyOut])
async def my_withdraw_applies(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = await db.execute(
        select(WithdrawApply).where(WithdrawApply.user_id == current_user.id).order_by(WithdrawApply.created_at.desc())
    )
    return rows.scalars().all()
