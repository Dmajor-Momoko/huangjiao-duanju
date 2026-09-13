from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.card import CardCode
from app.models.mixins import utcnow
from app.models.order import WalletLog
from app.models.user import User
from app.schemas.card import CardRedeemRequest, CardRedeemResult

router = APIRouter(prefix="/card-codes", tags=["卡密兑换"])


@router.post("/redeem", response_model=CardRedeemResult)
async def redeem_card(
    payload: CardRedeemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    code = payload.code.strip().upper()
    card = await db.scalar(select(CardCode).where(CardCode.code == code))
    if not card:
        raise HTTPException(404, "卡密不存在，请检查后重新输入")
    if card.status != "unused":
        raise HTTPException(400, "该卡密已被使用")
    if card.expire_at and utcnow() > card.expire_at:
        raise HTTPException(400, "该卡密已过期")

    if card.card_type == "vip":
        base = current_user.vip_expire_at if current_user.vip_active() else utcnow()
        current_user.vip_expire_at = base + timedelta(days=card.vip_days)
        current_user.is_vip = True
        db.add(current_user)
    elif card.card_type == "coins":
        current_user.coins += card.coins
        db.add(current_user)
        db.add(
            WalletLog(
                user_id=current_user.id,
                type="card",
                amount=card.coins,
                balance_after=current_user.coins,
                remark=f"卡密兑换（{card.code}）",
            )
        )
    else:
        raise HTTPException(400, "卡密类型异常")

    card.status = "used"
    card.used_by_user_id = current_user.id
    card.used_at = utcnow()
    db.add(card)
    await db.commit()
    await db.refresh(current_user)

    return CardRedeemResult(
        card_type=card.card_type,
        vip_days=card.vip_days,
        coins=card.coins,
        balance=current_user.coins,
        vip_expire_at=current_user.vip_expire_at,
    )
