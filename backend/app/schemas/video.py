from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    sort: int = 0

    class Config:
        from_attributes = True


class EpisodeOut(BaseModel):
    id: int
    episode_no: int
    title: str
    duration: int
    locked: bool
    # 只有未锁定时才会返回播放地址
    video_url: str | None = None

    class Config:
        from_attributes = True


class PerformerOut(BaseModel):
    id: int
    type: str
    name: str
    avatar: str
    role: str
    bio: str

    class Config:
        from_attributes = True


class VideoImageOut(BaseModel):
    id: int
    name: str
    image_url: str
    downloads: int

    class Config:
        from_attributes = True


class VideoListItem(BaseModel):
    id: int
    title: str
    cover: str
    category_id: int | None
    total_episodes: int

    class Config:
        from_attributes = True


class VideoDetailOut(BaseModel):
    id: int
    title: str
    cover: str
    description: str
    category: CategoryOut | None
    free_episodes: int
    unlock_price_coins: int
    is_unlocked: bool
    is_favorite: bool
    episodes: list[EpisodeOut]
    performers: list[PerformerOut]

    class Config:
        from_attributes = True
