import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.user import User
from utils.jwt_handler import create_access_token
from utils.schema_validators import UserCreate, UserOut, Token, AuthLogin, UserContextUpdate
from utils.auth_deps import get_current_user
from services.db import get_db


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


@router.post("/signup", response_model=UserOut)
@limiter.limit("5/minute")  # Max 5 signup attempts per minute
def signup(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account with proper transaction handling.

    This operation must be atomic - either user is fully created or rolled back.
    """
    try:
        # Check for existing user
        exists = db.query(User).filter(User.email == user_in.email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user within transaction
        user = User(
            email=user_in.email,
            username=user_in.username,
            password_hash=hash_password(user_in.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        # Re-raise HTTP exceptions without rollback
        raise
    except Exception as e:
        # Rollback on any unexpected error
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Max 10 login attempts per minute
def login(request: Request, payload: AuthLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(sub=str(user.id))
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_current_user_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile information
    """
    return user


@router.put("/me/context", response_model=UserOut)
def update_user_context(
    context_update: UserContextUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update the user's current working context.
    This context will be used by the AI to generate more relevant visualizations.
    """
    try:
        user.current_context = context_update.current_context
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")
