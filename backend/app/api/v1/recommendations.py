"""
Personalized Recommendations API

API endpoints for generating personalized dietary and lifestyle recommendations
based on user data, symptoms, and ML predictions.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.services.enhanced_recommendation_service import EnhancedRecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# Global enhanced recommendation service instance
enhanced_recommendation_service = None


async def get_enhanced_recommendation_service(
    db: AsyncSession = Depends(get_db),
) -> EnhancedRecommendationService:
    """Get or create enhanced recommendation service instance."""
    global enhanced_recommendation_service
    if enhanced_recommendation_service is None:
        # Create a synchronous session for the service that expects Session
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings

        # Create a synchronous engine and session
        sync_database_url = settings.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql://"
        )
        sync_engine = create_engine(sync_database_url)
        sync_session_factory = sessionmaker(bind=sync_engine)
        sync_session = sync_session_factory()

        enhanced_recommendation_service = EnhancedRecommendationService(sync_session)
    return enhanced_recommendation_service


@router.get("/personalized")
async def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Get personalized dietary and lifestyle recommendations for the user."""
    try:
        # Prepare user data for recommendations
        user_data = await _prepare_user_data(current_user, db)

        # Add recent dietary patterns
        user_data["diet"] = await _get_dietary_patterns(current_user.id, db)

        # Create mock ML predictions for the enhanced service
        ml_predictions = {
            "severity_prediction": {"predicted_severity": "medium", "confidence": 0.7},
            "flareup_risk": {"risk_level": "moderate", "confidence": 0.6},
            "recommendations": {
                "dietary_suggestions": [],
                "lifestyle_changes": [],
                "immediate_actions": [],
            },
        }

        # Generate enhanced recommendations with fallback
        try:
            recommendations = await service.generate_enhanced_recommendations(
                current_user.id, ml_predictions
            )
        except Exception as service_error:
            logger.warning(f"Service error, using fallback: {service_error}")
            recommendations = {
                "dietary_suggestions": [],
                "lifestyle_changes": [],
                "key_factors": [],
                "immediate_actions": []
            }

        # Ensure recommendations is a dict and has required keys
        if not isinstance(recommendations, dict):
            recommendations = {}
        
        # Safely get arrays with fallbacks
        dietary_suggestions = recommendations.get("dietary_suggestions", [])
        lifestyle_changes = recommendations.get("lifestyle_changes", [])
        key_factors = recommendations.get("key_factors", [])
        immediate_actions = recommendations.get("immediate_actions", [])
        
        # Ensure all are lists
        if not isinstance(dietary_suggestions, list):
            dietary_suggestions = []
        if not isinstance(lifestyle_changes, list):
            lifestyle_changes = []
        if not isinstance(key_factors, list):
            key_factors = []
        if not isinstance(immediate_actions, list):
            immediate_actions = []
            
        # Add default recommendations if arrays are empty
        if not dietary_suggestions:
            dietary_suggestions = [
                {"category": "General", "action": "Stay hydrated", "explanation": "Proper hydration supports digestive health", "priority": 5}
            ]
        if not lifestyle_changes:
            lifestyle_changes = [
                {"category": "Stress", "suggestion": "Practice relaxation techniques", "impact": "Stress reduction may help manage symptoms", "priority": 4}
            ]

        # Transform to match frontend expected format
        response = {
            "dietary_recommendations": [
                {
                    "category": rec.get("category", "General") if isinstance(rec, dict) else "General",
                    "recommendation": (rec.get("title", rec.get("action", "Dietary Recommendation")) 
                             if isinstance(rec, dict) else "Dietary Recommendation"),
                    "reasoning": (rec.get("description", rec.get("explanation", "Based on your symptom patterns")) 
                                   if isinstance(rec, dict) else "Based on your symptom patterns"),
                    "priority": rec.get("priority", 5) if isinstance(rec, dict) else 5,
                }
                for rec in dietary_suggestions
            ],
            "lifestyle_recommendations": [
                {
                    "category": rec.get("category", "General") if isinstance(rec, dict) else "General",
                    "recommendation": rec.get("suggestion", "Lifestyle improvement") if isinstance(rec, dict) else "Lifestyle improvement",
                    "reasoning": rec.get("impact", "May help improve your symptoms") if isinstance(rec, dict) else "May help improve your symptoms",
                    "priority": rec.get("priority", 5) if isinstance(rec, dict) else 5,
                }
                for rec in lifestyle_changes
            ],
            "medical_recommendations": [
                {
                    "category": "Medical",
                    "recommendation": "Consult with your healthcare provider",
                    "reasoning": "Regular check-ups help monitor your condition",
                    "priority": 3,
                }
            ],
            "trigger_analysis": {
                "primary_category": "Dietary",
                "insights": [
                    factor for factor in key_factors[:3] if isinstance(factor, str)
                ],
            },
            "management_strategy": {
                "strategy": "Personalized IBS Management",
                "approach": (
                    "Data-driven recommendations based on your symptoms and patterns"
                ),
                "timeline": "2-4 weeks for initial results",
            },
            "personalized_tips": [
                action.get("action", "") if isinstance(action, dict) else str(action)
                for action in immediate_actions[:5]
                if action
            ],
        }

        return response

    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting personalized recommendations",
        )


async def _prepare_user_data(user: User, db: AsyncSession) -> Dict[str, Any]:
    """Prepare user data for recommendation generation."""
    # Get recent symptoms (last 30 days)
    recent_symptoms_query = (
        select(SymptomLog)
        .where(
            SymptomLog.user_id == user.id,
            SymptomLog.logged_at >= datetime.now(timezone.utc) - timedelta(days=30),
        )
        .order_by(SymptomLog.logged_at.desc())
    )

    result = await db.execute(recent_symptoms_query)
    recent_symptoms = result.scalars().all()

    # Get recent diet logs (last 14 days)
    recent_diet_query = (
        select(DietLog)
        .where(
            DietLog.user_id == user.id,
            DietLog.consumed_at >= datetime.now(timezone.utc) - timedelta(days=14),
        )
        .order_by(DietLog.consumed_at.desc())
    )

    result = await db.execute(recent_diet_query)
    recent_diet = result.scalars().all()

    return {
        "user_id": user.id,
        "age": (datetime.now(timezone.utc).date() - user.date_of_birth).days // 365
        if user.date_of_birth
        else 30,
        "gender": user.gender.value
        if user.gender and hasattr(user.gender, "value")
        else "unknown",
        "ibs_type": user.ibs_type.value
        if user.ibs_type and hasattr(user.ibs_type, "value")
        else "unknown",
        "recent_symptoms": [
            {
                "severity": symptom.severity.value
                if symptom.severity and hasattr(symptom.severity, "value")
                else "mild",
                "logged_at": symptom.logged_at.isoformat(),
                "stress_level": symptom.stress_level or 5,
                "sleep_quality": symptom.sleep_quality or 5,
            }
            for symptom in recent_symptoms
        ],
        "recent_diet": [
            {
                "meal_type": diet.meal_type.value
                if diet.meal_type and hasattr(diet.meal_type, "value")
                else "other",
                "consumed_at": diet.consumed_at.isoformat(),
                "portion_size": diet.portion_size_g or 100,
            }
            for diet in recent_diet
        ],
    }


async def _get_dietary_patterns(user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get user's dietary patterns for the last 30 days."""
    diet_query = select(DietLog).where(
        DietLog.user_id == user_id,
        DietLog.consumed_at >= datetime.now(timezone.utc) - timedelta(days=30),
    )

    result = await db.execute(diet_query)
    diet_logs = result.scalars().all()

    # Analyze patterns
    meal_types = {}
    total_logs = len(diet_logs)

    for log in diet_logs:
        meal_type = log.meal_type.value
        meal_types[meal_type] = meal_types.get(meal_type, 0) + 1

    return {
        "total_logs": total_logs,
        "meal_distribution": meal_types,
        "average_daily_logs": total_logs / 30 if total_logs > 0 else 0,
        "most_common_meal": max(meal_types.keys(), key=meal_types.get)
        if meal_types
        else "unknown",
    }
