from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import WalletLog
from app.models.task import TaskCompletion, TaskDefinition
from app.models.user import User
from app.schemas.task import TaskCompleteResult, TaskOut

router = APIRouter(prefix="/tasks", tags=["积分任务"])


@router.get("", response_model=list[TaskOut])
async def list_tasks(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    tasks = (
        await db.execute(
            select(TaskDefinition).where(TaskDefinition.is_active.is_(True)).order_by(TaskDefinition.sort)
        )
    ).scalars().all()

    result = []
    for task in tasks:
        if task.task_type == "once":
            done_count = await db.scalar(
                select(func.count(TaskCompletion.id)).where(
                    TaskCompletion.user_id == current_user.id, TaskCompletion.task_id == task.id
                )
            )
            progress_today = min(done_count or 0, 1)
            completed = progress_today >= 1
        else:
            progress_today = await db.scalar(
                select(func.count(TaskCompletion.id)).where(
                    TaskCompletion.user_id == current_user.id,
                    TaskCompletion.task_id == task.id,
                    TaskCompletion.completed_on == today,
                )
            ) or 0
            completed = progress_today >= task.daily_limit

        result.append(
            TaskOut(
                id=task.id,
                code=task.code,
                title=task.title,
                description=task.description,
                reward_coins=task.reward_coins,
                task_type=task.task_type,
                daily_limit=task.daily_limit,
                progress_today=progress_today,
                completed=completed,
            )
        )
    return result


@router.post("/{task_id}/complete", response_model=TaskCompleteResult)
async def complete_task(
    task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    task = await db.get(TaskDefinition, task_id)
    if not task or not task.is_active:
        raise HTTPException(404, "任务不存在")

    today = date.today()
    if task.task_type == "once":
        existing = await db.scalar(
            select(TaskCompletion).where(
                TaskCompletion.user_id == current_user.id, TaskCompletion.task_id == task.id
            )
        )
        if existing:
            raise HTTPException(400, "任务已完成")
    else:
        done_today = await db.scalar(
            select(func.count(TaskCompletion.id)).where(
                TaskCompletion.user_id == current_user.id,
                TaskCompletion.task_id == task.id,
                TaskCompletion.completed_on == today,
            )
        ) or 0
        if done_today >= task.daily_limit:
            raise HTTPException(400, "今日已达完成次数上限")

    db.add(TaskCompletion(user_id=current_user.id, task_id=task.id, completed_on=today))
    current_user.coins += task.reward_coins
    db.add(current_user)
    db.add(
        WalletLog(
            user_id=current_user.id,
            type="task",
            amount=task.reward_coins,
            balance_after=current_user.coins,
            remark=f"完成任务《{task.title}》",
        )
    )
    await db.commit()

    return TaskCompleteResult(coins_awarded=task.reward_coins, balance=current_user.coins)
