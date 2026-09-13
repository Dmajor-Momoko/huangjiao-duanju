from pydantic import BaseModel


class BannerOut(BaseModel):
    id: int
    title: str
    image_url: str
    link_url: str

    class Config:
        from_attributes = True
