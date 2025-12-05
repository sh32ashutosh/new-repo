from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.core.config import settings

# Async engine and session factory
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# FastAPI dependency to provide an async DB session per request/event
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Usage in endpoints:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    Ensures the session is closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session