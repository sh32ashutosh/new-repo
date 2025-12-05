import json
import aiofiles
from pathlib import Path
from datetime import datetime

from backend.core.socket_manager import sio
from backend.core.security import decode_access_token
from backend.core.database import AsyncSessionLocal
from backend.db.models import LiveChunk, EventLog, User
from backend.core.worker import enqueue_ffprobe

# directory for live chunk files
LIVE_CHUNKS_DIR = Path("uploads") / "live_chunks"
LIVE_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)


def _extract_token_from_environ(environ: dict) -> str | None:
    # socketio client may send token in query string: ?token=...
    qs = environ.get("QUERY_STRING", "")
    for part in qs.split("&"):
        if part.startswith("token="):
            return part.split("=", 1)[1]
    # Alternatively, handshake headers may contain Authorization
    headers = environ.get("asgi.scope", {}) or environ.get("headers", [])
    # headers is list of [name, value] pairs in bytes, try to parse
    try:
        for name, val in environ.get("headers", []):
            if name.decode().lower() == "authorization":
                v = val.decode()
                if v.lower().startswith("bearer "):
                    return v.split(" ", 1)[1]
    except Exception:
        pass
    return None


@sio.event
async def connect(sid, environ):
    """
    Authenticate on handshake. Expect token in query string or Authorization header.
    Reject connection by returning False on invalid token.
    """
    token = _extract_token_from_environ(environ)
    if not token:
        # reject connection
        return False
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
    except Exception:
        return False
    # fetch user id and attach to session
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.username == username))
        user = res.scalars().first()
        if not user:
            return False
        await sio.save_session(sid, {"username": username, "user_id": user.id})
    print("Socket connected:", sid, "user:", username)
    return True


@sio.event
async def disconnect(sid):
    print("Socket disconnected:", sid)


@sio.on("join_class")
async def on_join_class(sid, data):
    # data expected: {"classroom_id": "<id>"}
    room = data.get("classroom_id")
    if room:
        await sio.save_session(sid, {"room": room})
        await sio.enter_room(sid, room)
        await sio.emit("joined_class", {"room": room}, room=sid)


# Audio chunk event (binary or base64 frames with metadata)
# protocol specified below in the "Audio-chunk protocol" block.
@sio.on("audio_chunk")
async def on_audio_chunk(sid, payload):
    """
    payload expected as dict:
    {
        "classroom_id": "<id>",
        "seq": <int>,
        "timestamp_ms": <int>,
        "codec": "opus",
        "binary": <bytes> OR "base64": "<...>" (prefer binary)
    }
    """
    session = await sio.get_session(sid)
    room = session.get("room")
    user_id = session.get("user_id")
    classroom_id = payload.get("classroom_id") or room
    seq = payload.get("seq")
    codec = payload.get("codec", "opus")
    timestamp_ms = payload.get("timestamp_ms")
    data = payload.get("binary") or payload.get("base64")

    if not classroom_id or seq is None or data is None:
        # ignore malformed
        return

    # If binary bytes delivered by socketio python client, data is bytes
    raw_bytes = None
    if isinstance(data, (bytes, bytearray)):
        raw_bytes = bytes(data)
    elif isinstance(data, str):
        import base64
        try:
            raw_bytes = base64.b64decode(data)
        except Exception:
            return
    else:
        return

    # persist chunk file asynchronously and create LiveChunk record
    filename = f"{classroom_id}_{seq}_{int(datetime.utcnow().timestamp()*1000)}.opus"
    dest_path = LIVE_CHUNKS_DIR / classroom_id
    dest_path.mkdir(parents=True, exist_ok=True)
    full_path = dest_path / filename

    try:
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(raw_bytes)
    except Exception:
        return

    # DB insert LiveChunk
    async with AsyncSessionLocal() as db:
        chunk = LiveChunk(classroom_id=classroom_id, sender_id=user_id, seq=seq, timestamp_ms=timestamp_ms, codec=codec, file_path=str(full_path))
        db.add(chunk)
        await db.commit()
        await db.refresh(chunk)
        # enqueue ffprobe to collect size/duration if desired
        enqueue_ffprobe(str(full_path), related={"type": "live_chunk", "id": chunk.id})

    # Broadcast to room (re-broadcast metadata; clients can fetch stream chunks via socket or HTTP)
    await sio.emit("audio_chunk_broadcast", {"classroom_id": classroom_id, "seq": seq, "sender_id": user_id, "codec": codec, "timestamp_ms": timestamp_ms}, room=classroom_id)


# Pen strokes / coord events -> store EventLog and broadcast
@sio.on("pen_event")
async def on_pen_event(sid, payload):
    """
    payload expected:
    {
        "classroom_id": "...",
        "event_type": "pen" | "coords" | "slide",
        "payload": { ... }  # JSON-serializable pen stroke / coords
    }
    """
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    classroom_id = payload.get("classroom_id") or session.get("room")
    event_type = payload.get("event_type") or "pen"
    event_payload = payload.get("payload")
    if not classroom_id or event_payload is None:
        return

    # persist event
    async with AsyncSessionLocal() as db:
        ev = EventLog(classroom_id=classroom_id, sender_id=user_id, event_type=event_type, payload=event_payload)
        db.add(ev)
        await db.commit()
        await db.refresh(ev)

    # broadcast to room
    await sio.emit("pen_event_broadcast", {"id": ev.id, "classroom_id": classroom_id, "event_type": event_type, "payload": event_payload}, room=classroom_id)