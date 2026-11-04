from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AnimeVault API",
    description="动漫知识库 Agent 平台 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok"}


@app.get("/", tags=["根路径"])
async def root():
    return {
        "name": "AnimeVault API",
        "version": "0.1.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }
