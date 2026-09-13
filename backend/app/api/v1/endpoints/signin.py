from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import WalletLog
from app.models.signin import SignInRecord, SignInRule
from app.models.user import User
from app.schemas.signin import SignInDayStatus, SignInResultOut, SignInRuleOut, SignInStatusOut

router = APIRouter(prefix="/signin", tags=["每日签到"])


async def _get_rules(db: AsyncSession) -> dict[int, int]:
    rows = await db.execute(select(SignInRule).order_by(SignInRule.day))
    return {r.day: r.coins for r in rows.scalars().all()}


async def _last_record(db: AsyncSession, user_id: int) -> SignInRecord | None:
    return await db.scalar(
        select(SignInRecord)
        .where(SignInRecord.user_id == user_id)
        .order_by(SignInRecord.sign_date.desc())
        .limit(1)
    )


@router.get("/status", response_model=SignInStatusOut)
async def signin_status(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    rules = await _get_rules(db)
    last_record = await _last_record(db, current_user.id)

    today_signed = bool(last_record and last_record.sign_date == today)
    if last_record and last_record.sign_date in (today, today - timedelta(days=1)):
        streak_days = last_record.streak_no
    else:
        streak_days = 0
    next_cycle_day = last_record.cycle_day if today_signed else (streak_days % 7) + 1

    month_start = today.replace(day=1)
    rows = await db.execute(
        select(SignInRecord).where(
            SignInRecord.user_id == current_user.id,
            SignInRecord.sign_date >= month_start,
            SignInRecord.sign_date <= today,
        )
    )
    signed_map = {r.sign_date: r.coins_awarded for r in rows.scalars().all()}

    calendar = []
    cursor = month_start
    while cursor.month == month_start.month:
        calendar.append(SignInDayStatus(date=cursor, signed=cursor in signed_map, coins=signed_map.get(cursor)))
        cursor += timedelta(days=1)

    return SignInStatusOut(
        today_signed=today_signed,
        streak_days=streak_days,
        next_cycle_day=next_cycle_day,
        rules=[SignInRuleOut(day=d, coins=c) for d, c in sorted(rules.items())],
        calendar=calendar,
    )


@router.post("", response_model=SignInResultOut)
async def sign_in(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    yesterday = today - timedelta(days=1)

    last_record = await _last_record(db, current_user.id)
    if last_record and last_record.sign_date == today:
        raise HTTPException(400, "今天已经签到过了")

    new_streak = last_record.streak_no + 1 if last_record and last_record.sign_date == yesterday else 1
    cycle_day = ((new_streak - 1) % 7) + 1

    rules = await _get_rules(db)
    coins = rules.get(cycle_day, 0)

    db.add(
        SignInRecord(
            user_id=current_user.id,
            sign_date=today,
            streak_no=new_streak,
            cycle_day=cycle_day,
            coins_awarded=coins,
        )
    )
    current_user.coins += coins
    db.add(current_user)
    db.add(
        WalletLog(
            user_id=current_user.id,
            type="signin",
            amount=coins,
            balance_after=current_user.coins,
            remark=f"每日签到（连续第{new_streak}天）",
        )
    )
    await db.commit()

    return SignInResultOut(coins_awarded=coins, streak_days=new_streak, balance=current_user.coins)
