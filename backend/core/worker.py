"""
Async background worker to:
1. Run ffprobe on uploaded audio files and update DB records.
2. Merge live streaming chunks (audio/video) into a final MP4 recording.

Usage:
- import enqueue_ffprobe(file_path, related={"type":..., "id":...})
- import enqueue_recording_merge(classroom_id)
- On app startup call start_ffprobe_worker() to begin the consumer.
"""

import asyncio
import json
import os
from typing import Optional
from pathlib import Path
from datetime import datetime

from backend.core.database import AsyncSessionLocal
from backend.db.models import AudioCache, FileResource, LiveChunk
from sqlalchemy.future import select

# Directory setup
RECORDINGS_DIR = Path("uploads") / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_LISTS_DIR = RECORDINGS_DIR / "temp"
TEMP_LISTS_DIR.mkdir(parents=True, exist_ok=True)

# --- FFprobe Worker Logic ---
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
    streams = info.get("streams") or []
    if streams:
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

    # Update DB
    async with AsyncSessionLocal() as db:
        if related and related.get("type") == "file_resource":
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
                # Update file size
                try:
                    chunk.file_size = Path(path).stat().st_size
                except:
                    pass
                await db.commit()


async def _consumer():
    while True:
        item = await _ffprobe_queue.get()
        try:
            await _process_item(item)
        except Exception:
            pass
        finally:
            _ffprobe_queue.task_done()


def enqueue_ffprobe(path: str, related: Optional[dict] = None):
    _ffprobe_queue.put_nowait({"path": path, "related": related})


def start_ffprobe_worker(loop: Optional[asyncio.AbstractEventLoop] = None):
    global _worker_task
    if _worker_task and not _worker_task.done():
        return
    loop = loop or asyncio.get_event_loop()
    _worker_task = loop.create_task(_consumer())
    return _worker_task


# --- NEW: Recording Merge Logic (Video + Audio) ---

async def enqueue_recording_merge(classroom_id: str):
    """
    1. Fetches all chunks (video/audio) for the classroom.
    2. Creates file lists for ffmpeg concat.
    3. Merges them into a single .mp4 file.
    4. Saves the result as a FileResource in the DB.
    """
    print(f"[Worker] Starting recording merge for {classroom_id}...")
    
    async with AsyncSessionLocal() as db:
        # Fetch chunks sorted by sequence
        stmt = select(LiveChunk).where(LiveChunk.classroom_id == classroom_id).order_by(LiveChunk.seq)
        result = await db.execute(stmt)
        chunks = result.scalars().all()
        
        if not chunks:
            print(f"[Worker] No chunks found for {classroom_id}")
            return

        # Separate by type
        # We ensure paths are absolute string paths
        video_chunks = [c for c in chunks if c.chunk_type == 'video' and c.file_path]
        audio_chunks = [c for c in chunks if c.chunk_type == 'audio' and c.file_path]

        if not video_chunks and not audio_chunks:
            return

        # Create temporary input files for FFmpeg concat demuxer
        vid_list_path = TEMP_LISTS_DIR / f"{classroom_id}_vid.txt"
        aud_list_path = TEMP_LISTS_DIR / f"{classroom_id}_aud.txt"
        
        # Helper to write list
        def write_list(file_path, chunk_list):
            with open(file_path, "w") as f:
                for c in chunk_list:
                    # FFmpeg concat requires 'file path' format
                    # Resolving to absolute path is safer
                    abs_path = Path(c.file_path).resolve()
                    f.write(f"file '{abs_path}'\n")

        has_video = len(video_chunks) > 0
        has_audio = len(audio_chunks) > 0

        if has_video:
            write_list(vid_list_path, video_chunks)
        if has_audio:
            write_list(aud_list_path, audio_chunks)

        # Output file
        filename = f"recording_{classroom_id}_{int(datetime.utcnow().timestamp())}.mp4"
        output_path = RECORDINGS_DIR / filename
        
        # Build FFmpeg command
        # Syntax: ffmpeg -f concat -safe 0 -i vid.txt -f concat -safe 0 -i aud.txt ...
        cmd = ["ffmpeg", "-y"]
        
        if has_video:
            cmd.extend(["-f", "concat", "-safe", "0", "-i", str(vid_list_path)])
        if has_audio:
            cmd.extend(["-f", "concat", "-safe", "0", "-i", str(aud_list_path)])
            
        # Encoding arguments
        # We copy video (fast) and AAC encode audio (compatible)
        if has_video and has_audio:
            # map 0:v and 1:a
            cmd.extend(["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", str(output_path)])
        elif has_video:
            cmd.extend(["-c:v", "copy", str(output_path)])
        elif has_audio:
            cmd.extend(["-c:a", "aac", str(output_path)])

        # Execute
        print(f"[Worker] Running FFmpeg: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await proc.communicate()

        if proc.returncode != 0:
            print(f"[Worker] FFmpeg failed: {err.decode()}")
            # Cleanup lists
            if vid_list_path.exists(): vid_list_path.unlink()
            if aud_list_path.exists(): aud_list_path.unlink()
            return

        print(f"[Worker] Recording created successfully: {output_path}")

        # Save to DB
        file_size = output_path.stat().st_size
        new_file = FileResource(
            classroom_id=classroom_id,
            filename=filename,
            file_path=str(output_path),
            file_size=str(file_size),
            file_type="video/mp4",
            is_offline_ready=True
        )
        db.add(new_file)
        await db.commit()

        # Cleanup temp lists
        if vid_list_path.exists(): vid_list_path.unlink()
        if aud_list_path.exists(): aud_list_path.unlink()