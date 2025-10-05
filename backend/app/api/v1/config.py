"""
Configuration API endpoints for dashboard settings and thresholds.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Configuration"])


@router.get("/dashboard-thresholds")
async def get_dashboard_thresholds(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get configurable thresholds for dashboard risk assessment and alerts."""
    try:
        # Return configurable thresholds for the dashboard
        # These could be stored in database per user or as system defaults
        return {
            "risk_thresholds": {
                "low": {
                    "min_score": 0.0,
                    "max_score": 0.3,
                    "color": "#22c55e",  # green
                    "label": "Low Risk",
                    "description": "Symptoms are well-managed"
                },
                "moderate": {
                    "min_score": 0.3,
                    "max_score": 0.7,
                    "color": "#f59e0b",  # amber
                    "label": "Moderate Risk",
                    "description": "Some symptoms may need attention"
                },
                "high": {
                    "min_score": 0.7,
                    "max_score": 1.0,
                    "color": "#ef4444",  # red
                    "label": "High Risk",
                    "description": "Symptoms require immediate attention"
                }
            },
            "severity_levels": {
                "mild": {
                    "score": 1,
                    "color": "#22c55e",
                    "label": "Mild",
                    "description": "Minimal impact on daily activities"
                },
                "moderate": {
                    "score": 2,
                    "color": "#f59e0b",
                    "label": "Moderate",
                    "description": "Some impact on daily activities"
                },
                "severe": {
                    "score": 3,
                    "color": "#ef4444",
                    "label": "Severe",
                    "description": "Significant impact on daily activities"
                }
            },
            "adherence_targets": {
                "symptom_logging": {
                    "target_percentage": 80,
                    "description": "Log symptoms at least 80% of days",
                    "frequency": "daily"
                },
                "meal_logging": {
                    "target_percentage": 70,
                    "description": "Log meals at least 70% of the time",
                    "frequency": "per_meal"
                },
                "medication_adherence": {
                    "target_percentage": 95,
                    "description": ("Take medications as prescribed "
                                    "95% of the time"),
                    "frequency": "as_prescribed"
                }
            },
            "alert_settings": {
                "flare_prediction": {
                    "enabled": True,
                    "threshold": 0.6,
                    "advance_notice_hours": 24
                },
                "symptom_escalation": {
                    "enabled": True,
                    "consecutive_days": 3,
                    "severity_threshold": "moderate"
                },
                "missed_logging": {
                    "enabled": True,
                    "days_without_logging": 2
                }
            },
            "dashboard_refresh": {
                "auto_refresh_enabled": True,
                "refresh_interval_minutes": 15,
                "real_time_updates": True
            },
            "personalization": {
                "learning_enabled": True,
                "adaptive_thresholds": True,
                "user_specific_adjustments": True
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard thresholds: {str(e)}",
        )


@router.get("/user-preferences")
async def get_user_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user-specific dashboard preferences."""
    try:
        # Return user preferences for dashboard customization
        # These would typically be stored in a user_preferences table
        return {
            "dashboard_layout": {
                # Options: "simple", "comprehensive", "custom"
                "preferred_view": "comprehensive",
                "widget_order": [
                    "risk_assessment",
                    "recent_symptoms", 
                    "ai_predictions",
                    "weekly_stats",
                    "insights",
                    "reminders",
                    "recommendations"
                ],
                "hidden_widgets": []
            },
            "notifications": {
                "email_enabled": True,
                "push_enabled": True,
                "sms_enabled": False,
                "frequency": "daily"  # "immediate", "daily", "weekly"
            },
            "data_sharing": {
                "anonymous_analytics": True,
                "research_participation": False,
                "healthcare_provider_access": True
            },
            "privacy": {
                "data_retention_days": 365,
                "auto_delete_old_logs": True,
                "export_data_format": "json"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user preferences: {str(e)}",
        )