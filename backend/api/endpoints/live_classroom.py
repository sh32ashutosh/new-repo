from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Classroom, ClassStatus
# You will need to ensure this function exists in your worker file
from backend.core.worker import enqueue_recording_merge 

router = APIRouter()

@router.post("/{class_id}/start")
async def start_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Switches class status to LIVE. 
    Triggered when Teacher enters LiveClassroom.jsx.
    """
    # 1. Fetch Class
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalars().first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")

    # 2. Verify Ownership
    if classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can start the class")

    # 3. Update Status
    classroom.status = ClassStatus.LIVE
    await db.commit()
    
    return {
        "success": True, 
        "status": "live", 
        "url": f"/classroom/{class_id}/live",
        "message": "Class is now LIVE"
    }

@router.post("/{class_id}/end")
async def end_class(
    class_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Switches class status to COMPLETED and triggers recording generation.
    """
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalars().first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")

    if classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can end the class")

    # 1. Update Status
    classroom.status = ClassStatus.COMPLETED
    await db.commit()

    # 2. Trigger FFmpeg Merge Task
    # This runs in the background so the teacher gets an immediate "Class Ended" response.
    background_tasks.add_task(enqueue_recording_merge, class_id)
    
    return {
        "success": True, 
        "status": "completed", 
        "message": "Class session ended. Recording is being processed."
    }