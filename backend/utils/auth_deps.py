from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .jwt_handler import decode_token
from models.user import User
from services.db import get_db


auth_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not creds or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = decode_token(creds.credentials)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user is an admin.
    Raises 403 Forbidden if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required. You do not have permission to perform this action."
        )
    return current_user
