from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
# You might need to import your token creation utility here
# from backend.core.security import create_access_token 

router = APIRouter()

# 1. Define the Login Route
@router.post("/login/access-token")
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint that accepts 'student'/'123'
    """
    username = form_data.username
    password = form_data.password

    # ⚡ HARDCODED CHECK (What you asked for)
    if (username == "student" or username == "teacher") and password == "123":
        # ✅ SUCCESS: Generate a generic token
        # In a real app, you would sign this with a secret key
        return {
            "access_token": f"real-token-for-{username}", 
            "token_type": "bearer",
            "user": {"username": username, "role": username}
        }
    
    # ❌ FAILURE
    raise HTTPException(status_code=400, detail="Incorrect email or password")