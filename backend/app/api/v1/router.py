from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    banners,
    cards,
    distribution,
    feedback,
    orders,
    pages,
    signin,
    tasks,
    uploads,
    users,
    videos,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(videos.router)
api_router.include_router(orders.router)
api_router.include_router(signin.router)
api_router.include_router(tasks.router)
api_router.include_router(cards.router)
api_router.include_router(distribution.router)
api_router.include_router(pages.router)
api_router.include_router(feedback.router)
api_router.include_router(banners.router)
api_router.include_router(uploads.router)
api_router.include_router(admin.router)
