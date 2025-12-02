from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Any

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Classroom, Enrollment, ClassStatus, UserRole

router = APIRouter()

# ⚡ FIX: Use empty string "" to match "/api/dashboard" exactly (no trailing slash)
@router.get("")
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # ... (Keep your existing logic for fetching classes/stats) ...
    # 1. Fetch Classes based on Role
    if current_user.role == UserRole.TEACHER:
        stmt = (
            select(Classroom)
            .where(Classroom.teacher_id == current_user.id)
            .options(
                selectinload(Classroom.assignments), 
                selectinload(Classroom.students)
            )
        )
    else:
        stmt = (
            select(Classroom)
            .join(Enrollment)
            .where(Enrollment.user_id == current_user.id)
            .options(
                selectinload(Classroom.assignments), 
                selectinload(Classroom.teacher),
                selectinload(Classroom.students)
            )
        )

    result = await db.execute(stmt)
    classes = result.scalars().all()

    # 2. Calculate Stats
    formatted_classes = []
    all_assignments = []
    live_count = 0
    upcoming_count = 0

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
            "teacher": c.teacher.full_name if c.teacher else "Unknown",
            "participants": len(c.students)
        })

        for a in c.assignments:
            all_assignments.append({
                "id": a.id,
                "title": a.title,
                "class_title": c.title,
                "status": "pending"
            })

    # 3. Return Payload
    return {
        "dashboard": {
            "live": live_count,
            "upcoming": upcoming_count,
            "completed": 0,
            "pending": len(all_assignments)
        },
        "classes": formatted_classes,
        "assignments": all_assignments,
        "files": [],
        "discussions": []
    }