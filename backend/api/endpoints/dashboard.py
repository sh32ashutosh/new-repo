from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Classroom, Enrollment, Assignment, ClassStatus, UserRole

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggregates data for the PWA Dashboard.
    Matches the structure expected by React Dashboard.jsx exactly.
    """
    
    # 1. Fetch Classes with related data (Teacher Name & Students)
    if current_user.role == UserRole.TEACHER:
        # Teacher: Get classes created by them
        result = await db.execute(
            select(Classroom)
            .where(Classroom.teacher_id == current_user.id)
            .options(
                selectinload(Classroom.assignments),
                selectinload(Classroom.teacher),  # Load teacher name
                selectinload(Classroom.students)  # Load students for count
            )
        )
        classes = result.scalars().all()
    else:
        # Student: Get classes they are enrolled in
        result = await db.execute(
            select(Classroom)
            .join(Enrollment)
            .where(Enrollment.user_id == current_user.id)
            .options(
                selectinload(Classroom.assignments),
                selectinload(Classroom.teacher),
                selectinload(Classroom.students)
            )
        )
        classes = result.scalars().all()

    # 2. Extract Assignments & Stats
    all_assignments = []
    live_count = 0
    upcoming_count = 0
    
    formatted_classes = []

    for c in classes:
        if c.status == ClassStatus.LIVE:
            live_count += 1
        elif c.status == ClassStatus.UPCOMING:
            upcoming_count += 1
            
        formatted_classes.append({
            "id": c.id,
            "title": c.title,
            "code": c.code,
            "status": c.status,
            # FIXED: React expects "teacher" name, not ID
            "teacher": c.teacher.full_name if c.teacher else "Unknown", 
            # FIXED: React expects participant count
            "participants": len(c.students) 
        })

        for a in c.assignments:
            all_assignments.append({
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "due_date": a.due_date,
                "class_title": c.title,
                "status": "pending"
            })

    # 3. Construct Payload
    return {
        "dashboard": {
            "live": live_count,
            "upcoming": upcoming_count,
            "completed": 0, 
            "pending": len(all_assignments) # FIXED: Key name "pending" matches React
        },
        "classes": formatted_classes,
        "assignments": all_assignments,
        "files": [], 
        "discussions": []
    }