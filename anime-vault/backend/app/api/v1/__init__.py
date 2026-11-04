from fastapi import APIRouter

from app.api.v1 import admin, anime, auth, chat, collection, recommend, search

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(anime.router)
api_router.include_router(search.router)
api_router.include_router(recommend.router)
api_router.include_router(collection.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)


@api_router.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok"}
