from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "vLink"
    API_STR: str = "/api"
    # ⚡ CRITICAL: Hardcode this key so it never changes between restarts
    SECRET_KEY: str = "my_super_secret_hackathon_key_123" 
    ALGORITHM: str = "HS256"
    
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./vlink.db"

settings = Settings()