from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

# 🔄 IMPORTS
from backend.core.database import get_db
from backend.api.deps import get_current_user
# ⚡ ADDED: Enrollment needed for student queries
from backend.db.models import User, Assignment, Submission, SubmissionStatus, UserRole, Classroom, Enrollment

router = APIRouter()

# --- SCHEMAS ---
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    # total_points field added for frontend compatibility
    total_points: int = 10 
    classroom_id: str

class QuizSubmission(BaseModel):
    answers: dict 

# --- ROUTES ---

@router.get("/me")
async def get_my_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all assignments for the current user.
    - Teachers: Assignments they created.
    - Students: Assignments in classes they are enrolled in.
    """
    if current_user.role == UserRole.TEACHER:
        # Fetch assignments created by this teacher
        stmt = (
            select(Assignment)
            .join(Classroom)
            .where(Classroom.teacher_id == current_user.id)
            .options(selectinload(Assignment.submissions)) # Load submissions to check status
        )
    else:
        # Fetch assignments for classes student is enrolled in
        stmt = (
            select(Assignment)
            .join(Classroom)
            .join(Enrollment, Enrollment.classroom_id == Classroom.id)
            .where(Enrollment.user_id == current_user.id)
            .options(
                selectinload(Assignment.submissions.and_(Submission.student_id == current_user.id))
            )
        )

    result = await db.execute(stmt)
    assignments = result.scalars().all()

    # Format for Frontend
    data = []
    for a in assignments:
        # Determine status for Student
        status = "pending"
        score = None
        
        # Check if student has a submission for this assignment
        user_sub = next((s for s in a.submissions if s.student_id == current_user.id), None)
        
        if user_sub:
            status = "completed"
            score = user_sub.grade

        data.append({
            "id": a.id,
            "title": a.title,
            "details": a.description or "No description",
            "status": status,
            "score": score,
            "total": 10, # Mock total points for now
            "classroom_id": a.classroom_id
        })
    return data

@router.post("/create")
async def create_assignment(
    request: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can assign work.")

    result = await db.execute(select(Classroom).where(Classroom.id == request.classroom_id))
    classroom = result.scalars().first()
    if not classroom:
         raise HTTPException(status_code=404, detail="Classroom not found")

    new_assignment = Assignment(
        id=f"assign_{uuid.uuid4().hex[:8]}",
        classroom_id=request.classroom_id,
        title=request.title,
        description=request.description,
    )
    
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    
    return {"success": True, "id": new_assignment.id, "title": new_assignment.title}

@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str,
    quiz_data: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify Assignment
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # 2. Check if already submitted
    stmt = select(Submission).where(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    )
    existing = await db.execute(stmt)
    if existing.scalars().first():
        return {"success": False, "message": "You have already submitted this assignment."}

    # 3. Auto-Grade Logic (Mocked)
    score = "10" 
    
    # 4. Create Submission
    submission = Submission(
        id=f"sub_{uuid.uuid4().hex[:8]}",
        assignment_id=assignment_id,
        student_id=current_user.id,
        file_url=str(quiz_data.answers), 
        status=SubmissionStatus.GRADED,
        grade=score,
        submitted_at=datetime.utcnow()
    )
    
    db.add(submission)
    await db.commit()
    
    return {
        "success": True,
        "id": submission.id,
        "status": "graded",
        "grade": score,
        "message": f"Quiz submitted! Score: {score}/10"
    }