from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
import shutil
import uuid
from datetime import datetime

# 🔄 FIX: Correct imports to prevent "Table defined" error
from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, FileResource, Classroom, UserRole

router = APIRouter()

# Local storage (Tus.io destination)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resource(
    file: UploadFile = File(...),
    classroom_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handles file uploads.
    """
    # 1. Save File Physically
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Create DB Entry
    size_mb = f"{round(file.size / 1024 / 1024, 2)} MB" if file.size else "Unknown"

    new_file = FileResource(
        id=str(uuid.uuid4()),
        classroom_id=classroom_id,
        filename=file.filename,
        file_path=file_path,
        file_size=size_mb,
        file_type=file.content_type,
        is_offline_ready=False,
        uploaded_at=datetime.utcnow()
    )
    
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    
    return {
        "success": True,
        "file": {
            "id": new_file.id,
            "name": new_file.filename,
            "size": new_file.file_size,
            "url": f"/api/files/download/{new_file.id}",
            "offline": new_file.is_offline_ready
        }
    }

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Serves the physical file.
    """
    result = await db.execute(select(FileResource).where(FileResource.id == file_id))
    file_record = result.scalars().first()
    
    if not file_record or not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_record.file_path, 
        filename=file_record.filename,
        media_type=file_record.file_type
    )