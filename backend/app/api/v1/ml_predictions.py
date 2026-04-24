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
from app.core.dynamic_config import get_config
from app.models import User, SymptomLog, DietLog, MedicationLog
from app.services.enhanced_recommendation_service import EnhancedRecommendationService
from app.services.dynamic_data_service import DynamicDataService
from app.services.user_personalization_service import UserPersonalizationService
from app.schemas.ml_predictions import (
    SeverityPredictionRequest,
    SeverityPredictionResponse,
    FlareupPredictionRequest,
    FlareupPredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
    ModelInfoResponse,
    MedicationEffectivenessRequest,
    MedicationEffectivenessResponse,
    DietaryTriggerRequest,
    DietaryTriggerResponse,
    StressSymptomCorrelationRequest,
    StressSymptomCorrelationResponse,
    SleepQualityImpactRequest,
    SleepQualityImpactResponse,
    ExerciseToleranceRequest,
    ExerciseToleranceResponse,
    SymptomProgressionRequest,
    SymptomProgressionResponse,
    TreatmentResponseRequest,
    TreatmentResponseResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ML Predictions"])

# Global enhanced recommendation service instance - will be initialized on first use
enhanced_recommendation_service = None


async def get_enhanced_recommendation_service(
    db: AsyncSession = Depends(get_db),
) -> EnhancedRecommendationService:
    """Get or create the enhanced recommendation service instance."""
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


@router.get("/models/info", response_model=ModelInfoResponse)
async def get_model_info(
    current_user: User = Depends(get_current_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Get information about loaded enhanced ML models."""
    try:
        info = service.get_model_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving model information",
        )


@router.post("/models/reload")
async def reload_models(
    current_user: User = Depends(get_current_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Reload enhanced ML models from the latest checkpoint."""
    try:
        service.reload_models()
        return {"message": "Enhanced models reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reloading models",
        )


@router.post("/predict/severity", response_model=SeverityPredictionResponse)
async def predict_severity(
    request: SeverityPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Predict IBS severity based on current symptoms and user data."""
    try:
        # Prepare user data for prediction
        user_data = await _prepare_user_data(current_user, db, request.symptoms)

        # Check if ML models are available
        model_info = service.get_model_info()

        if model_info["active_models"] == 0:
            # No models loaded, use fallback prediction
            symptoms = user_data.get("symptoms", {})
            avg_severity = (
                sum(
                    symptoms.get(k, 0)
                    for k in [
                        "abdominal_pain",
                        "bloating",
                        "gas",
                        "diarrhea",
                        "constipation",
                        "urgency",
                    ]
                )
                / 6
            )
            severity_level = (
                "High"
                if avg_severity > 2.5
                else "Medium"
                if avg_severity > 1.5
                else "Low"
            )

            prediction = {
                "severity_score": round(avg_severity, 2),
                "severity_level": severity_level,
                "confidence": 0.6,
                "model_version": "fallback_rule_based",
            }
        else:
            # Make prediction using enhanced service
            prediction = service.predict_symptom_risk(user_data)

        # Store prediction in database for tracking
        await _store_prediction(
            db, current_user.id, "severity", prediction, request.dict()
        )

        return SeverityPredictionResponse(
            severity_score=prediction.get(
                "severity_score", prediction.get("risk_probability", 0.5)
            ),
            severity_level=prediction.get(
                "severity_level", prediction.get("risk_level", "Medium")
            ),
            confidence=prediction.get("confidence", 0.6),
            contributing_factors=_extract_severity_factors(user_data, prediction),
            recommendations=_generate_severity_recommendations(user_data, prediction),
        )

    except Exception as e:
        logger.error(f"Error in severity prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error predicting severity",
        )


@router.post("/predict/flareup", response_model=FlareupPredictionResponse)
async def predict_flareup(
    request: FlareupPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Predict flareup risk for the next N days."""
    try:
        # Extract symptoms from recent_symptoms data for user preparation
        latest_symptoms = {}
        if request.recent_symptoms:
            # Get the most recent symptom entry
            latest_entry = request.recent_symptoms[-1]
            # Ensure latest_entry is a dictionary before calling .get()
            if isinstance(latest_entry, dict):
                latest_symptoms = latest_entry.get("symptoms", {})
            else:
                # If latest_entry is not a dict, treat it as symptoms directly
                latest_symptoms = latest_entry if isinstance(latest_entry, dict) else {}
        
        # Prepare user data for prediction
        user_data = await _prepare_user_data(current_user, db, latest_symptoms)

        # Add recent symptom trends from request
        user_data["recent_symptoms"] = request.recent_symptoms
        user_data["lifestyle_factors"] = request.lifestyle_factors
        user_data["prediction_horizon"] = request.prediction_horizon

        # Get dynamic configuration
        config = get_config()

        # Check if models are loaded, use fallback if not
        if not service.ml_models:
            # Fallback prediction based on recent symptom trends using dynamic weights
            symptoms = user_data.get("symptoms", {})
            _recent_symptoms = user_data.get("recent_symptoms", [])

            # Calculate risk based on symptom severity and trends
            avg_severity = (
                sum(
                    [
                        symptoms.get("abdominal_pain", 0),
                        symptoms.get("bloating", 0),
                        symptoms.get("diarrhea", 0),
                        symptoms.get("constipation", 0),
                        symptoms.get("urgency", 0),
                    ]
                )
                / 5.0
            )

            # Adjust for stress and sleep using configurable weights
            stress_factor = symptoms.get("stress_level", 5) / 10.0
            sleep_factor = (10 - symptoms.get("sleep_quality", 5)) / 10.0

            # Use dynamic weights from configuration
            risk_score = min(
                1.0,
                (
                    avg_severity / 10.0 * config.ml_model.symptom_weight
                    + stress_factor * config.ml_model.stress_weight
                    + sleep_factor * config.ml_model.sleep_weight
                ),
            )

            # Use dynamic risk level determination
            risk_level = config.get_risk_level(risk_score).value.title()

            prediction = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "days_ahead": request.prediction_horizon or 7,
                "confidence": config.ml_model.default_confidence,
                "model_version": config.ml_model.fallback_model_version,
            }
        else:
            # Make prediction using enhanced service
            prediction = service.predict_symptom_risk(user_data)

        # Store prediction in database
        await _store_prediction(
            db, current_user.id, "flareup", prediction, request.dict()
        )

        return FlareupPredictionResponse(
            flareup_probability=prediction.get(
                "risk_score", prediction.get("risk_probability", 0.5)
            ),
            risk_level=prediction.get("risk_level", "moderate"),
            peak_risk_days=prediction.get("peak_risk_days", [3, 5, 7]),
            risk_factors=_extract_risk_factors(user_data, prediction),
            prevention_strategies=_generate_prevention_strategies(user_data, prediction),
        )

    except Exception as e:
        logger.error(f"Error in flareup prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error predicting flareup risk",
        )


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Generate personalized diet and lifestyle recommendations."""
    try:
        # Prepare user data for recommendations
        user_data = await _prepare_user_data(current_user, db, request.current_symptoms)

        # Add dietary patterns
        user_data["diet"] = await _get_dietary_patterns(current_user.id, db)

        # Create ML predictions format from user data
        ml_predictions = {
            "severity_prediction": {
                "predicted_severity": user_data.get("current_severity", "medium"),
                "confidence": 0.7
            },
            "flareup_risk": {
                "risk_level": "moderate",
                "confidence": 0.6
            },
            "recommendations": {
                "dietary_suggestions": [],
                "lifestyle_changes": [],
                "immediate_actions": []
            },
            "confidence": 0.7
        }

        # Generate enhanced recommendations
        recommendations = await service.generate_enhanced_recommendations(
            current_user.id, ml_predictions
        )

        # Store recommendations in database
        await _store_prediction(
            db, current_user.id, "recommendations", recommendations, request.dict()
        )

        return RecommendationResponse(
            recommendations={
                "dietary": recommendations.get("diet_recommendations", []),
                "lifestyle": recommendations.get("lifestyle_recommendations", []),
                "immediate": recommendations.get("immediate_actions", []),
                "supplements": recommendations.get("nutrition_optimization", [])
            },
            personalization_score=recommendations.get("personalization_score", 0.0),
            implementation_priority=["dietary", "lifestyle", "immediate", "supplements"],
            expected_timeline={
                "dietary": "1-2 weeks",
                "lifestyle": "2-4 weeks", 
                "immediate": "immediate",
                "supplements": "4-6 weeks"
            }
        )

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations",
        )


@router.get("/predictions")
async def get_predictions(
    timeframe: str = "week",
    include_recommendations: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ML predictions for the user based on their data with personalization."""
    try:
        # Prepare basic user data for prediction
        user_data = await _prepare_user_data(current_user, db)

        # Add recent symptom trends based on timeframe
        if timeframe == "day":
            days_back = 1
        elif timeframe == "week":
            days_back = 7
        else:  # month
            days_back = 30

        user_data["recent_symptoms"] = await _get_recent_symptom_trends(
            str(current_user.id), db, days_back
        )

        # Default personalized thresholds (simplified for now)
        personalized_thresholds = {
            "high_risk_threshold": 0.7,
            "medium_risk_threshold": 0.4,
            "learning_score": 0.5,
        }

        # Apply personalized thresholds to user data
        user_data["personalized_thresholds"] = personalized_thresholds

        # Calculate real predictions from user data
        from sqlalchemy import func as sqlfunc
        from app.models.diet import DietLog, Food
        from app.models.symptom import SymptomLog

        cutoff = datetime.utcnow() - timedelta(days=days_back)

        # Get recent symptom logs
        sym_result = await db.execute(
            select(SymptomLog)
            .where(SymptomLog.user_id == current_user.id)
            .where(SymptomLog.logged_at >= cutoff)
            .order_by(SymptomLog.logged_at.desc())
        )
        recent_symptoms = sym_result.scalars().all()

        # Calculate risk level from real symptom data
        if recent_symptoms:
            severities = []
            for s in recent_symptoms:
                sev_map = {"none": 0, "mild": 2, "moderate": 5, "severe": 8, "very_severe": 10}
                severities.append(sev_map.get(str(s.severity).lower(), 5))
            avg_severity = sum(severities) / len(severities)
            if avg_severity >= 7:
                risk_level = "high"
                risk_score = 0.8
            elif avg_severity >= 4:
                risk_level = "medium"
                risk_score = 0.5
            else:
                risk_level = "low"
                risk_score = 0.2
            confidence = min(0.5 + len(recent_symptoms) * 0.05, 0.95)
        else:
            risk_level = "low"
            risk_score = 0.2
            confidence = 0.3
            avg_severity = 0

        # Get real trigger foods from diet logs
        diet_result = await db.execute(
            select(Food.name, Food.fodmap_level, Food.common_triggers)
            .join(DietLog, DietLog.food_id == Food.id)
            .where(DietLog.user_id == current_user.id)
            .where(DietLog.consumed_at >= cutoff)
            .distinct()
        )
        diet_rows = diet_result.all()
        trigger_foods = []
        for name, fodmap, is_trigger in diet_rows:
            if is_trigger or (fodmap and str(fodmap).lower() == "high"):
                trigger_foods.append(name)
        if not trigger_foods:
            trigger_foods = ["Log more meals to identify your trigger foods"]

        # Real recommendations based on data
        recommendations = []
        if recent_symptoms:
            stress_levels = [s.stress_level for s in recent_symptoms if s.stress_level]
            sleep_levels = [s.sleep_quality for s in recent_symptoms if s.sleep_quality]
            if stress_levels and sum(stress_levels)/len(stress_levels) > 6:
                recommendations.append("High stress detected - try relaxation techniques")
            if sleep_levels and sum(sleep_levels)/len(sleep_levels) < 5:
                recommendations.append("Poor sleep detected - maintain consistent sleep schedule")
            if avg_severity > 5:
                recommendations.append("High symptom severity - consider consulting your doctor")
            if trigger_foods and "Log more" not in trigger_foods[0]:
                recommendations.append(f"Avoid recent trigger foods: {', '.join(trigger_foods[:2])}")
        if not recommendations:
            recommendations = [
                "Keep logging daily symptoms for personalized insights",
                "Stay hydrated throughout the day",
                "Log your meals to identify food triggers",
            ]

        # Key factors from real data
        key_factors = []
        if recent_symptoms:
            key_factors.append(f"{len(recent_symptoms)} symptoms logged this period")
        if diet_rows:
            key_factors.append(f"{len(diet_rows)} unique foods consumed")
        stress_vals = [s.stress_level for s in recent_symptoms if s.stress_level]
        if stress_vals:
            key_factors.append(f"Avg stress: {sum(stress_vals)/len(stress_vals):.1f}/10")
        sleep_vals = [s.sleep_quality for s in recent_symptoms if s.sleep_quality]
        if sleep_vals:
            key_factors.append(f"Avg sleep: {sum(sleep_vals)/len(sleep_vals):.1f}/10")
        if not key_factors:
            key_factors = ["Start logging symptoms and meals for AI insights"]

        response = {
            "riskLevel": risk_level,
            "nextFlareRisk": round(risk_score, 2),
            "confidence": round(confidence, 2),
            "triggerFoods": trigger_foods[:5],
            "recommendations": recommendations[:5],
            "keyFactors": key_factors[:4],
            "timeline": f"Next {timeframe}",
            "modelVersion": "v2.0.0-realdata"
        }
        return response

    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting predictions",
        )


@router.get("/realtime-predictions")
async def get_realtime_predictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Get real-time predictions based on current user state."""
    try:
        # Prepare user data for real-time prediction
        user_data = await _prepare_user_data(current_user, db)

        # Get very recent data (last 24 hours)
        user_data["recent_symptoms"] = await _get_recent_symptom_trends(
            current_user.id, db, 1
        )

        # Make real-time prediction
        prediction = service.predict_symptom_risk(user_data)

        # Generate simple immediate recommendations without async database calls
        risk_level = prediction.get("risk_probability", 0.35)
        immediate_recommendations = []

        if risk_level > 0.7:
            immediate_recommendations = [
                "Consider avoiding trigger foods today",
                "Practice stress reduction techniques",
                "Stay hydrated and rest",
            ]
        elif risk_level > 0.4:
            immediate_recommendations = [
                "Monitor your symptoms closely",
                "Stick to safe foods",
                "Consider light exercise",
            ]
        else:
            immediate_recommendations = [
                "Continue current routine",
                "Maintain balanced diet",
                "Stay active",
            ]

        return {
            "current_risk": risk_level * 100,
            "risk_factors": _extract_risk_factors(user_data, prediction)[:3],  # Top 3
            "immediate_recommendations": immediate_recommendations[:3],
            "confidence_score": prediction.get("confidence", 0.78)
            if isinstance(prediction.get("confidence"), (int, float))
            else 0.78,
        }

    except Exception as e:
        logger.error(f"Error getting realtime predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting realtime predictions",
        )


async def _prepare_user_data(
    user: User, db: AsyncSession, symptoms: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Prepare user data for ML predictions."""

    # Calculate user profile features
    age = (
        (
            datetime.utcnow()
            - datetime.combine(user.date_of_birth, datetime.min.time())
        ).days
        // 365
        if user.date_of_birth
        else 30
    )
    bmi = (
        user.weight_kg / ((user.height_cm / 100) ** 2)
        if user.height_cm and user.weight_kg
        else 25.0
    )
    years_since_diagnosis = (
        (
            datetime.utcnow()
            - datetime.combine(user.diagnosis_date, datetime.min.time())
        ).days
        // 365
        if user.diagnosis_date
        else 1
    )

    user_data = {
        "profile": {
            "age": age,
            "gender": user.gender,
            "bmi": bmi,
            "years_since_diagnosis": years_since_diagnosis,
            "ibs_type": user.ibs_type,
        },
        "symptoms": symptoms or {},
    }

    # If no symptoms provided, get the most recent symptom log
    if not symptoms:
        stmt = (
            select(SymptomLog)
            .where(SymptomLog.user_id == user.id)
            .order_by(SymptomLog.logged_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        recent_symptom = result.scalar_one_or_none()

        if recent_symptom:
            # Since SymptomLog doesn't have specific symptom attributes,
            # we'll use the generic severity and create a default symptom profile
            severity_score = (
                recent_symptom.severity_score
                if hasattr(recent_symptom, "severity_score")
                else _severity_to_numeric(recent_symptom.severity)
            )

            user_data["symptoms"] = {
                "abdominal_pain": severity_score,
                "bloating": severity_score,
                "gas": severity_score,
                "diarrhea": severity_score,
                "constipation": severity_score,
                "urgency": severity_score,
                "incomplete_evacuation": severity_score,
                "nausea": severity_score,
                "fatigue": severity_score,
                "mood_score": recent_symptom.stress_level
                or 5,  # Use stress_level as mood proxy
                "stress_level": recent_symptom.stress_level or 5,
                "sleep_quality": recent_symptom.sleep_quality or 5,
            }

    return user_data


async def _get_recent_symptom_trends(
    user_id: str, db: AsyncSession, days_back: int = 7
) -> Dict[str, Any]:
    """Get recent symptom trends for the user."""
    # Get symptoms from the specified number of days back
    days_ago = datetime.utcnow() - timedelta(days=days_back)
    result = await db.execute(
        select(SymptomLog).filter(
            SymptomLog.user_id == user_id, SymptomLog.logged_at >= days_ago
        )
    )
    recent_symptoms = result.scalars().all()

    if not recent_symptoms:
        return {"avg_severity_7d": 0, "symptom_frequency_7d": 0, "stress_trend": 0}

    # Calculate averages
    severity_scores = []
    stress_levels = []

    for symptom in recent_symptoms:
        # Calculate overall severity score using the actual severity field
        severity_score = (
            symptom.severity_score
            if hasattr(symptom, "severity_score")
            else _severity_to_numeric(symptom.severity)
        )
        severity_scores.append(severity_score)

        if symptom.stress_level:
            stress_levels.append(symptom.stress_level)

    return {
        "avg_severity_7d": sum(severity_scores) / len(severity_scores),
        "symptom_frequency_7d": len(recent_symptoms),
        "stress_trend": sum(stress_levels) / len(stress_levels) if stress_levels else 5,
    }


async def _get_dietary_patterns(user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get dietary patterns for the user."""
    # Get diet logs from the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(DietLog).filter(
            DietLog.user_id == user_id, DietLog.consumed_at >= thirty_days_ago
        )
    )
    diet_logs = result.scalars().all()

    if not diet_logs:
        return {
            "fodmap_adherence": 0.5,
            "fiber_intake": 25.0,
            "trigger_food_frequency": 0.1,
        }

    # Calculate dietary metrics (simplified since DietLog doesn't have these fields)
    _total_logs = len(diet_logs)

    # For now, return default values since the DietLog model doesn't have
    # fodmap_level, trigger_foods, or fiber_grams fields
    return {
        "fodmap_adherence": 0.7,  # Default moderate adherence
        "fiber_intake": 25.0,  # Default recommended fiber intake
        "trigger_food_frequency": 0.2,  # Default low trigger frequency
    }


async def _store_prediction(
    db: AsyncSession,
    user_id: str,
    prediction_type: str,
    prediction_data: Dict[str, Any],
    input_data: Dict[str, Any],
):
    """Store ML prediction in the database."""
    try:
        from app.models.ml_prediction import MLPrediction

        prediction = MLPrediction(
            user_id=user_id,
            prediction_type=prediction_type,
            model_version=prediction_data.get("model_version", "unknown"),
            input_data=input_data,
            prediction_data=prediction_data,
            confidence_score=prediction_data.get("confidence", 0.5),
            predicted_at=datetime.utcnow(),
        )

        db.add(prediction)
        await db.commit()

    except Exception as e:
        logger.error(f"Error storing prediction: {e}")
        db.rollback()


def _severity_to_numeric(severity: str) -> int:
    """Convert severity enum to numeric value."""
    severity_map = {"none": 0, "mild": 1, "moderate": 2, "severe": 3}
    return severity_map.get(severity, 0)


def _extract_severity_factors(
    user_data: Dict[str, Any], prediction: Dict[str, Any]
) -> List[str]:
    """Extract factors contributing to severity prediction."""
    factors = []
    symptoms = user_data.get("symptoms", {})

    if symptoms.get("stress_level", 0) > 6:
        factors.append("High stress levels")

    if symptoms.get("sleep_quality", 10) < 5:
        factors.append("Poor sleep quality")

    if symptoms.get("abdominal_pain", 0) > 2:
        factors.append("Severe abdominal pain")

    if symptoms.get("bloating", 0) > 2:
        factors.append("Significant bloating")

    return factors


def _generate_severity_recommendations(
    user_data: Dict[str, Any], prediction: Dict[str, Any]
) -> List[str]:
    """Generate recommendations based on severity prediction."""
    recommendations = []
    symptoms = user_data.get("symptoms", {})
    severity_level = prediction.get("severity_level", "Medium")

    # High stress recommendations
    if symptoms.get("stress_level", 0) > 6:
        recommendations.append("Practice stress management techniques")
        recommendations.append("Consider meditation or deep breathing exercises")

    # Poor sleep recommendations
    if symptoms.get("sleep_quality", 10) < 5:
        recommendations.append("Improve sleep hygiene")
        recommendations.append("Maintain consistent sleep schedule")

    # High severity recommendations
    if severity_level in ["High", "Severe"] or symptoms.get("abdominal_pain", 0) > 7:
        recommendations.append("Consult healthcare provider")
        recommendations.append("Consider dietary modifications")

    # Bloating recommendations
    if symptoms.get("bloating", 0) > 5:
        recommendations.append("Reduce gas-producing foods")
        recommendations.append("Try gentle abdominal massage")

    # General recommendations if none specific
    if not recommendations:
        recommendations.extend([
            "Monitor symptoms regularly",
            "Maintain food diary",
            "Stay hydrated"
        ])

    return recommendations


def _generate_prevention_strategies(
    user_data: Dict[str, Any], prediction: Dict[str, Any]
) -> List[str]:
    """Generate prevention strategies based on user data and prediction."""
    strategies = []
    
    # Risk level based strategies
    risk_level = prediction.get("risk_level", "moderate")
    if risk_level == "high":
        strategies.extend([
            "Strictly follow your prescribed diet plan",
            "Increase stress management activities",
            "Consider consulting your healthcare provider"
        ])
    elif risk_level == "moderate":
        strategies.extend([
            "Monitor your symptoms closely",
            "Maintain regular meal times",
            "Practice relaxation techniques"
        ])
    else:
        strategies.extend([
            "Continue current management routine",
            "Keep a food and symptom diary"
        ])
    
    # Lifestyle factor based strategies
    lifestyle_factors = user_data.get("lifestyle_factors", {})
    if lifestyle_factors.get("stress_level", 0) > 6:
        strategies.append("Focus on stress reduction techniques")
    if lifestyle_factors.get("sleep_quality", 0) < 5:
        strategies.append("Improve sleep hygiene")
    if lifestyle_factors.get("exercise_frequency", 0) < 3:
        strategies.append("Gradually increase physical activity")
    
    # Recent symptoms based strategies
    recent_symptoms = user_data.get("recent_symptoms", [])
    if recent_symptoms:
        # Get the latest symptom entry
        latest_symptoms = recent_symptoms[-1] if recent_symptoms else {}
        if isinstance(latest_symptoms, dict):
            symptoms_data = latest_symptoms.get("symptoms", {})
            if symptoms_data.get("abdominal_pain", 0) > 5:
                strategies.append("Apply heat therapy for pain relief")
            if symptoms_data.get("diarrhea", 0) > 3:
                strategies.append("Stay hydrated and avoid trigger foods")
            if symptoms_data.get("constipation", 0) > 3:
                strategies.append("Increase fiber intake gradually")
    
    # General prevention strategies
    strategies.extend([
        "Take medications as prescribed",
        "Stay consistent with meal timing",
        "Avoid known trigger foods"
    ])
    
    return list(set(strategies))  # Remove duplicates


# New ML Prediction Endpoints

@router.post("/predict/medication-effectiveness", 
             response_model=MedicationEffectivenessResponse)
async def predict_medication_effectiveness(
    request: MedicationEffectivenessRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Predict medication effectiveness based on user history and current symptoms.
    """
    try:
        # Prepare medication history data
        medication_features = await _prepare_medication_effectiveness_features(
            current_user.id, request, db
        )
        
        # Use enhanced recommendation service for prediction
        prediction = await service.predict_medication_effectiveness(
            medication_features
        )
        
        # Map service response to schema requirements
        response_data = {
            "effectiveness_score": prediction.get("effectiveness_score", 0.0),
            "confidence": prediction.get("confidence", 0.0),
            "predicted_improvement": {
                "abdominal_pain": prediction.get("predicted_improvement", 0.3),
                "diarrhea": prediction.get("predicted_improvement", 0.3) * 0.8,
                "bloating": prediction.get("predicted_improvement", 0.3) * 0.9,
                "constipation": prediction.get("predicted_improvement", 0.3) * 0.7,
                "nausea": prediction.get("predicted_improvement", 0.3) * 0.6
            }
        }
        
        # Store prediction
        await _store_prediction(
            db,
            current_user.id,
            "medication_effectiveness",
            prediction,
            request.model_dump(),
        )
        
        return MedicationEffectivenessResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error predicting medication effectiveness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to predict medication effectiveness"
        )


@router.post("/predict/dietary-triggers", response_model=DietaryTriggerResponse)
async def predict_dietary_triggers(
    request: DietaryTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Identify dietary triggers based on food diary and symptom correlation.
    """
    try:
        # Prepare dietary analysis data
        dietary_features = await _prepare_dietary_trigger_features(
            current_user.id, request, db
        )
        
        # Use enhanced recommendation service for analysis
        prediction = await service.analyze_dietary_triggers(dietary_features)
        
        # Store prediction
        await _store_prediction(
            db,
            current_user.id,
            "dietary_triggers",
            prediction,
            request.model_dump(),
        )
        
        return DietaryTriggerResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error analyzing dietary triggers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze dietary triggers"
        )


@router.post("/predict/stress-symptom-correlation", 
             response_model=StressSymptomCorrelationResponse)
async def predict_stress_symptom_correlation(
    request: StressSymptomCorrelationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Analyze stress-symptom correlations and provide targeted interventions.
    """
    try:
        # Prepare stress-symptom correlation data
        correlation_features = await _prepare_stress_correlation_features(
            current_user.id, request, db
        )
        
        # Use enhanced recommendation service for analysis
        prediction = await service.analyze_stress_symptom_correlation(
            correlation_features
        )
        
        # Store prediction
        await _store_prediction(
            db,
            current_user.id,
            "stress_symptom_correlation",
            prediction,
            request.model_dump(),
        )
        
        return StressSymptomCorrelationResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error analyzing stress-symptom correlation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze stress-symptom correlation"
        )


@router.post("/predict/sleep-quality-impact", 
             response_model=SleepQualityImpactResponse)
async def predict_sleep_quality_impact(
    request: SleepQualityImpactRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Analyze sleep quality impact on IBS symptoms and provide recommendations.
    """
    try:
        # Prepare sleep analysis data
        sleep_features = await _prepare_sleep_quality_features(
            current_user.id, request, db
        )
        
        # Use enhanced recommendation service for analysis
        prediction = await service.analyze_sleep_quality_impact(sleep_features)
        
        # Store prediction
        await _store_prediction(
            db,
            current_user.id,
            "sleep_quality_impact",
            prediction,
            request.model_dump(),
        )
        
        return SleepQualityImpactResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error analyzing sleep quality impact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze sleep quality impact"
        )


@router.post("/predict/exercise-tolerance", 
             response_model=ExerciseToleranceResponse)
async def predict_exercise_tolerance(
    request: ExerciseToleranceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Predict exercise tolerance and provide personalized exercise recommendations.
    """
    try:
        # Prepare exercise tolerance data
        exercise_features = await _prepare_exercise_tolerance_features(
            current_user.id, request, db
        )
        
        # Use enhanced recommendation service for prediction
        prediction = await service.predict_exercise_tolerance(exercise_features)
        
        # Store prediction
        await _store_prediction(
            db,
            current_user.id,
            "exercise_tolerance",
            prediction,
            request.model_dump(),
        )
        
        return ExerciseToleranceResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error predicting exercise tolerance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to predict exercise tolerance"
        )


# Helper functions for new prediction types


async def _prepare_sleep_quality_features(
    user_id: int, request: SleepQualityImpactRequest, db: AsyncSession
) -> dict:
    """Prepare features for sleep quality impact analysis."""
    # Get recent symptom logs
    recent_symptoms = await db.execute(
        select(SymptomLog)
        .where(SymptomLog.user_id == user_id)
        .order_by(SymptomLog.logged_at.desc())
        .limit(30)
    )
    symptoms = recent_symptoms.scalars().all()
    
    return {
        "sleep_duration": request.sleep_duration,
        "sleep_quality": request.sleep_quality,
        "bedtime": request.bedtime,
        "wake_time": request.wake_time,
        "sleep_interruptions": request.sleep_interruptions,
        "recent_symptoms": [
            {
                "severity": s.severity.value,
                "logged_at": s.logged_at.isoformat(),
                "symptoms": s.symptoms,
            }
            for s in symptoms
        ],
        "user_id": user_id,
    }


async def _prepare_exercise_tolerance_features(
    user_id: int, request: ExerciseToleranceRequest, db: AsyncSession
) -> dict:
    """Prepare features for exercise tolerance prediction."""
    # Get recent symptom logs
    recent_symptoms = await db.execute(
        select(SymptomLog)
        .where(SymptomLog.user_id == user_id)
        .order_by(SymptomLog.logged_at.desc())
        .limit(30)
    )
    symptoms = recent_symptoms.scalars().all()
    
    return {
        "current_fitness_level": request.current_fitness_level,
        "exercise_history": request.exercise_history,
        "preferred_activities": request.preferred_activities,
        "time_availability": request.time_availability,
        "symptom_triggers": request.symptom_triggers,
        "recent_symptoms": [
            {
                "severity": s.severity.value,
                "logged_at": s.logged_at.isoformat(),
                "symptoms": s.symptoms,
            }
            for s in symptoms
        ],
        "user_id": user_id,
    }


async def _prepare_medication_effectiveness_features(
    user_id: str, request: MedicationEffectivenessRequest, db: AsyncSession
) -> Dict[str, Any]:
    """Prepare features for medication effectiveness prediction."""
    # Get recent medication logs
    result = await db.execute(
        select(MedicationLog)
        .where(MedicationLog.user_id == user_id)
        .order_by(MedicationLog.taken_at.desc())
        .limit(50)
    )
    medication_logs = result.scalars().all()
    
    return {
        "medication_history": request.medication_history,
        "current_symptoms": request.current_symptoms,
        "user_profile": request.user_profile,
        "prediction_period": request.prediction_period,
        "recent_medication_logs": [
            {
                "medication": log.medication.name if log.medication else "unknown",
                "dosage": log.dosage,
                "taken_at": log.taken_at.isoformat(),
                "adherence": log.adherence.value if log.adherence else "unknown"
            }
            for log in medication_logs
        ]
    }


async def _prepare_dietary_trigger_features(
    user_id: str, request: DietaryTriggerRequest, db: AsyncSession
) -> Dict[str, Any]:
    """Prepare features for dietary trigger analysis."""
    # Get recent diet logs
    result = await db.execute(
        select(DietLog)
        .where(DietLog.user_id == user_id)
        .order_by(DietLog.logged_at.desc())
        .limit(100)
    )
    diet_logs = result.scalars().all()
    
    return {
        "food_diary": request.food_diary,
        "symptom_history": request.symptom_history,
        "user_profile": request.user_profile,
        "analysis_period": request.analysis_period,
        "recent_diet_logs": [
            {
                "food_item": log.food_item.name if log.food_item else "unknown",
                "quantity": log.quantity,
                "meal_type": log.meal_type.value if log.meal_type else "unknown",
                "logged_at": log.logged_at.isoformat()
            }
            for log in diet_logs
        ]
    }


async def _prepare_stress_correlation_features(
    user_id: str, request: StressSymptomCorrelationRequest, db: AsyncSession
) -> Dict[str, Any]:
    """Prepare features for stress-symptom correlation analysis."""
    # Get recent symptom logs with eager loading to avoid lazy loading issues
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(SymptomLog)
        .options(selectinload(SymptomLog.symptom))
        .where(SymptomLog.user_id == user_id)
        .order_by(SymptomLog.logged_at.desc())
        .limit(100)
    )
    symptom_logs = result.scalars().all()
    
    # Convert to simple data structures to avoid SQLAlchemy session issues
    recent_symptom_logs = []
    for log in symptom_logs:
        recent_symptom_logs.append({
            "symptom": log.symptom.name if log.symptom else "unknown",
            "severity": log.severity.value if log.severity else "unknown",
            "logged_at": log.logged_at.isoformat() if log.logged_at else "",
            "notes": log.notes or ""
        })
    
    return {
        "stress_levels": request.stress_levels,
        "symptoms": request.symptoms,
        "timeframe_days": request.timeframe_days,
        "recent_symptom_logs": recent_symptom_logs
    }


def _extract_risk_factors(
    user_data: Dict[str, Any], prediction: Dict[str, Any]
) -> List[str]:
    """Extract factors contributing to flareup risk."""
    factors = []
    symptoms = user_data.get("symptoms", {})
    recent_symptoms = user_data.get("recent_symptoms", [])

    # Calculate average severity from recent symptoms if available
    if recent_symptoms:
        total_severity = 0
        count = 0
        for symptom_entry in recent_symptoms:
            if isinstance(symptom_entry, dict) and "symptoms" in symptom_entry:
                entry_symptoms = symptom_entry["symptoms"]
                if isinstance(entry_symptoms, dict):
                    severity_sum = sum(entry_symptoms.values())
                    total_severity += severity_sum
                    count += len(entry_symptoms)
        
        if count > 0:
            avg_severity = total_severity / count
            if avg_severity > 5:
                factors.append("Increasing symptom severity trend")

    # Check lifestyle factors for stress
    lifestyle_factors = user_data.get("lifestyle_factors", {})
    if lifestyle_factors.get("stress_level", 0) > 6:
        factors.append("Elevated stress levels")

    if symptoms.get("urgency", 0) > 2:
        factors.append("High urgency symptoms")

    diet = user_data.get("diet", {})
    if diet.get("trigger_food_frequency", 0) > 0.3:
        factors.append("Frequent trigger food consumption")

    return factors


@router.post("/predict/symptom-progression", response_model=SymptomProgressionResponse)
async def predict_symptom_progression(
    request: SymptomProgressionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Predict symptom progression over time."""
    try:
        # Prepare features for symptom progression forecasting
        features = await _prepare_symptom_progression_features(
            current_user.id, request, db
        )
        
        # Get prediction from enhanced recommendation service
        prediction = await service.forecast_symptom_progression(features)
        
        # Store prediction
        await _store_prediction(
            db, current_user.id, "symptom_progression", prediction, features
        )
        
        return SymptomProgressionResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error in symptom progression prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate symptom progression forecast"
        )


@router.post("/predict/treatment-response", response_model=TreatmentResponseResponse)
async def predict_treatment_response(
    request: TreatmentResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """Predict treatment response probability."""
    try:
        # Prepare features for treatment response prediction
        features = await _prepare_treatment_response_features(
            current_user.id, request, db
        )
        
        # Get prediction from enhanced recommendation service
        prediction = await service.predict_treatment_response(features)
        
        # Store prediction
        await _store_prediction(
            db, current_user.id, "treatment_response", prediction, features
        )
        
        return TreatmentResponseResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error in treatment response prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate treatment response prediction"
        )


async def _prepare_symptom_progression_features(
    user_id: str, request: SymptomProgressionRequest, db: AsyncSession
) -> Dict[str, Any]:
    """Prepare features for symptom progression forecasting."""
    # Get recent symptom logs
    result = await db.execute(
        select(SymptomLog)
        .where(SymptomLog.user_id == user_id)
        .order_by(SymptomLog.logged_at.desc())
        .limit(200)
    )
    symptom_logs = result.scalars().all()
    
    return {
        "historical_symptoms": request.historical_symptoms,
        "current_treatments": request.current_treatments,
        "lifestyle_factors": request.lifestyle_factors,
        "prediction_horizon": request.prediction_horizon,
        "recent_symptom_logs": [
            {
                "symptom": log.symptom.name if log.symptom else "unknown",
                "severity": log.severity.value if log.severity else "unknown",
                "logged_at": log.logged_at.isoformat(),
                "notes": log.notes
            }
            for log in symptom_logs
        ]
    }


@router.post("/predict/multimodal")
async def predict_multimodal(
    timeframe_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Generate comprehensive multi-modal predictions using integrated data analysis.
    
    This endpoint combines data from multiple sources (symptoms, diet, lifestyle, 
    biometrics) to provide enhanced predictions and insights.
    
    Args:
        timeframe_days: Number of days to analyze (default: 30)
        
    Returns:
        Comprehensive multi-modal predictions and recommendations
    """
    try:
        logger.info(f"Generating multi-modal predictions for user {current_user.id}")
        
        # Generate multi-modal predictions
        predictions = await service.generate_multimodal_predictions(
            user_id=current_user.id,
            timeframe_days=timeframe_days
        )
        
        return {
            "status": "success",
            "data": predictions,
            "message": "Multi-modal predictions generated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating multi-modal predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate multi-modal predictions: {str(e)}"
        )


async def _prepare_treatment_response_features(
    user_id: str, request: TreatmentResponseRequest, db: AsyncSession
) -> Dict[str, Any]:
    """Prepare features for treatment response prediction."""
    # Get recent medication logs
    result = await db.execute(
        select(MedicationLog)
        .where(MedicationLog.user_id == user_id)
        .order_by(MedicationLog.logged_at.desc())
        .limit(100)
    )
    medication_logs = result.scalars().all()
    
    return {
        "treatment_type": request.treatment_type,
        "treatment_details": request.treatment_details,
        "patient_profile": request.patient_profile,
        "historical_responses": request.historical_responses,
        "recent_medication_logs": [
            {
                "medication": log.medication.name if log.medication else "unknown",
                "dosage": log.dosage,
                "logged_at": log.logged_at.isoformat(),
                "notes": log.notes
            }
            for log in medication_logs
        ]
    }
