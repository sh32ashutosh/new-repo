from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
import shutil
import uuid
from datetime import datetime

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, FileResource, Classroom, UserRole

router = APIRouter()

# Local storage for the Hackathon (In production, use AWS S3)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resource(
    file: UploadFile = File(...),
    classroom_id: str = Form(...), # Required by DB Schema
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handles generic file uploads for Class Resources.
    Expects FormData: { "file": (binary), "classroom_id": "uuid" }
    """
    # 1. Validation
    # Ensure user has access to this classroom (Teacher or Student)
    # For hackathon, we skip strict permission checks for speed, 
    # but normally we'd check Enrollment or Ownership.
    
    # 2. Save File Physically
    # Generate unique filename to prevent overwrites
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Create DB Entry
    file_size_mb = f"{round(file.size / 1024 / 1024, 2)} MB" if file.size else "Unknown"
    
    new_file = FileResource(
        classroom_id=classroom_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size_mb,
        file_type=file.content_type,
        is_offline_ready=False # Default
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
    # current_user check removed to allow easier downloading/caching 
    # for Service Workers (PWA) in this prototype phase
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