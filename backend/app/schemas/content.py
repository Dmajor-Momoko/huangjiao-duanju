from datetime import datetime

from pydantic import BaseModel


class StaticPageOut(BaseModel):
    slug: str
    title: str
    content: str

    class Config:
        from_attributes = True


class StaticPageListItem(BaseModel):
    slug: str
    title: str

    class Config:
        from_attributes = True


class FeedbackCreateRequest(BaseModel):
    content: str
    contact: str = ""
    images: list[str] = []


class FeedbackOut(BaseModel):
    id: int
    content: str
    contact: str
    images: list[str]
    status: str
    admin_reply: str
    created_at: datetime
