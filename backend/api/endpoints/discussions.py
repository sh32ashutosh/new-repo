from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List

from backend.core.database import get_db
from backend.api.deps import get_current_user
from backend.db.models import User, Discussion, DiscussionReply, Classroom

router = APIRouter()

# --- SCHEMAS ---
class DiscussionCreate(BaseModel):
    classroom_id: str
    title: str
    content: str

class ReplyCreate(BaseModel):
    content: str

class DiscussionResponse(BaseModel):
    id: str
    title: str
    content: str
    author: str
    replies: int
    created_at: str

# --- ROUTES ---

@router.post("/create", response_model=DiscussionResponse)
async def create_discussion(
    post: DiscussionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new discussion thread in a specific classroom.
    """
    # 1. Check Class Exists
    result = await db.execute(select(Classroom).where(Classroom.id == post.classroom_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 2. Create Thread
    new_discussion = Discussion(
        classroom_id=post.classroom_id,
        author_id=current_user.id,
        title=post.title,
        content=post.content
    )
    
    db.add(new_discussion)
    await db.commit()
    await db.refresh(new_discussion)
    
    return {
        "id": new_discussion.id,
        "title": new_discussion.title,
        "content": new_discussion.content,
        "author": current_user.full_name,
        "replies": 0,
        "created_at": new_discussion.created_at.strftime("%Y-%m-%d")
    }

@router.get("/class/{classroom_id}", response_model=List[DiscussionResponse])
async def get_class_discussions(
    classroom_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches all discussions for a specific class.
    Includes Author Name and Reply Count.
    """
    stmt = (
        select(Discussion)
        .where(Discussion.classroom_id == classroom_id)
        .options(selectinload(Discussion.author), selectinload(Discussion.replies))
        .order_by(Discussion.created_at.desc())
    )
    
    result = await db.execute(stmt)
    discussions = result.scalars().all()
    
    return [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "author": d.author.full_name if d.author else "Unknown",
            "replies": len(d.replies),
            "created_at": d.created_at.strftime("%Y-%m-%d")
        }
        for d in discussions
    ]

@router.post("/{discussion_id}/reply")
async def add_reply(
    discussion_id: str,
    reply: ReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adds a comment/reply to a discussion thread.
    """
    # Verify Discussion exists
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalars().first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    new_reply = DiscussionReply(
        discussion_id=discussion_id,
        author_id=current_user.id,
        content=reply.content
    )
    
    db.add(new_reply)
    await db.commit()
    
    return {"success": True, "message": "Reply added"}