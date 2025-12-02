from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import random
import string
import uuid

# 🔄 FIX: Ensure correct imports
from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Classroom, Enrollment, UserRole, ClassStatus

router = APIRouter()

# --- SCHEMAS ---
class CreateClassRequest(BaseModel):
    title: str

class JoinClassRequest(BaseModel):
    code: str

# --- ROUTES ---

@router.post("/create")
async def create_classroom(
    request: CreateClassRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Permission Check
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only teachers can create classes"
        )

    # 2. Generate Unique Code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # 3. Insert into DB with UUID
    new_class = Classroom(
        id=str(uuid.uuid4()), # ⚡ Use UUID
        title=request.title,
        code=code,
        teacher_id=current_user.id,
        status=ClassStatus.UPCOMING
    )
    db.add(new_class)
    await db.commit()
    await db.refresh(new_class)
    
    return {
        "success": True, 
        "id": new_class.id, 
        "title": new_class.title,
        "code": new_class.code,
        "status": new_class.status
    }

@router.post("/join")
async def join_classroom(
    request: JoinClassRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find Class
    result = await db.execute(select(Classroom).where(Classroom.code == request.code))
    classroom = result.scalars().first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Invalid Class Code")
        
    if classroom.teacher_id == current_user.id:
        return {"success": True, "message": "You are the teacher of this class", "classId": classroom.id}

    # 2. Check Existing Enrollment
    stmt = select(Enrollment).where(
        Enrollment.user_id == current_user.id,
        Enrollment.classroom_id == classroom.id
    )
    existing = await db.execute(stmt)
    if existing.scalars().first():
        return {"success": True, "message": "Already enrolled", "classId": classroom.id}
        
    # 3. Enroll
    enrollment = Enrollment(user_id=current_user.id, classroom_id=classroom.id)
    db.add(enrollment)
    await db.commit()
    
    return {"success": True, "classId": classroom.id}

@router.get("/{class_id}")
async def get_classroom_details(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Load teacher and students to prevent NoneType errors
    stmt = (
        select(Classroom)
        .where(Classroom.id == class_id)
        .options(selectinload(Classroom.teacher), selectinload(Classroom.students))
    )
    result = await db.execute(stmt)
    classroom = result.scalars().first()

    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")

    return {
        "id": classroom.id,
        "title": classroom.title,
        "code": classroom.code,
        "status": classroom.status,
        "teacher": {
            "id": classroom.teacher.id,
            "name": classroom.teacher.full_name
        },
        "is_teacher": classroom.teacher_id == current_user.id
    }