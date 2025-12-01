import sys
import os

# 1. PATH FIX: Add the parent directory to sys.path
# This allows "from backend.core..." to work even if you run this file from inside the backend folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api.router import api_router

# 2. Initialize the FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# 3. Configure CORS (Critical for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount Routes
app.include_router(api_router, prefix=settings.API_STR)

# 5. Database Startup Event
@app.on_event("startup")
async def init_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Tables Verified/Created")

# 6. Health Check
@app.get("/")
async def root():
    return {"status": "ok", "message": "vLink Backend is Running"}

# 7. Debug Runner
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)