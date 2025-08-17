from datetime import datetime, timedelta
from typing import Optional, Tuple
#from jose import jwt  # Using PyJWT-like API via 'jose' would be ideal, but we stick to PyJWT
import jwt as pyjwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .models import User, RoleEnum
from .database import db_session, set_search_path

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ------------- Password helpers -------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

# ------------- JWT helpers -------------

def create_access_token(*, user_id: Optional[int], username: str, role: str, tenant_id: str, expires_minutes: int | None = None) -> str:
    to_encode = {
        "sub": username,
        "uid": user_id,
        "role": role,
        "tenant_id": tenant_id,
        "iat": int(datetime.utcnow().timestamp()),
    }
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = pyjwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ------------- Dependencies -------------

def get_current_claims(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_token(token)


def require_superadmin(claims: dict = Depends(get_current_claims)) -> dict:
    if claims.get("role") != RoleEnum.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    return claims


def require_tenant_role(allowed: tuple[RoleEnum, ...]):
    def _dep(claims: dict = Depends(get_current_claims)) -> dict:
        role = claims.get("role")
        if role == RoleEnum.SUPERADMIN:
            # Superadmin cannot operate inside tenant routes by default for safety
            raise HTTPException(status_code=403, detail="Forbidden for superadmin on tenant routes")
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return claims
    return _dep
