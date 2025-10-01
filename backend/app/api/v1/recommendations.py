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

async def get_enhanced_recommendation_service(db: AsyncSession = Depends(get_db)) -> EnhancedRecommendationService:
    """Get or create enhanced recommendation service instance."""
    global enhanced_recommendation_service
    if enhanced_recommendation_service is None:
        # Create a synchronous session for the service that expects Session
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        
        # Create a synchronous engine and session
        sync_database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        sync_engine = create_engine(sync_database_url)
        sync_session_factory = sessionmaker(bind=sync_engine)
        sync_session = sync_session_factory()
        
        enhanced_recommendation_service = EnhancedRecommendationService(sync_session)
    return enhanced_recommendation_service

@router.get("/personalized")
async def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(get_enhanced_recommendation_service)
):
    """Get personalized dietary and lifestyle recommendations for the user."""
    try:
        # Prepare user data for recommendations
        user_data = await _prepare_user_data(current_user, db)
        
        # Add recent dietary patterns
        user_data['diet'] = await _get_dietary_patterns(current_user.id, db)
        
        # Generate enhanced recommendations
        recommendations = await service.generate_enhanced_recommendations(current_user.id, user_data, db)
        
        # Transform to match frontend expected format
        response = {
            "dietary_recommendations": [
                {
                    "type": rec.get('type', 'general'),
                    "title": rec.get('title', rec.get('action', 'Dietary Recommendation')),
                    "description": rec.get('description', rec.get('explanation', '')),
                    "priority": rec.get('priority', 'medium')
                }
                for rec in recommendations.get('dietary_suggestions', [])
            ],
            "lifestyle_insights": [
                {
                    "category": rec.get('category', 'General'),
                    "insight": rec.get('suggestion', ''),
                    "recommendation": rec.get('impact', ''),
                    "priority": rec.get('priority', 'medium')
                }
                for rec in recommendations.get('lifestyle_changes', [])
            ],
            "trigger_analysis": {
                "primary_category": "Dietary",
                "insights": [
                    factor for factor in recommendations.get('key_factors', [])[:3]
                ]
            },
            "management_strategy": {
                "strategy": "Personalized IBS Management",
                "approach": "Data-driven recommendations based on your symptoms and patterns",
                "timeline": "2-4 weeks for initial results"
            },
            "personalized_tips": [
                action.get('action', '') 
                for action in recommendations.get('immediate_actions', [])[:5]
            ]
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting personalized recommendations"
        )

async def _prepare_user_data(user: User, db: AsyncSession) -> Dict[str, Any]:
    """Prepare user data for recommendation generation."""
    # Get recent symptoms (last 30 days)
    recent_symptoms_query = select(SymptomLog).where(
        SymptomLog.user_id == user.id,
        SymptomLog.logged_at >= datetime.now(timezone.utc) - timedelta(days=30)
    ).order_by(SymptomLog.logged_at.desc())
    
    result = await db.execute(recent_symptoms_query)
    recent_symptoms = result.scalars().all()
    
    # Get recent diet logs (last 14 days)
    recent_diet_query = select(DietLog).where(
        DietLog.user_id == user.id,
        DietLog.consumed_at >= datetime.now(timezone.utc) - timedelta(days=14)
    ).order_by(DietLog.consumed_at.desc())
    
    result = await db.execute(recent_diet_query)
    recent_diet = result.scalars().all()
    
    return {
        "user_id": user.id,
        "age": (datetime.now(timezone.utc).date() - user.date_of_birth).days // 365 if user.date_of_birth else 30,
        "gender": user.gender.value if user.gender and hasattr(user.gender, 'value') else "unknown",
        "ibs_type": user.ibs_type.value if user.ibs_type and hasattr(user.ibs_type, 'value') else "unknown",
        "recent_symptoms": [
            {
                "severity": symptom.severity.value if symptom.severity and hasattr(symptom.severity, 'value') else "mild",
                "logged_at": symptom.logged_at.isoformat(),
                "stress_level": symptom.stress_level or 5,
                "sleep_quality": symptom.sleep_quality or 5
            }
            for symptom in recent_symptoms
        ],
        "recent_diet": [
            {
                "meal_type": diet.meal_type.value if diet.meal_type and hasattr(diet.meal_type, 'value') else "other",
                "consumed_at": diet.consumed_at.isoformat(),
                "portion_size": diet.portion_size_g or 100
            }
            for diet in recent_diet
        ]
    }

async def _get_dietary_patterns(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get user's dietary patterns for the last 30 days."""
    diet_query = select(DietLog).where(
        DietLog.user_id == user_id,
        DietLog.consumed_at >= datetime.now(timezone.utc) - timedelta(days=30)
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
        "most_common_meal": max(meal_types.keys(), key=meal_types.get) if meal_types else "unknown"
    }