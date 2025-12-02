from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 🔄 UPDATED IMPORTS: backend -> backend
from backend.core.config import settings
from backend.core.database import get_db
from backend.db.models import User

# ⚡ CRITICAL FIX: The token URL must match exactly where your auth.py is mounted.
# In router.py, we mounted auth at root ("") prefix, so the path is /api/login/access-token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/login/access-token")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Decodes the JWT token from the Authorization header.
    Returns the User object from the REAL Database (vlink.db).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode Token
        # We use "HS256" as the default algorithm if not explicitly set in config
        algorithm = getattr(settings, "ALGORITHM", "HS256")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 2. Query the Real Database
    # We look up the user by the ID found in the token
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    return user