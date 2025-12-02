from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.config import settings
from backend.core.database import get_db
from backend.db.models import User

# Ensure this matches your router mount
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/login/access-token")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # DEBUG LOGGING
        # print(f"🔍 DEBUG: Checking Token: {token[:10]}...") 
        
        # 1. Decode Token
        algorithm = getattr(settings, "ALGORITHM", "HS256")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            print("❌ DEBUG: Token has no 'sub' (User ID)")
            raise credentials_exception
            
        # print(f"✅ DEBUG: Token valid. User ID: {user_id}")

    except JWTError as e:
        print(f"❌ DEBUG: JWT Error: {str(e)}")
        raise credentials_exception
    
    # 2. Query Database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        print(f"❌ DEBUG: User ID {user_id} NOT found in Database (vlink.db).")
        print("💡 TIP: Did you run 'python backend/db_initializer.py'?")
        raise credentials_exception
        
    return user