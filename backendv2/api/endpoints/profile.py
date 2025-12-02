from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional

from backend.api.deps import get_current_user
from backend.db.models import User

router = APIRouter()

# --- SCHEMAS ---
class ProfileResponse(BaseModel):
    id: str
    username: str
    role: str
    name: str 
    # Serializes 'student_class' in Python to 'class' in JSON for React
    student_class: Optional[str] = Field(default="12th Grade", serialization_alias="class")
    roll: Optional[str] = "2023001"
    
    # Preferences (Mocked for now as they aren't in DB yet)
    notifications_enabled: bool = True
    auto_download: bool = False

class PreferenceUpdate(BaseModel):
    notifications_enabled: bool
    auto_download: bool

# --- ROUTES ---

@router.get("/", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/profile
    Refreshes user data for the Profile Page.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "name": current_user.full_name,
        # Hardcoded logic to match Auth logic until DB columns exist
        "student_class": "12th Science" if current_user.role == "student" else "Faculty",
        "roll": "STU-2025-001" if current_user.role == "student" else "FAC-001",
        "notifications_enabled": True,
        "auto_download": False
    }

@router.post("/preferences")
async def update_preferences(
    prefs: PreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/profile/preferences
    Handles the toggle switches in Profile.jsx
    """
    # In a real app, you'd update columns in the User table here.
    return {"success": True, "message": "Preferences updated", "data": prefs}