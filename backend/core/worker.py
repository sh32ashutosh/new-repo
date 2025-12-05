"""
Simple async background worker to run ffprobe on uploaded audio files and update DB records.

Usage:
- import enqueue_ffprobe(file_path, related_file_id=None, record_type="file_resource"|"live_chunk")
- On app startup call start_ffprobe_worker() to begin the consumer.
"""

import asyncio
import json
from typing import Optional
from pathlib import Path
import shlex

from backend.core.database import AsyncSessionLocal
from backend.db.models import AudioCache, FileResource, LiveChunk
from sqlalchemy.future import select

_ffprobe_queue: asyncio.Queue = asyncio.Queue()
_worker_task: Optional[asyncio.Task] = None


async def _run_ffprobe(path: str) -> Optional[dict]:
    # Returns parsed ffprobe JSON or None
    if not Path(path).exists():
        return None
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await proc.communicate()
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


async def _process_item(item: dict):
    """
    item: {
        "path": "/full/path",
        "related": {"type":"file_resource" or "live_chunk", "id": "<id>"},
    }
    """
    path = item.get("path")
    related = item.get("related")
    if not path:
        return
    info = await _run_ffprobe(path)
    if not info:
        return
    # extract duration and sample_rate (approx)
    duration = None
    sample_rate = None
    # try streams
    streams = info.get("streams") or []
    if streams:
        # choose first audio stream
        for s in streams:
            if s.get("codec_type") == "audio":
                sample_rate = int(s.get("sample_rate")) if s.get("sample_rate") else None
                break
    fmt = info.get("format") or {}
    if fmt.get("duration"):
        try:
            duration = int(float(fmt.get("duration")) * 1000)  # ms
        except Exception:
            duration = None

    # Store in AudioCache if a FileResource or update LiveChunk metadata
    async with AsyncSessionLocal() as db:
        if related and related.get("type") == "file_resource":
            # find file resource and update/create audio cache
            res = await db.execute(select(FileResource).where(FileResource.id == related.get("id")))
            f = res.scalars().first()
            if f:
                audio = AudioCache(filename=f.filename, file_path=str(path), duration_ms=duration, sample_rate=sample_rate, classroom_id=f.classroom_id)
                db.add(audio)
                await db.commit()
        elif related and related.get("type") == "live_chunk":
            res = await db.execute(select(LiveChunk).where(LiveChunk.id == related.get("id")))
            chunk = res.scalars().first()
            if chunk:
                chunk.file_size = Path(path).stat().st_size
                # optionally update codec/duration fields if needed
                await db.commit()


async def _consumer():
    while True:
        item = await _ffprobe_queue.get()
        try:
            await _process_item(item)
        except Exception:
            # swallow errors to keep worker alive
            pass
        finally:
            _ffprobe_queue.task_done()


def enqueue_ffprobe(path: str, related: Optional[dict] = None):
    """
    related example: {"type":"file_resource","id":"..."} or {"type":"live_chunk","id":"..."}
    """
    _ffprobe_queue.put_nowait({"path": path, "related": related})


def start_ffprobe_worker(loop: Optional[asyncio.AbstractEventLoop] = None):
    global _worker_task
    if _worker_task and not _worker_task.done():
        return
    loop = loop or asyncio.get_event_loop()
    _worker_task = loop.create_task(_consumer())
    return _worker_task