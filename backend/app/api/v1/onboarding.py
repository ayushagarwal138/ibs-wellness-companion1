"""
Onboarding API endpoints for IBS Wellness Companion.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.ml_integration_service import MLIntegrationService

router = APIRouter()


@router.post("/predictions")
async def generate_onboarding_predictions(
    questionnaire_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate ML-powered predictions based on onboarding questionnaire data.
    
    Args:
        questionnaire_data: Onboarding questionnaire responses
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Comprehensive predictions and recommendations
    """
    try:
        # Initialize ML service
        ml_service = MLIntegrationService(db)
        
        # Generate predictions
        predictions = ml_service.generate_onboarding_predictions(questionnaire_data)
        
        return {
            "user_id": current_user.id,
            "predictions": predictions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate predictions: {str(e)}"
        )


@router.get("/status")
async def check_onboarding_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if user has completed onboarding questionnaire.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Onboarding completion status
    """
    # Check if user has completed onboarding based on profile completeness
    is_completed = all([
        current_user.age is not None,
        current_user.gender is not None,
        current_user.ibs_type is not None,
        current_user.diagnosis_date is not None
    ])
    
    return {
        "completed": is_completed,
        "user_id": current_user.id,
        "completion_percentage": _calculate_completion_percentage(current_user)
    }


def _calculate_completion_percentage(user: User) -> float:
    """Calculate onboarding completion percentage based on filled fields."""
    required_fields = [
        user.age,
        user.gender,
        user.ibs_type,
        user.diagnosis_date,
        user.height,
        user.weight,
        user.activity_level
    ]
    
    completed_fields = sum(1 for field in required_fields if field is not None)
    return (completed_fields / len(required_fields)) * 100