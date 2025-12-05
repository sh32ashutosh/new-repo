import sys
import os
import asyncio
import logging

# Ensure backend package imports work when running from backend/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api.router import api_router

# Socket manager and event handlers
from backend.core.socket_manager import sio
import backend.api.sockets  # registers socket event handlers

# FFProbe worker (background consumer)
from backend.core.worker import start_ffprobe_worker

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.main")

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_STR}/openapi.json")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads dir exists and mount for static serving
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Include API router under configured prefix
app.include_router(api_router, prefix=settings.API_STR)


# DB startup: create tables and start background worker
@app.on_event("startup")
async def startup_event():
    # Create DB tables if missing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database Tables Verified/Created")

    # Start ffprobe background worker (runs on the current event loop)
    try:
        start_ffprobe_worker()
        logger.info("✅ FFProbe worker started")
    except Exception as e:
        logger.warning("⚠️  Could not start FFProbe worker: %s", e)


@app.get("/")
async def root():
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} (HTTP + WebSockets) is Running"}


# Wrap FastAPI with Socket.IO ASGI app
# This allows /socket.io requests to be handled by socketio while other requests go to FastAPI
app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app, socketio_path="socket.io")


if __name__ == "__main__":
    # When run directly, start Uvicorn with the ASGI app (Socket.IO + FastAPI)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")