import json
import base64
import asyncio
import logging
import aiofiles
from pathlib import Path
from datetime import datetime

# SQLAlchemy imports
from sqlalchemy.future import select

# Backend imports
from backend.core.socket_manager import sio
from backend.core.security import decode_access_token
from backend.core.database import AsyncSessionLocal
from backend.db.models import LiveChunk, EventLog, User
from backend.core.worker import enqueue_ffprobe

# Setup Directories
UPLOAD_DIR = Path("uploads")
LIVE_AUDIO_DIR = UPLOAD_DIR / "live_audio"
LIVE_VIDEO_DIR = UPLOAD_DIR / "live_video"

LIVE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
LIVE_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

def _extract_token_from_environ(environ: dict) -> str | None:
    qs = environ.get("QUERY_STRING", "")
    for part in qs.split("&"):
        if part.startswith("token="):
            return part.split("=", 1)[1]
    try:
        for name, val in environ.get("headers", []):
            if name.decode().lower() == "authorization":
                v = val.decode()
                if v.lower().startswith("bearer "):
                    return v.split(" ", 1)[1]
    except Exception:
        pass
    return None

async def _persist_chunk(chunk_type, classroom_id, user_id, seq, timestamp_ms, codec, raw_bytes):
    """
    Unified background task to handle I/O for both Audio and Video.
    """
    try:
        # Determine paths based on type
        if chunk_type == "video":
            # standard extension for raw x264/h264 streams
            ext = "h264" 
            dest_dir = LIVE_VIDEO_DIR
        else:
            ext = "opus"
            dest_dir = LIVE_AUDIO_DIR

        filename = f"{classroom_id}_{seq}_{int(datetime.utcnow().timestamp()*1000)}.{ext}"
        room_dir = dest_dir / classroom_id
        room_dir.mkdir(parents=True, exist_ok=True)
        full_path = room_dir / filename

        # 1. Write File (Async I/O)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(raw_bytes)

        # 2. DB Insert
        async with AsyncSessionLocal() as db:
            chunk = LiveChunk(
                classroom_id=classroom_id, 
                sender_id=user_id, 
                seq=seq, 
                timestamp_ms=timestamp_ms, 
                codec=codec, 
                # Ensure your DB model has a 'chunk_type' column or similar
                chunk_type=chunk_type, 
                file_path=str(full_path)
            )
            db.add(chunk)
            await db.commit()
            
            # Enqueue ffprobe for metadata analysis
            enqueue_ffprobe(str(full_path), related={"type": f"live_{chunk_type}", "id": chunk.id})
            
    except Exception as e:
        logger.error(f"Failed to persist {chunk_type} chunk {seq} for room {classroom_id}: {e}")

@sio.event
async def connect(sid, environ):
    token = _extract_token_from_environ(environ)
    if not token:
        return False
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
    except Exception:
        return False
        
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.username == username))
        user = res.scalars().first()
        if not user:
            return False
        await sio.save_session(sid, {"username": username, "user_id": user.id})
    
    print(f"Socket connected: {sid} user: {username}")
    return True

@sio.event
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

@sio.on("join_class")
async def on_join_class(sid, data):
    room = data.get("classroom_id")
    if room:
        await sio.save_session(sid, {"room": room})
        await sio.enter_room(sid, room)
        await sio.emit("joined_class", {"room": room}, room=sid)

async def handle_media_chunk(sid, payload, media_type):
    """
    Generic handler for Audio/Video to reduce code duplication.
    """
    session = await sio.get_session(sid)
    room = session.get("room")
    user_id = session.get("user_id")
    classroom_id = payload.get("classroom_id") or room
    
    if not classroom_id:
        return

    seq = payload.get("seq")
    timestamp_ms = payload.get("timestamp_ms")
    data = payload.get("binary") or payload.get("base64")
    
    # Defaults
    if media_type == "video":
        codec = payload.get("codec", "h264")
    else:
        codec = payload.get("codec", "opus")

    if seq is None or data is None:
        return

    # Decode Data
    raw_bytes = None
    if isinstance(data, (bytes, bytearray)):
        raw_bytes = bytes(data)
    elif isinstance(data, str):
        try:
            raw_bytes = base64.b64decode(data)
        except Exception:
            return
    else:
        return

    # 1. BROADCAST IMMEDIATELY (Real-time Priority)
    # Clients rely on timestamp_ms to sync audio/video
    event_name = f"{media_type}_chunk_broadcast"
    await sio.emit(event_name, {
        "classroom_id": classroom_id, 
        "seq": seq, 
        "sender_id": user_id, 
        "codec": codec, 
        "timestamp_ms": timestamp_ms
    }, room=classroom_id)

    # 2. PERSIST IN BACKGROUND (Data Integrity)
    # This ensures the loop is not blocked by file I/O
    sio.start_background_task(
        _persist_chunk, 
        media_type, classroom_id, user_id, seq, timestamp_ms, codec, raw_bytes
    )

@sio.on("audio_chunk")
async def on_audio_chunk(sid, payload):
    await handle_media_chunk(sid, payload, "audio")

@sio.on("video_chunk")
async def on_video_chunk(sid, payload):
    await handle_media_chunk(sid, payload, "video")

@sio.on("pen_event")
async def on_pen_event(sid, payload):
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    classroom_id = payload.get("classroom_id") or session.get("room")
    event_type = payload.get("event_type") or "pen"
    event_payload = payload.get("payload")
    
    if not classroom_id or event_payload is None:
        return

    # Broadcast FIRST
    await sio.emit("pen_event_broadcast", {
        "sender_id": user_id,
        "classroom_id": classroom_id, 
        "event_type": event_type, 
        "payload": event_payload
    }, room=classroom_id)

    # Persist Background
    async def _persist_pen_event():
        async with AsyncSessionLocal() as db:
            ev = EventLog(classroom_id=classroom_id, sender_id=user_id, event_type=event_type, payload=event_payload)
            db.add(ev)
            await db.commit()
            
    sio.start_background_task(_persist_pen_event)