from datetime import datetime, timedelta
from typing import Optional, Dict

from passlib.context import CryptContext
import jwt
from fastapi import HTTPException, status

from backend.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: Dict[str, object] = {"sub": subject, "exp": expire}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


# Robust exception resolution for different PyJWT versions
try:
    ExpiredSignatureError = jwt.ExpiredSignatureError  # PyJWT common alias
    InvalidTokenError = jwt.InvalidTokenError
except AttributeError:
    # Some installations expose exceptions under jwt.exceptions
    try:
        from jwt import exceptions as jwt_exceptions  # type: ignore
        ExpiredSignatureError = getattr(jwt_exceptions, "ExpiredSignatureError", Exception)
        InvalidTokenError = getattr(jwt_exceptions, "InvalidTokenError", Exception)
    except Exception:
        # Fallback to generic Exception types if nothing else is available
        ExpiredSignatureError = Exception
        InvalidTokenError = Exception


def decode_access_token(token: str) -> Dict[str, object]:
    """
    Decode a JWT and return the payload (dictionary).
    Raises HTTPException(401) for expired/invalid tokens so callers that depend on HTTP flows
    receive proper 401 responses. Socket handlers that call this should catch Exception and reject the handshake.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")