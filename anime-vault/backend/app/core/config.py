from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./animevault.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    BGM_APP_ID: str = ""
    BGM_APP_SECRET: str = ""
    BGM_REDIRECT_URI: str = "http://localhost:3000/auth/bgm/callback"

    SYNC_CONCURRENCY: int = 8
    SYNC_RATE_LIMIT: str = "100/min"

    # Semantic search index. It is a rebuildable cache keyed by bgm_id; see
    # docs/adr/0001-retrieval-index-is-a-cache.md at the workspace root.
    CHROMA_DIR: str = "./chroma_db"
    # api.bgm.tv resets direct connections on this network, so a proxy is opted
    # into per client instead of relying on ambient HTTP_PROXY variables.
    BGM_PROXY: str = ""

    PROJECT_NAME: str = "AnimeVault"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()
