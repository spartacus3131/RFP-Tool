"""
Authentication API - Register, login, user info.
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.user import User
from app.models.audit_log import AuditAction
from app.services.audit import log_action, get_client_ip, get_user_agent
from app.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter()


# Password complexity validation
def validate_password_complexity(password: str) -> str:
    """Validate password meets complexity requirements."""
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        errors.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("at least one number")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("at least one special character")

    if errors:
        raise ValueError(f"Password must contain {', '.join(errors)}")
    return password


# Request/Response models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    organization: Optional[str] = Field(None, max_length=255)

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        return validate_password_complexity(v)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    organization: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenWithUser(Token):
    user: UserResponse


@router.post("/register", response_model=TokenWithUser)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        organization=user_data.organization,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            is_active=user.is_active,
        ),
    }


@router.post("/login", response_model=TokenWithUser)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    # Find user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        await log_action(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            user_email=form_data.username,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=False,
            error_message="Invalid credentials",
        )
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        # Log inactive user login attempt
        await log_action(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            user_id=user.id,
            user_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=False,
            error_message="Inactive user",
        )
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Log successful login
    await log_action(
        db=db,
        action=AuditAction.LOGIN,
        user_id=user.id,
        user_email=user.email,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        success=True,
    )
    await db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            is_active=user.is_active,
        ),
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        organization=current_user.organization,
        is_active=current_user.is_active,
    )
