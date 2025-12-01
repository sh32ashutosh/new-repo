from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Assignment, Submission, SubmissionStatus, UserRole

router = APIRouter()

# --- SCHEMAS ---
class QuizSubmission(BaseModel):
    answers: dict # e.g. {"q1": "3.14"}

class SubmissionResponse(BaseModel):
    id: str
    status: str
    grade: Optional[int]
    message: str

# --- ROUTES ---

@router.get("/")
async def get_my_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns assignments specific to the student's enrolled classes.
    """
    # Logic similar to dashboard, but focused on the Assignment list view
    # In a real app, we would join Enrollment -> Classroom -> Assignment
    # For now, we reuse the robust logic via the dashboard aggregation or build a direct query
    # This is a placeholder for the specific list view if you expand beyond dashboard
    return {"message": "Use /api/dashboard for the main list for now, or implement specific pagination here."}

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

    # 3. Auto-Grade Logic (Mocked as 10/10 per your React toast)
    # In reality, you'd compare quiz_data.answers with a stored answer key
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
        "status": submission.status,
        "grade": score,
        "message": f"Quiz submitted! Score: {score}/{assignment.total_points or 10}"
    }

# --- TUS.IO / FILE UPLOAD PREP ---
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Standard upload handler. 
    If using TUS.io client-side, we need a dedicated TUS server implementation 
    (handling PATCH/HEAD/OFFSET).
    This is a fallback for standard multipart uploads.
    """
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": file_path, "filename": file.filename}