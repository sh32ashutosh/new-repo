from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from backend.core import security
from backend.core.database import get_db
from backend.db.models import User

router = APIRouter()

# --- SCHEMAS ---
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    full_name: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse

# --- ROUTE ---
@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    POST /api/auth/login
    """
    # 1. Fetch User
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()

    # 2. Verify Credentials
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 3. Create Token
    access_token = security.create_access_token(data={"sub": user.id})

    # 4. Return exact JSON shape React expects
    return {
        "success": True,
        "token": f"Bearer {access_token}", 
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name
        }
    }