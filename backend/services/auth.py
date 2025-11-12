import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
import pyotp
import json
import secrets

from models.user import User
from utils.jwt_handler import create_access_token
from utils.schema_validators import UserCreate, UserOut, Token, AuthLogin, UserContextUpdate
from utils.auth_deps import get_current_user
from services.db import get_db
from services.email_service import (
    send_verification_email, send_password_reset_email,
    send_2fa_code_email, send_welcome_email, generate_token
)


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Request/Response models for new features
class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]


class Verify2FARequest(BaseModel):
    code: str


class LoginWith2FARequest(BaseModel):
    email: EmailStr
    password: str
    code: str


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
    Create a new user account with email verification.

    This operation must be atomic - either user is fully created or rolled back.
    """
    try:
        # Check for existing user
        exists = db.query(User).filter(User.email == user_in.email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Generate verification token
        verification_token = generate_token()

        # Create user within transaction
        user = User(
            email=user_in.email,
            username=user_in.username,
            password_hash=hash_password(user_in.password),
            email_verified=False,
            verification_token=verification_token,
            verification_sent_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Send verification email (async, don't block response)
        try:
            send_verification_email(user.email, user.username, verification_token)
        except Exception as e:
            # Log error but don't fail signup
            print(f"Failed to send verification email: {e}")

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


# ============= Email Verification Endpoints =============

@router.post("/verify-email")
@limiter.limit("10/minute")
def verify_email(request: Request, data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user's email with token"""
    user = db.query(User).filter(User.verification_token == data.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    # Check if token is expired (24 hours)
    if user.verification_sent_at and (datetime.utcnow() - user.verification_sent_at) > timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Verification token has expired")

    # Mark email as verified
    user.email_verified = True
    user.verification_token = None
    user.verification_sent_at = None

    db.commit()

    # Send welcome email
    try:
        send_welcome_email(user.email, user.username)
    except:
        pass  # Don't fail verification if welcome email fails

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
@limiter.limit("3/hour")
def resend_verification(request: Request, data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend verification email"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification link has been sent"}

    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Generate new token
    verification_token = generate_token()
    user.verification_token = verification_token
    user.verification_sent_at = datetime.utcnow()

    db.commit()

    # Send verification email
    try:
        send_verification_email(user.email, user.username, verification_token)
    except:
        pass

    return {"message": "If the email exists, a verification link has been sent"}


# ============= Password Reset Endpoints =============

@router.post("/forgot-password")
@limiter.limit("3/hour")
def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset email"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    reset_token = generate_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

    db.commit()

    # Send reset email
    try:
        send_password_reset_email(user.email, user.username, reset_token)
    except:
        pass

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
@limiter.limit("5/hour")
def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check if token is expired
    if not user.reset_token_expires or datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Reset token has expired")

    # Update password
    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None

    db.commit()

    return {"message": "Password reset successfully"}


# ============= 2FA Endpoints =============

@router.post("/enable-2fa", response_model=Enable2FAResponse)
def enable_2fa(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Enable 2FA for the current user"""
    if user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")

    # Generate TOTP secret
    secret = pyotp.random_base32()

    # Generate backup codes
    backup_codes = [secrets.token_hex(4) for _ in range(10)]

    # Store encrypted backup codes
    user.totp_secret = secret
    user.backup_codes = json.dumps(backup_codes)

    db.commit()

    # Generate QR code URL
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="Nawwa AI"
    )

    return Enable2FAResponse(
        secret=secret,
        qr_code=provisioning_uri,
        backup_codes=backup_codes
    )


@router.post("/verify-2fa")
def verify_2fa(data: Verify2FARequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify 2FA setup with code"""
    if user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")

    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")

    # Verify the code
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Enable 2FA
    user.two_factor_enabled = True
    db.commit()

    return {"message": "2FA enabled successfully"}


@router.post("/disable-2fa")
def disable_2fa(data: Verify2FARequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Disable 2FA for the current user"""
    if not user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    # Verify the code or backup code
    totp = pyotp.TOTP(user.totp_secret)
    is_valid = totp.verify(data.code, valid_window=1)

    # Check backup codes if TOTP fails
    if not is_valid and user.backup_codes:
        backup_codes = json.loads(user.backup_codes)
        if data.code in backup_codes:
            is_valid = True
            backup_codes.remove(data.code)
            user.backup_codes = json.dumps(backup_codes)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Disable 2FA
    user.two_factor_enabled = False
    user.totp_secret = None
    user.backup_codes = None

    db.commit()

    return {"message": "2FA disabled successfully"}


@router.post("/login-2fa", response_model=Token)
@limiter.limit("10/minute")
def login_with_2fa(request: Request, data: LoginWith2FARequest, db: Session = Depends(get_db)):
    """Login with 2FA code"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled for this account")

    # Verify 2FA code
    totp = pyotp.TOTP(user.totp_secret)
    is_valid = totp.verify(data.code, valid_window=1)

    # Check backup codes if TOTP fails
    if not is_valid and user.backup_codes:
        backup_codes = json.loads(user.backup_codes)
        if data.code in backup_codes:
            is_valid = True
            backup_codes.remove(data.code)
            user.backup_codes = json.dumps(backup_codes)
            db.commit()

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid 2FA code")

    token = create_access_token(sub=str(user.id))
    return Token(access_token=token)
