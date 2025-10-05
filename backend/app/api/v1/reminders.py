"""
Reminders API endpoints for managing user reminders and notifications.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Reminders"])


class ReminderResponse(BaseModel):
    """Schema for reminder response."""
    id: str
    title: str
    description: str
    reminder_time: datetime
    reminder_type: str  # "medication", "appointment", "symptom_log", "meal"
    priority: str  # "low", "medium", "high"
    is_completed: bool = False


@router.get("/upcoming")
async def get_upcoming_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(
        7, description="Number of days to look ahead for reminders"
    ),
    limit: int = Query(
        10, description="Maximum number of reminders to return"
    ),
):
    """Get upcoming reminders for the current user."""
    try:
        # Calculate date range
        now = datetime.utcnow()
        
        # For now, return mock reminders since we don't have a reminders table
        # In a real implementation, you would query the reminders table
        mock_reminders = []
        
        # Add some sample reminders based on user activity patterns
        # Medication reminders (if user has medications)
        mock_reminders.append({
            "id": "med_1",
            "title": "Take Morning Medication",
            "description": "Don't forget to take your prescribed medication",
            "scheduled_time": (now + timedelta(hours=2)).isoformat(),
            "type": "medication",
            "priority": "high",
            "is_completed": False
        })
        
        # Symptom logging reminder
        mock_reminders.append({
            "id": "symptom_1",
            "title": "Log Daily Symptoms",
            "description": "Record your symptoms to track patterns",
            "scheduled_time": (now + timedelta(hours=8)).isoformat(),
            "type": "log",
            "priority": "medium",
            "is_completed": False
        })
        
        # Meal logging reminder
        mock_reminders.append({
            "id": "meal_1",
            "title": "Log Lunch",
            "description": "Remember to log your lunch for better tracking",
            "scheduled_time": (now + timedelta(hours=4)).isoformat(),
            "type": "log",
            "priority": "medium",
            "is_completed": False
        })
        
        # Appointment reminder
        mock_reminders.append({
            "id": "appointment_1",
            "title": "Doctor Appointment",
            "description": "Don't forget your scheduled appointment with Dr. Smith",
            "scheduled_time": (now + timedelta(days=2)).isoformat(),
            "type": "appointment",
            "priority": "high",
            "is_completed": False
        })
        
        # Hydration reminder (categorized as log)
        mock_reminders.append({
            "id": "hydration_1",
            "title": "Drink Water",
            "description": "Stay hydrated for better digestive health",
            "scheduled_time": (now + timedelta(hours=1)).isoformat(),
            "type": "log",
            "priority": "low",
            "is_completed": False
        })
        
        # Sort by scheduled time and limit results
        sorted_reminders = sorted(
            mock_reminders, 
            key=lambda x: x["scheduled_time"]
        )[:limit]
        
        return {
            "reminders": sorted_reminders,
            "total_count": len(sorted_reminders),
            "days_ahead": days
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reminders: {str(e)}",
        )


@router.get("/types")
async def get_reminder_types(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get available reminder types."""
    return {
        "reminder_types": [
            {
                "type": "medication",
                "name": "Medication Reminders",
                "description": "Reminders to take prescribed medications"
            },
            {
                "type": "symptom_log",
                "name": "Symptom Logging",
                "description": "Reminders to log daily symptoms"
            },
            {
                "type": "meal",
                "name": "Meal Logging",
                "description": "Reminders to log meals and food intake"
            },
            {
                "type": "appointment",
                "name": "Appointments",
                "description": "Upcoming medical appointments"
            },
            {
                "type": "check_in",
                "name": "Health Check-ins",
                "description": "Regular health and progress reviews"
            },
            {
                "type": "hydration",
                "name": "Hydration",
                "description": "Reminders to drink water"
            }
        ]
    }


@router.get("/stats")
async def get_reminder_stats(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days to analyze"),
):
    """Get reminder statistics for the user."""
    try:
        # Mock statistics - in real implementation, query actual reminder data
        return {
            "total_reminders": 45,
            "completed_reminders": 38,
            "completion_rate": 84.4,
            "most_common_type": "symptom_log",
            "streak_days": 7,
            "by_type": {
                "medication": {"total": 15, "completed": 14},
                "symptom_log": {"total": 20, "completed": 16},
                "meal": {"total": 8, "completed": 6},
                "hydration": {"total": 2, "completed": 2}
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reminder stats: {str(e)}",
        )