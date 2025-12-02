from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Classroom, ClassStatus

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
    
    return {"success": True, "status": "live", "message": "Class is now LIVE"}

@router.post("/{class_id}/end")
async def end_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Switches class status to COMPLETED.
    Triggered when Teacher clicks 'Leave Class' or ends session.
    """
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalars().first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")

    if classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can end the class")

    classroom.status = ClassStatus.COMPLETED
    await db.commit()
    
    return {"success": True, "status": "completed", "message": "Class session ended"}