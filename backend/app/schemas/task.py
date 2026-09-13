from pydantic import BaseModel


class TaskOut(BaseModel):
    id: int
    code: str
    title: str
    description: str
    reward_coins: int
    task_type: str
    daily_limit: int
    progress_today: int
    completed: bool


class TaskCompleteResult(BaseModel):
    coins_awarded: int
    balance: int
