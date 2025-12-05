from typing import List

# Try to import BaseSettings from either pydantic (v1) or pydantic-settings (for pydantic v2)
try:
    # pydantic v1 exposes BaseSettings here
    from pydantic import BaseSettings  # type: ignore
except Exception:
    # pydantic v2 moved BaseSettings into the pydantic-settings package
    from pydantic_settings import BaseSettings  # type: ignore

from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "vLink Hybrid Backend"
    SECRET_KEY: str = Field("change-me-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    DATABASE_URL: str = "sqlite+aiosqlite:///./vlink.db"
    API_STR: str = "/api"
    FRONTEND_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()