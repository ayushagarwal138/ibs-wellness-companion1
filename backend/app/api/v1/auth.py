"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    AuthResponse,
    RefreshToken,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    ChangePassword,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User


router = APIRouter()


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        background_tasks: Background tasks for sending emails
        db: Database session

    Returns:
        The created user with tokens
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)

    # Create tokens for the new user
    from datetime import timedelta
    from app.core.security import create_access_token, create_refresh_token
    from app.core.config import settings

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # TODO: Send verification email in background
    # verification_token = await auth_service.create_email_verification(user)
    # background_tasks.add_task(
    #     send_verification_email, user.email, verification_token
    # )

    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login_at,
        phone_number=getattr(user, "phone_number", None),
        date_of_birth=user.date_of_birth,
        gender=getattr(user, "gender", None),
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        ibs_type=getattr(user, "ibs_type", None),
        diagnosis_date=user.diagnosis_date,
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response.dict(),
    )


@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login a user and return access tokens with user data.

    Args:
        login_data: User login credentials
        db: Database session

    Returns:
        Access and refresh tokens with user data
    """
    auth_service = AuthService(db)
    token_data = await auth_service.login_user(login_data)

    # Get user data by authenticating again
    # (we already know credentials are valid)
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login_at,
        phone_number=getattr(user, "phone_number", None),
        date_of_birth=user.date_of_birth,
        gender=getattr(user, "gender", None),
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        ibs_type=getattr(user, "ibs_type", None),
        diagnosis_date=user.diagnosis_date,
    )

    return AuthResponse(
        access_token=token_data.access_token,
        refresh_token=token_data.refresh_token,
        token_type=token_data.token_type,
        expires_in=token_data.expires_in,
        user=user_response.dict(),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken, db: AsyncSession = Depends(get_db)):
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_data: Refresh token data
        db: Database session

    Returns:
        New access and refresh tokens
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(refresh_data.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout a user (client-side token removal).

    Args:
        current_user: The current authenticated user

    Returns:
        Success message
    """
    # In a JWT-based system, logout is typically handled client-side
    # by removing the token. For server-side logout, you would need
    # to maintain a blacklist of tokens.
    return {"message": "Successfully logged out"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    verification_data: EmailVerification, db: AsyncSession = Depends(get_db)
):
    """
    Verify a user's email address.

    Args:
        verification_data: Email verification token
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    success = await auth_service.verify_email(verification_data.token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification.

    Args:
        background_tasks: Background tasks for sending emails
        current_user: The current authenticated user
        db: Database session

    Returns:
        Success message
    """
    if current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )

    auth_service = AuthService(db)
    await auth_service.create_email_verification(current_user)

    # TODO: Send verification email in background
    # verification_token = await auth_service.create_email_verification(
    #     current_user
    # )
    # background_tasks.add_task(
    #     send_verification_email, current_user.email, verification_token
    # )

    return {"message": "Verification email sent"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    password_reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset.

    Args:
        password_reset_data: Password reset request data
        background_tasks: Background tasks for sending emails
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    await auth_service.create_password_reset(password_reset_data.email)

    # Always return success to prevent email enumeration
    # TODO: Send password reset email in background if user exists
    # reset_token = await auth_service.create_password_reset(
    #     password_reset_data.email
    # )
    # if reset_token:
    #     background_tasks.add_task(
    #         send_password_reset_email, password_reset_data.email, reset_token
    #     )

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Reset a user's password using a reset token.

    Args:
        reset_data: Password reset confirmation data
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    success = await auth_service.reset_password(
        reset_data.token, reset_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {"message": "Password reset successfully"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change a user's password.

    Args:
        password_data: Password change data
        current_user: The current authenticated user
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        current_user, password_data.current_password, password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.

    Args:
        current_user: The current authenticated user

    Returns:
        Current user information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login_at,
        phone_number=getattr(current_user, "phone_number", None),
        date_of_birth=current_user.date_of_birth,
        gender=getattr(current_user, "gender", None),
        height_cm=current_user.height_cm,
        weight_kg=current_user.weight_kg,
        ibs_type=getattr(current_user, "ibs_type", None),
        diagnosis_date=current_user.diagnosis_date,
    )
