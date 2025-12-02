from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
# We use a relative import here to ensure it works regardless of where the script is run
from .config import settings

# 1. Create the Async Engine
# check_same_thread=False is needed ONLY for SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}, 
    echo=False,
    future=True
)

# 2. Create the Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. Base class for Models
# The error you saw happened because this specific line was missing
Base = declarative_base()

# 4. Dependency Injection for Routes
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()