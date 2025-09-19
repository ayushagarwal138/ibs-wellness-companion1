"""
OAuth authentication endpoints for Google and GitHub integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse
from app.schemas.user import UserResponse
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from sqlalchemy import select
import uuid

router = APIRouter(prefix="/oauth", tags=["oauth"])


class OAuthRequest(BaseModel):
    """OAuth authentication request schema."""
    provider: str
    provider_id: str
    email: EmailStr
    name: str
    image: Optional[str] = None
    access_token: str


class OAuthUserCreate(BaseModel):
    """OAuth user creation schema."""
    email: EmailStr
    first_name: str
    last_name: str
    provider: str
    provider_id: str
    avatar: Optional[str] = None
    is_verified: bool = True


@router.post("/", response_model=AuthResponse)
async def oauth_login(
    oauth_data: OAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth login/registration for Google and GitHub.
    
    Args:
        oauth_data: OAuth authentication data
        db: Database session
        
    Returns:
        Access and refresh tokens with user data
    """
    # Check if user exists by email
    result = await db.execute(
        select(User).where(User.email == oauth_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user from OAuth data
        name_parts = oauth_data.name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User(
            id=uuid.uuid4(),
            email=oauth_data.email,
            first_name=first_name,
            last_name=last_name,
            avatar=oauth_data.image,
            is_verified=True,  # OAuth users are pre-verified
            is_active=True,
            # Set a random password hash since OAuth users don't use passwords
            password_hash="oauth_user_no_password"
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update existing user's avatar if provided
        if oauth_data.image and not user.avatar:
            user.avatar = oauth_data.image
            await db.commit()
            await db.refresh(user)
    
    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login_at,
        phone_number=getattr(user, 'phone_number', None),
        date_of_birth=user.date_of_birth,
        gender=getattr(user, 'gender', None),
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        ibs_type=getattr(user, 'ibs_type', None),
        diagnosis_date=user.diagnosis_date
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response.dict()
    )


@router.get("/providers")
async def get_oauth_providers():
    """
    Get available OAuth providers.
    
    Returns:
        List of available OAuth providers
    """
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "enabled": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
            },
            {
                "name": "github", 
                "display_name": "GitHub",
                "enabled": bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)
            }
        ]
    }