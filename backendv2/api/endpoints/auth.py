from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field
from typing import Optional

from backend.core import security
from backend.core.database import get_db
from backend.db.models import User

router = APIRouter()

# --- SCHEMAS ---
# This matches the JSON sent by your React Login.jsx
class LoginRequest(BaseModel):
    username: str
    password: str

# This matches the data expected by your AuthContext.jsx and Profile.jsx
class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    # Profile.jsx expects "name", not "full_name"
    name: str 
    # Profile.jsx expects "class" and "roll"
    # We use serialization_alias because 'class' is a keyword in Python
    student_class: Optional[str] = Field(default="12th Grade", serialization_alias="class")
    roll: Optional[str] = "2023001"

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse

# --- ROUTES ---

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Handles authentication for Login.jsx.
    1. accepts JSON { username, password }
    2. verifies against DB
    3. returns JWT token + user info shaped for Profile.jsx
    """
    # 1. Fetch User from DB
    # We select the user where the username matches
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()

    # 2. Verify Credentials
    # Check if user exists AND if the password hash matches
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 3. Create Access Token
    # This generates the JWT string
    access_token = security.create_access_token(data={"sub": user.id})

    # 4. Return Response
    # The structure here matches exactly what your AuthContext.jsx expects:
    # data.success, data.token, and data.user
    return {
        "success": True,
        "token": f"Bearer {access_token}", 
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role, # "teacher" or "student"
            # Map DB 'full_name' to Frontend 'name'
            "name": user.full_name,
            # Hardcoded defaults for Hackathon since these columns aren't in User table yet
            "student_class": "12th Science" if user.role == "student" else "Faculty",
            "roll": "STU-2025-001" if user.role == "student" else "FAC-001"
        }
    }