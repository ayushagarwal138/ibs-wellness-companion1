"""
Firebase API endpoints for authentication and messaging.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.firebase_service import firebase_admin_service

router = APIRouter(prefix="/firebase", tags=["firebase"])


class TokenVerificationRequest(BaseModel):
    """Request schema for Firebase token verification."""

    id_token: str


class TokenVerificationResponse(BaseModel):
    """Response schema for Firebase token verification."""

    valid: bool
    uid: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    error: Optional[str] = None


class PushNotificationRequest(BaseModel):
    """Request schema for push notification."""

    token: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = None


class MulticastNotificationRequest(BaseModel):
    """Request schema for multicast push notification."""

    tokens: List[str]
    title: str
    body: str
    data: Optional[Dict[str, str]] = None


class TopicNotificationRequest(BaseModel):
    """Request schema for topic push notification."""

    topic: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = None


@router.post("/verify-token", response_model=TokenVerificationResponse)
async def verify_firebase_token(
    request: TokenVerificationRequest, db: AsyncSession = Depends(get_db)
):
    """Verify Firebase ID token."""
    try:
        decoded_token = await firebase_admin_service.verify_id_token(request.id_token)

        if decoded_token:
            return TokenVerificationResponse(
                valid=True,
                uid=decoded_token.get("uid"),
                email=decoded_token.get("email"),
                email_verified=decoded_token.get("email_verified", False),
            )
        else:
            return TokenVerificationResponse(
                valid=False, error="Invalid or expired token"
            )

    except Exception as e:
        return TokenVerificationResponse(valid=False, error=str(e))


@router.post("/send-notification")
async def send_push_notification(
    request: PushNotificationRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Send push notification to a specific device token."""
    try:
        success = await firebase_admin_service.send_push_notification(
            token=request.token,
            title=request.title,
            body=request.body,
            data=request.data,
        )

        if success:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send notification",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}",
        )


@router.post("/send-multicast-notification")
async def send_multicast_notification(
    request: MulticastNotificationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Send push notification to multiple device tokens."""
    try:
        result = await firebase_admin_service.send_multicast_notification(
            tokens=request.tokens,
            title=request.title,
            body=request.body,
            data=request.data,
        )

        return {
            "message": (
                f"Sent {result['success_count']} notifications successfully, "
                f"{result['failure_count']} failed"
            ),
            "details": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending multicast notification: {str(e)}",
        )


@router.post("/send-topic-notification")
async def send_topic_notification(
    request: TopicNotificationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Send push notification to a topic."""
    try:
        success = await firebase_admin_service.send_topic_notification(
            topic=request.topic,
            title=request.title,
            body=request.body,
            data=request.data,
        )

        if success:
            return {
                "message": (
                    f"Topic notification sent to '{request.topic}' " "successfully"
                )
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send topic notification",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending topic notification: {str(e)}",
        )


@router.get("/user/{uid}")
async def get_firebase_user(
    uid: str, current_user: User = Depends(get_current_active_user)
):
    """Get Firebase user information by UID."""
    try:
        user_info = await firebase_admin_service.get_user(uid)

        if user_info:
            return user_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Firebase user not found"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Firebase user: {str(e)}",
        )


@router.get("/health")
async def firebase_health_check():
    """Check Firebase Admin SDK health."""
    try:
        # Try to initialize if not already done
        initialized = firebase_admin_service.initialize()

        return {
            "status": "healthy" if initialized else "not_configured",
            "initialized": initialized,
            "message": (
                "Firebase Admin SDK is ready"
                if initialized
                else "Firebase credentials not configured"
            ),
        }

    except Exception as e:
        return {
            "status": "error",
            "initialized": False,
            "message": f"Firebase Admin SDK error: {str(e)}",
        }
