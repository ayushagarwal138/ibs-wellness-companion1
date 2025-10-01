"""
User Personalization API

API endpoints for managing user-specific personalization settings,
adaptive algorithms, and learning patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.user_personalization_service import UserPersonalizationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Personalization"])


@router.get("/profile")
async def get_personalization_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's personalization profile and learning patterns."""
    try:
        # For now, return a basic personalization profile with default values
        # This ensures the endpoint works while the full personalization service is being developed
        
        # Basic user profile data
        user_profile = {
            "age": getattr(current_user, 'age', None),
            "gender": getattr(current_user, 'gender', None),
            "ibs_type": getattr(current_user, 'ibs_type', None),
            "height_cm": getattr(current_user, 'height_cm', None),
            "weight_kg": getattr(current_user, 'weight_kg', None)
        }
        
        # Default personalized thresholds
        thresholds = {
            "risk_thresholds": {
                "high": 0.7,
                "medium": 0.4
            },
            "weights": {
                "symptom_weight": 0.4,
                "stress_weight": 0.3,
                "sleep_weight": 0.3
            },
            "confidence_threshold": 0.75,
            "personalization_metadata": {
                "last_updated": datetime.utcnow().isoformat(),
                "data_points_used": 0,
                "adaptation_level": "initial"
            }
        }
        
        # Default nutrition targets
        nutrition_targets = {
            "calories": 2000,
            "protein_g": 50,
            "fiber_g": 25,
            "water_ml": 2000
        }
        
        # Default learning patterns
        learning_patterns = {
            "confidence": 0.5,
            "learning_progress": "initial",
            "dietary_preferences": {},
            "lifestyle_patterns": {},
            "medical_adherence": {}
        }
        
        return {
            "user_id": str(current_user.id),
            "user_profile": user_profile,
            "personalized_thresholds": thresholds,
            "nutrition_targets": nutrition_targets,
            "learning_patterns": learning_patterns,
            "personalization_score": 0.5,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting personalization profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving personalization profile"
        )


@router.post("/thresholds/update")
async def update_personalization_thresholds(
    thresholds: Dict[str, float],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's personalized ML thresholds."""
    try:
        personalization_service = UserPersonalizationService(db)
        
        # Validate threshold values
        valid_keys = ['high_risk_threshold', 'medium_risk_threshold', 'confidence_threshold']
        for key, value in thresholds.items():
            if key not in valid_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid threshold key: {key}"
                )
            if not 0.0 <= value <= 1.0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Threshold values must be between 0.0 and 1.0"
                )
        
        # Update thresholds
        updated_thresholds = await personalization_service._update_personalized_thresholds(
            current_user.id, thresholds
        )
        
        return {
            "message": "Thresholds updated successfully",
            "updated_thresholds": updated_thresholds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating personalization thresholds"
        )


@router.get("/recommendations/adaptive")
async def get_adaptive_recommendations(
    timeframe: str = "week",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get adaptive recommendations based on user's learning patterns."""
    try:
        personalization_service = UserPersonalizationService(db)
        
        # Prepare basic user data
        user_data = {
            "user_id": current_user.id,
            "timeframe": timeframe
        }
        
        # Get current predictions (simplified for this endpoint)
        current_predictions = {
            "risk_level": "medium",
            "confidence": 0.75,
            "risk_score": 0.5
        }
        
        # Get adaptive recommendations
        recommendations = await personalization_service.get_adaptive_recommendations(
            current_user.id, user_data, current_predictions
        )
        
        return {
            "user_id": current_user.id,
            "timeframe": timeframe,
            "adaptive_recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting adaptive recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving adaptive recommendations"
        )


@router.post("/feedback")
async def submit_personalization_feedback(
    feedback: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback to improve personalization algorithms."""
    try:
        personalization_service = UserPersonalizationService(db)
        
        # Validate feedback structure
        required_fields = ['recommendation_id', 'effectiveness_score', 'feedback_type']
        for field in required_fields:
            if field not in feedback:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Process feedback
        feedback_data = {
            "user_id": current_user.id,
            "recommendation_id": feedback['recommendation_id'],
            "effectiveness_score": feedback['effectiveness_score'],
            "feedback_type": feedback['feedback_type'],
            "comments": feedback.get('comments', ''),
            "timestamp": datetime.utcnow()
        }
        
        # Update learning patterns based on feedback
        await personalization_service.update_user_learning_patterns(
            current_user.id, feedback_data, {}
        )
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": f"fb_{current_user.id}_{int(datetime.utcnow().timestamp())}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting personalization feedback"
        )


@router.get("/analytics")
async def get_personalization_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics about user's personalization effectiveness."""
    try:
        personalization_service = UserPersonalizationService(db)
        
        # Get learning patterns and analytics
        learning_patterns = await personalization_service._analyze_user_learning_patterns(current_user.id)
        
        # Calculate effectiveness metrics
        effectiveness_metrics = {
            "prediction_accuracy": learning_patterns.get('prediction_accuracy', 0.7),
            "recommendation_effectiveness": learning_patterns.get('recommendation_effectiveness', 0.75),
            "adaptation_rate": learning_patterns.get('adaptation_rate', 0.6),
            "personalization_maturity": learning_patterns.get('learning_score', 0.5)
        }
        
        # Get historical trends (mock data for now)
        historical_trends = {
            "accuracy_trend": [0.6, 0.65, 0.7, 0.72, 0.75],
            "effectiveness_trend": [0.7, 0.72, 0.75, 0.77, 0.8],
            "weeks": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
        }
        
        return {
            "user_id": current_user.id,
            "effectiveness_metrics": effectiveness_metrics,
            "historical_trends": historical_trends,
            "total_interactions": learning_patterns.get('total_interactions', 0),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting personalization analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving personalization analytics"
        )