import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException
from pathlib import Path
from sqlalchemy.future import select

from backend.api.deps import get_current_user
from backend.core.database import AsyncSessionLocal
from backend.db.models import FileResource, AudioCache
from backend.core.worker import enqueue_ffprobe

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_upload_file_async(upload_file: UploadFile, dest_path: Path):
    # async streaming write
    async with aiofiles.open(dest_path, "wb") as out_file:
        while True:
            chunk = await upload_file.read(1024 * 64)
            if not chunk:
                break
            await out_file.write(chunk)
    # ensure upload_file file is closed
    try:
        await upload_file.close()
    except Exception:
        pass


@router.post("/upload")
async def upload_file(classroom_id: str = Query(...), upload_file: UploadFile = File(...), current_user=Depends(get_current_user)):
    # Save file asynchronously
    dest = UPLOAD_DIR / upload_file.filename
    # avoid overwriting: if exists, append uuid
    if dest.exists():
        from uuid import uuid4
        dest = UPLOAD_DIR / f"{uuid4().hex}_{upload_file.filename}"
    await save_upload_file_async(upload_file, dest)

    # Create DB record (async)
    async with AsyncSessionLocal() as db:
        file_record = FileResource(
            classroom_id=classroom_id,
            filename=dest.name,
            file_path=str(dest),
            file_size=str(dest.stat().st_size),
            file_type=upload_file.content_type or "application/octet-stream",
            is_offline_ready=False,
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

    # enqueue ffprobe job to extract audio metadata (non-blocking)
    if upload_file.content_type and upload_file.content_type.startswith("audio"):
        enqueue_ffprobe(str(dest), related={"type": "file_resource", "id": file_record.id})

    return file_record


@router.get("/")
async def list_files(classroom_id: str | None = None):
    async with AsyncSessionLocal() as db:
        if classroom_id:
            result = await db.execute(select(FileResource).where(FileResource.classroom_id == classroom_id))
        else:
            result = await db.execute(select(FileResource))
        return result.scalars().all()