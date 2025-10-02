"""
Analytics API endpoints for user analytics, system metrics, and achievements.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import UserAnalyticsResponse

router = APIRouter(tags=["Analytics"])


# User Analytics endpoints
@router.get("/user-analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    _db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days to retrieve analytics for"),
):
    """Get user analytics for the specified period."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Mock analytics data for now
        return UserAnalyticsResponse(
            user_id=current_user.id,
            total_symptom_logs=25,
            total_diet_logs=30,
            total_medication_logs=15,
            avg_symptom_severity=3.2,
            symptom_free_days=12,
            most_common_symptoms=[
                {"name": "Abdominal Pain", "frequency": 15},
                {"name": "Bloating", "frequency": 12},
            ],
            trigger_foods=[
                {"name": "Dairy", "confidence": 0.8},
                {"name": "Gluten", "confidence": 0.6},
            ],
            medication_adherence_rate=0.85,
            improvement_trend="improving",
            period_start=start_date,
            period_end=end_date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user analytics: {str(e)}",
        )


@router.get("/analytics-summary")
async def get_analytics_summary(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days for summary"),
):
    """Get analytics summary for the user."""
    try:
        # Return mock summary data
        return {
            "total_symptom_logs": 25,
            "total_diet_logs": 30,
            "total_medication_logs": 15,
            "average_symptom_severity": 3.2,
            "total_achievements": 5,
            "analytics_period_days": days,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics summary: {str(e)}",
        )


# System Metrics endpoints
@router.get("/system-metrics")
async def get_system_metrics(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    _metric_category: Optional[str] = Query(
        None, description="Filter by metric category"
    ),
    _hours: int = Query(24, description="Number of hours to retrieve metrics for"),
):
    """Get system metrics (admin only for now, but can be extended)."""
    try:
        # Return mock system metrics
        return [
            {
                "metric_name": "api_response_time",
                "metric_value": 150.5,
                "metric_category": "performance",
                "recorded_at": datetime.utcnow().isoformat(),
            },
            {
                "metric_name": "active_users",
                "metric_value": 42,
                "metric_category": "usage",
                "recorded_at": datetime.utcnow().isoformat(),
            },
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system metrics: {str(e)}",
        )


# Achievements endpoints
@router.get("/achievements")
async def get_achievements(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    _is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """Get all available achievements."""
    try:
        # Return mock achievements
        return [
            {
                "id": 1,
                "name": "First Log",
                "description": "Log your first symptom",
                "points_awarded": 10,
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Consistent Logger",
                "description": "Log symptoms for 7 consecutive days",
                "points_awarded": 50,
                "is_active": True,
            },
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve achievements: {str(e)}",
        )


@router.get("/user-achievements")
async def get_user_achievements(
    _db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get user's earned achievements."""
    try:
        # Return mock user achievements
        return [
            {
                "id": 1,
                "achievement_id": 1,
                "user_id": current_user.id,
                "earned_at": datetime.utcnow().isoformat(),
                "achievement": {
                    "name": "First Log",
                    "description": "Log your first symptom",
                    "points_awarded": 10,
                },
            }
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user achievements: {str(e)}",
        )


@router.post("/check-achievements")
async def check_achievements(
    _db: AsyncSession = Depends(get_db), _current_user: User = Depends(get_current_user)
):
    """Check and award new achievements for the user."""
    # This would contain logic to check various achievement criteria
    # For now, return a simple response
    return {"message": "Achievement check completed", "new_achievements": 0}
