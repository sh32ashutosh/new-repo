from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.future import select

from backend.core.database import AsyncSessionLocal
from backend.db.models import LiveChunk, EventLog
from pathlib import Path

router = APIRouter()


@router.get("/chunks/{classroom_id}")
async def list_chunks(classroom_id: str, limit: int = 100):
    """
    List recent LiveChunk metadata for a classroom (ordered by seq desc).
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(LiveChunk).where(LiveChunk.classroom_id == classroom_id).order_by(LiveChunk.seq.desc()).limit(limit))
        return result.scalars().all()


@router.get("/chunk/file/{chunk_id}")
async def download_chunk(chunk_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(LiveChunk).where(LiveChunk.id == chunk_id))
        chunk = result.scalars().first()
        if not chunk or not chunk.file_path:
            raise HTTPException(status_code=404, detail="Chunk not found")
        p = Path(chunk.file_path)
        if not p.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path=str(p), filename=p.name, media_type="application/octet-stream")


@router.get("/events/{classroom_id}")
async def list_events(classroom_id: str, limit: int = 200):
    """
    List recent EventLog entries for a classroom (pen strokes / slides / coords)
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EventLog).where(EventLog.classroom_id == classroom_id).order_by(EventLog.created_at.desc()).limit(limit))
        return result.scalars().all()