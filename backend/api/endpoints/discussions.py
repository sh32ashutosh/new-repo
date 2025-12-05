from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

# 🔄 FIX: backend -> backend
from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Discussion, Classroom

router = APIRouter()

# --- SCHEMAS ---
class PostCreate(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: str
    user: str
    text: str
    time: str
    is_me: bool

# --- ROUTES ---

@router.get("/class/{class_id}", response_model=List[PostResponse])
async def get_discussions(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches the classroom chat feed (Real DB).
    """
    stmt = (
        select(DiscussionPost)
        .where(DiscussionPost.classroom_id == class_id)
        .order_by(DiscussionPost.created_at.asc())
        .options(selectinload(DiscussionPost.author))
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    response_data = []
    for p in posts:
        author_name = p.author.full_name if p.author else "Unknown User"
        response_data.append({
            "id": p.id,
            "user": author_name,
            "text": p.content,
            "time": p.created_at.strftime("%H:%M"),
            "is_me": p.user_id == current_user.id
        })
        
    return response_data

@router.post("/class/{class_id}")
async def create_post(
    class_id: str,
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves a new message to the classroom feed.
    """
    # Verify class exists
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalars().first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    new_post = DiscussionPost(
        id=str(uuid.uuid4()),
        classroom_id=class_id,
        user_id=current_user.id,
        content=post_data.content,
        created_at=datetime.utcnow()
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return {
        "success": True,
        "post": {
            "id": new_post.id,
            "user": current_user.full_name,
            "text": new_post.content,
            "time": new_post.created_at.strftime("%H:%M"),
            "is_me": True
        }
    }