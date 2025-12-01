import sys
import os

# 1. PATH FIX: Add the parent directory to sys.path
# This ensures "from backend.core..." works even if you run this file directly from the backend folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api.router import api_router

# Import Socket Manager
from backend.core.socket_manager import sio
# CRITICAL: Import the event handlers so they are registered with the 'sio' instance
import backend.api.sockets 

# 2. Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# 3. Configure CORS
# This allows your React app (typically on localhost:5173) to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount API Routes
# This connects Auth, Dashboard, Classes, Assignments, Files, etc.
app.include_router(api_router, prefix=settings.API_STR)

# 5. Database Startup Event
# Automatically creates the strict schema tables in vlink.db on boot
@app.on_event("startup")
async def init_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Tables Verified/Created")

@app.get("/")
async def root():
    return {"status": "ok", "message": "vLink Hybrid Backend (HTTP + WebSockets) is Running"}

# 6. WRAP FASTAPI WITH SOCKET.IO
# This wrapper intercepts requests to /socket.io/ and handles them via the 'sio' instance.
# All other requests are passed through to the 'app' (FastAPI).
app = socketio.ASGIApp(sio, app)

# 7. Debug Runner
if __name__ == "__main__":
    # Note: We pass the 'app' object directly, not the string "backend.main:app"
    # because 'app' is now a SocketIO ASGI wrapper.
    # If using 'secure: true' in frontend, consider adding ssl_keyfile/ssl_certfile here.
    uvicorn.run(app, host="0.0.0.0", port=8000)