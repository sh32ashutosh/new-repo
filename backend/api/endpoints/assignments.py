from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Assignment, Submission, SubmissionStatus, UserRole

router = APIRouter()

# --- SCHEMAS ---
class CreateAssignmentSchema(BaseModel):
    classroom_id: str
    title: str
    description: Optional[str] = None
    total_points: int = 10

class QuizSubmission(BaseModel):
    answers: dict # e.g. {"q1": "3.14"}

# --- ROUTES ---

@router.post("/create")
async def create_assignment(
    request: CreateAssignmentSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Teacher creates a new assignment for a class.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")

    new_assignment = Assignment(
        classroom_id=request.classroom_id,
        title=request.title,
        description=request.description,
        total_points=request.total_points,
        updated_at=None # Allow DB default
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
    """
    Handles the 'Submit Quiz' action from Assignments.jsx
    """
    # 1. Verify Assignment Exists
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

    # 3. Auto-Grade Logic (Mocked logic matches your React toast "Score: 10/10")
    # In a real app, you would validate quiz_data.answers against a key
    score = 10 
    
    # 4. Create Submission
    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=str(quiz_data.answers),
        status=SubmissionStatus.GRADED, # Auto-graded
        grade=score
    )
    
    db.add(submission)
    await db.commit()
    
    return {
        "success": True,
        "id": submission.id,
        "status": submission.status.value,
        "grade": score,
        "message": f"Quiz submitted! Score: {score}/{assignment.total_points or 10}"
    }

# --- FILE UPLOAD (Tus.io Placeholder) ---
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Standard upload handler. 
    This serves as the endpoint for file submissions if you aren't using a dedicated TUS server yet.
    """
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": file_path, "filename": file.filename}