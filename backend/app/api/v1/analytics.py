"""
Analytics API endpoints for user analytics, system metrics, and achievements.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.symptom import SymptomLog, Symptom
from app.models.diet import DietLog
from app.schemas.analytics import UserAnalyticsResponse

router = APIRouter(tags=["Analytics"])


# User Analytics endpoints
@router.get("/user-analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days to retrieve analytics"),
):
    """Get user analytics for the specified period."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get symptom logs count
        symptom_logs_result = await db.execute(
            select(func.count(SymptomLog.id)).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        total_symptom_logs = symptom_logs_result.scalar() or 0

        # Get diet logs count
        diet_logs_result = await db.execute(
            select(func.count(DietLog.id)).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            )
        )
        total_diet_logs = diet_logs_result.scalar() or 0

        # Get average symptom severity (simplified approach)
        severity_logs = await db.execute(
            select(SymptomLog.severity).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        
        # Calculate average severity manually
        severity_values = []
        for row in severity_logs:
            severity = row[0]
            if severity == 'mild':
                severity_values.append(1)
            elif severity == 'moderate':
                severity_values.append(2)
            elif severity == 'severe':
                severity_values.append(3)
            elif severity == 'very_severe':
                severity_values.append(4)
        
        avg_severity = (sum(severity_values) / len(severity_values) 
                        if severity_values else 0)

        # Get most common symptoms
        most_common_symptoms_result = await db.execute(
            select(
                Symptom.name, 
                func.count(SymptomLog.id).label('frequency')
            )
            .join(SymptomLog, Symptom.id == SymptomLog.symptom_id)
            .where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
            .group_by(Symptom.name)
            .order_by(func.count(SymptomLog.id).desc())
            .limit(5)
        )
        most_common_symptoms = [
            {"name": row.name, "frequency": row.frequency}
            for row in most_common_symptoms_result.all()
        ]

        # Calculate symptom-free days (days without any symptom logs)
        symptom_days_result = await db.execute(
            select(
                func.count(func.distinct(func.date(SymptomLog.logged_at)))
            ).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        symptom_days = symptom_days_result.scalar() or 0
        symptom_free_days = max(0, days - symptom_days)

        return UserAnalyticsResponse(
            user_id=current_user.id,
            total_symptom_logs=total_symptom_logs,
            total_diet_logs=total_diet_logs,
            total_medication_logs=0,  # TODO: Add medication logs when available
            avg_symptom_severity=round(float(avg_severity), 2),
            symptom_free_days=symptom_free_days,
            most_common_symptoms=most_common_symptoms,
            trigger_foods=[],  # TODO: Implement trigger food analysis
            medication_adherence_rate=0.0,  # TODO: Add when medication tracking is available
            improvement_trend="stable",  # TODO: Calculate trend based on historical data
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days for summary"),
):
    """Get analytics summary for the user."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get symptom logs count
        symptom_logs_result = await db.execute(
            select(func.count(SymptomLog.id)).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        total_symptom_logs = symptom_logs_result.scalar() or 0

        # Get diet logs count
        diet_logs_result = await db.execute(
            select(func.count(DietLog.id)).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            )
        )
        total_diet_logs = diet_logs_result.scalar() or 0

        # Get average symptom severity
        avg_severity_result = await db.execute(
            select(func.avg(
                func.case(
                    (SymptomLog.severity == 'mild', 1),
                    (SymptomLog.severity == 'moderate', 2),
                    (SymptomLog.severity == 'severe', 3),
                    else_=0
                )
            )).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        avg_severity = avg_severity_result.scalar() or 0.0

        return {
            "total_symptom_logs": total_symptom_logs,
            "total_diet_logs": total_diet_logs,
            "total_medication_logs": 0,  # TODO: Add when available
            "average_symptom_severity": round(float(avg_severity), 2),
            "total_achievements": 0,  # TODO: Add when available
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
