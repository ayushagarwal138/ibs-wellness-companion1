"""
Authentication service for user registration, login, and token management.
"""

from typing import Optional
from datetime import timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    create_email_verification_token,
    verify_email_verification_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.core.config import settings


class AuthService:
    """Authentication service class."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            The created user

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            is_verified=False,  # Will be verified via email
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            The authenticated user or None if authentication fails
        """
        result = await self.db.execute(
            select(User).where(User.email == email)  # type: ignore[arg-type]
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.password_hash or not verify_password(
            password, user.password_hash
        ):
            return None

        return user

    async def login_user(self, login_data: UserLogin) -> Token:
        """
        Login a user and return tokens.

        Args:
            login_data: User login data

        Returns:
            Access and refresh tokens

        Raises:
            HTTPException: If authentication fails
        """
        user = await self.authenticate_user(login_data.email, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Update last login
        from datetime import datetime

        user.last_login_at = datetime.utcnow()
        await self.db.commit()

        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            New access and refresh tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = verify_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        try:
            user_id_uuid = uuid.UUID(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await self.db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def create_email_verification(self, user: User) -> str:
        """
        Create an email verification token for a user.

        Args:
            user: The user to create verification for

        Returns:
            The verification token
        """
        return create_email_verification_token(user.email)

    async def verify_email(self, token: str) -> bool:
        """
        Verify a user's email using a verification token.

        Args:
            token: The email verification token

        Returns:
            True if verification successful, False otherwise
        """
        email = verify_email_verification_token(token)

        if email is None:
            return False

        # Find user and mark as verified
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.is_verified = True
        await self.db.commit()

        return True

    async def create_password_reset(self, email: str) -> Optional[str]:
        """
        Create a password reset token for a user.

        Args:
            email: The user's email

        Returns:
            The password reset token if user exists, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        return create_password_reset_token(email)

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.

        Args:
            token: The password reset token
            new_password: The new password

        Returns:
            True if reset successful, False otherwise
        """
        email = verify_password_reset_token(token)

        if email is None:
            return False

        # Find user and update password
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.password_hash = get_password_hash(new_password)
        await self.db.commit()

        return True

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """
        Change a user's password.

        Args:
            user: The user
            current_password: The current password
            new_password: The new password

        Returns:
            True if change successful, False otherwise
        """
        if not verify_password(current_password, user.password_hash):
            return False

        user.password_hash = get_password_hash(new_password)
        await self.db.commit()

        return True
