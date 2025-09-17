"""
ML Predictions API

API endpoints for machine learning predictions including severity assessment,
flareup prediction, and personalized recommendations.
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
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.models.medication import MedicationLog
from app.services.ml_model_service import MLModelService
from app.schemas.ml_predictions import (
    SeverityPredictionRequest,
    SeverityPredictionResponse,
    FlareupPredictionRequest,
    FlareupPredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
    ModelInfoResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Predictions"])

# Global ML service instance
ml_service = MLModelService()


@router.get("/models/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about loaded ML models."""
    try:
        info = ml_service.get_model_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving model information"
        )


@router.post("/models/reload")
async def reload_models():
    """Reload ML models from the latest checkpoint."""
    try:
        ml_service.reload_models()
        return {"message": "Models reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reloading models"
        )


@router.post("/predict/severity", response_model=SeverityPredictionResponse)
async def predict_severity(
    request: SeverityPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict IBS severity based on current symptoms and user data."""
    try:
        # Prepare user data for prediction
        user_data = await _prepare_user_data(current_user, db, request.symptoms)
        
        # Make prediction
        prediction = ml_service.predict_severity(user_data)
        
        # Store prediction in database for tracking
        await _store_prediction(
            db, current_user.id, "severity", prediction, request.dict()
        )
        
        return SeverityPredictionResponse(
            severity_score=prediction['severity_score'],
            severity_level=prediction['severity_level'],
            confidence=prediction['confidence'],
            model_version=prediction['model_version'],
            predicted_at=datetime.utcnow(),
            factors=_extract_severity_factors(user_data, prediction)
        )
        
    except Exception as e:
        logger.error(f"Error in severity prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error predicting severity"
        )


@router.post("/predict/flareup", response_model=FlareupPredictionResponse)
async def predict_flareup(
    request: FlareupPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict flareup risk for the next N days."""
    try:
        # Prepare user data for prediction
        user_data = await _prepare_user_data(current_user, db, request.symptoms)
        
        # Add recent symptom trends
        user_data['recent_symptoms'] = await _get_recent_symptom_trends(
            current_user.id, db
        )
        
        # Make prediction
        prediction = ml_service.predict_flareup_risk(user_data, request.days_ahead)
        
        # Store prediction in database
        await _store_prediction(
            db, current_user.id, "flareup", prediction, request.dict()
        )
        
        return FlareupPredictionResponse(
            risk_score=prediction['risk_score'],
            risk_level=prediction['risk_level'],
            days_ahead=prediction['days_ahead'],
            confidence=prediction['confidence'],
            model_version=prediction['model_version'],
            predicted_at=datetime.utcnow(),
            risk_factors=_extract_risk_factors(user_data, prediction)
        )
        
    except Exception as e:
        logger.error(f"Error in flareup prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error predicting flareup risk"
        )


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized diet and lifestyle recommendations."""
    try:
        # Prepare user data for recommendations
        user_data = await _prepare_user_data(current_user, db, request.symptoms)
        
        # Add dietary patterns
        user_data['diet'] = await _get_dietary_patterns(current_user.id, db)
        
        # Generate recommendations
        recommendations = ml_service.generate_recommendations(user_data)
        
        # Store recommendations in database
        await _store_prediction(
            db, current_user.id, "recommendations", recommendations, request.dict()
        )
        
        return RecommendationResponse(
            diet_recommendations=recommendations['diet_recommendations'],
            lifestyle_recommendations=recommendations['lifestyle_recommendations'],
            diet_score=recommendations['diet_score'],
            lifestyle_score=recommendations['lifestyle_score'],
            model_version=recommendations['model_version'],
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations"
        )


async def _prepare_user_data(
    user: User, 
    db: AsyncSession, 
    symptoms: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Prepare user data for ML predictions."""
    
    # Calculate user profile features
    age = (datetime.utcnow().date() - user.date_of_birth).days // 365 if user.date_of_birth else 30
    bmi = user.weight_kg / ((user.height_cm / 100) ** 2) if user.height_cm and user.weight_kg else 25.0
    years_since_diagnosis = (datetime.utcnow().date() - user.diagnosis_date).days // 365 if user.diagnosis_date else 1
    
    user_data = {
        'profile': {
            'age': age,
            'gender': user.gender,
            'bmi': bmi,
            'years_since_diagnosis': years_since_diagnosis,
            'ibs_subtype': user.ibs_subtype
        },
        'symptoms': symptoms or {}
    }
    
    # If no symptoms provided, get the most recent symptom log
    if not symptoms:
        recent_symptom = db.query(SymptomLog).filter(
            SymptomLog.user_id == user.id
        ).order_by(SymptomLog.logged_at.desc()).first()
        
        if recent_symptom:
            user_data['symptoms'] = {
                'abdominal_pain': _severity_to_numeric(recent_symptom.abdominal_pain),
                'bloating': _severity_to_numeric(recent_symptom.bloating),
                'gas': _severity_to_numeric(recent_symptom.gas),
                'diarrhea': _severity_to_numeric(recent_symptom.diarrhea),
                'constipation': _severity_to_numeric(recent_symptom.constipation),
                'urgency': _severity_to_numeric(recent_symptom.urgency),
                'incomplete_evacuation': _severity_to_numeric(recent_symptom.incomplete_evacuation),
                'nausea': _severity_to_numeric(recent_symptom.nausea),
                'fatigue': _severity_to_numeric(recent_symptom.fatigue),
                'mood_score': recent_symptom.mood_score or 5,
                'stress_level': recent_symptom.stress_level or 5,
                'sleep_quality': recent_symptom.sleep_quality or 5
            }
    
    return user_data


async def _get_recent_symptom_trends(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get recent symptom trends for the user."""
    # Get symptoms from the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(SymptomLog).filter(
            SymptomLog.user_id == user_id,
            SymptomLog.logged_at >= seven_days_ago
        )
    )
    recent_symptoms = result.scalars().all()
    
    if not recent_symptoms:
        return {
            'avg_severity_7d': 0,
            'symptom_frequency_7d': 0,
            'stress_trend': 0
        }
    
    # Calculate averages
    severity_scores = []
    stress_levels = []
    
    for symptom in recent_symptoms:
        # Calculate overall severity score
        severity_score = (
            _severity_to_numeric(symptom.abdominal_pain) +
            _severity_to_numeric(symptom.bloating) +
            _severity_to_numeric(symptom.diarrhea) +
            _severity_to_numeric(symptom.constipation)
        ) / 4
        severity_scores.append(severity_score)
        
        if symptom.stress_level:
            stress_levels.append(symptom.stress_level)
    
    return {
        'avg_severity_7d': sum(severity_scores) / len(severity_scores),
        'symptom_frequency_7d': len(recent_symptoms),
        'stress_trend': sum(stress_levels) / len(stress_levels) if stress_levels else 5
    }


async def _get_dietary_patterns(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get dietary patterns for the user."""
    # Get diet logs from the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(DietLog).filter(
            DietLog.user_id == user_id,
            DietLog.consumed_at >= thirty_days_ago
        )
    )
    diet_logs = result.scalars().all()
    
    if not diet_logs:
        return {
            'fodmap_adherence': 0.5,
            'fiber_intake': 25.0,
            'trigger_food_frequency': 0.1
        }
    
    # Calculate dietary metrics (simplified since DietLog doesn't have these fields)
    total_logs = len(diet_logs)
    
    # For now, return default values since the DietLog model doesn't have
    # fodmap_level, trigger_foods, or fiber_grams fields
    return {
        'fodmap_adherence': 0.7,  # Default moderate adherence
        'fiber_intake': 25.0,     # Default recommended fiber intake
        'trigger_food_frequency': 0.2  # Default low trigger frequency
    }


async def _store_prediction(
    db: AsyncSession,
    user_id: str,
    prediction_type: str,
    prediction_data: Dict[str, Any],
    input_data: Dict[str, Any]
):
    """Store ML prediction in the database."""
    try:
        from app.models.ml_prediction import MLPrediction
        
        prediction = MLPrediction(
            user_id=user_id,
            prediction_type=prediction_type,
            model_version=prediction_data.get('model_version', 'unknown'),
            input_data=input_data,
            prediction_data=prediction_data,
            confidence_score=prediction_data.get('confidence', 0.5),
            predicted_at=datetime.utcnow()
        )
        
        db.add(prediction)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error storing prediction: {e}")
        db.rollback()


def _severity_to_numeric(severity: str) -> int:
    """Convert severity enum to numeric value."""
    severity_map = {
        'none': 0,
        'mild': 1,
        'moderate': 2,
        'severe': 3
    }
    return severity_map.get(severity, 0)


def _extract_severity_factors(user_data: Dict[str, Any], prediction: Dict[str, Any]) -> List[str]:
    """Extract factors contributing to severity prediction."""
    factors = []
    symptoms = user_data.get('symptoms', {})
    
    if symptoms.get('stress_level', 0) > 6:
        factors.append("High stress levels")
    
    if symptoms.get('sleep_quality', 10) < 5:
        factors.append("Poor sleep quality")
    
    if symptoms.get('abdominal_pain', 0) > 2:
        factors.append("Severe abdominal pain")
    
    if symptoms.get('bloating', 0) > 2:
        factors.append("Significant bloating")
    
    return factors


def _extract_risk_factors(user_data: Dict[str, Any], prediction: Dict[str, Any]) -> List[str]:
    """Extract factors contributing to flareup risk."""
    factors = []
    symptoms = user_data.get('symptoms', {})
    recent_symptoms = user_data.get('recent_symptoms', {})
    
    if recent_symptoms.get('avg_severity_7d', 0) > 1.5:
        factors.append("Increasing symptom severity trend")
    
    if recent_symptoms.get('stress_trend', 0) > 6:
        factors.append("Elevated stress levels")
    
    if symptoms.get('urgency', 0) > 2:
        factors.append("High urgency symptoms")
    
    diet = user_data.get('diet', {})
    if diet.get('trigger_food_frequency', 0) > 0.3:
        factors.append("Frequent trigger food consumption")
    
    return factors