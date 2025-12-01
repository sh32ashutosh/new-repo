from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "vLink Backend"
    
    # FIXED: Renamed from API_V1_STR to API_STR to match the new flattened structure
    API_STR: str = "/api"
    
    # CORS Configuration
    # In production, set this to your specific frontend domain
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Database (Async SQLite for Hackathon)
    DATABASE_URL: str = "sqlite+aiosqlite:///./vlink.db"
    
    # JWT Auth
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SUPER_SECRET_KEY_IN_ENV_FILE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    class Config:
        case_sensitive = True

settings = Settings()