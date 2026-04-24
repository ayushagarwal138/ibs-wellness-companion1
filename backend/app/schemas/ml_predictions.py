"""
ML Predictions Schemas

Pydantic schemas for ML prediction API requests and responses.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SeverityPredictionRequest(BaseModel):
    symptoms: Dict[str, float] = Field(
        ..., description="Symptom severity scores (0-10)"
    )
    triggers: Optional[Dict[str, Any]] = Field(
        None, description="Potential triggers"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None, description="User context data"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "symptoms": {
                    "abdominal_pain": 7.5,
                    "bloating": 6.0,
                    "gas": 4.5,
                    "diarrhea": 3.0,
                    "constipation": 0.0,
                    "nausea": 2.5,
                },
                "triggers": {
                    "foods": ["dairy", "gluten"],
                    "stress_level": 8,
                    "sleep_quality": 4,
                },
                "user_context": {
                    "age": 32,
                    "gender": "female",
                    "ibs_type": "IBS-D"
                },
            }
        }
    }


class SeverityPredictionResponse(BaseModel):
    severity_level: str = Field(..., description="Predicted severity level")
    severity_score: float = Field(
        ..., description="Numerical severity score (0-10)"
    )
    confidence: float = Field(..., description="Model confidence (0-1)")
    contributing_factors: List[str] = Field(
        ..., description="Key contributing factors"
    )
    recommendations: List[str] = Field(
        ..., description="Immediate recommendations"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "severity_level": "moderate",
                "severity_score": 6.5,
                "confidence": 0.85,
                "contributing_factors": [
                    "high_stress", "dietary_triggers"
                ],
                "recommendations": [
                    "stress_management", "dietary_modification"
                ],
            }
        }
    }


class FlareupPredictionRequest(BaseModel):
    recent_symptoms: List[Dict[str, Any]] = Field(
        ..., description="Recent symptom history"
    )
    lifestyle_factors: Dict[str, Any] = Field(
        ..., description="Current lifestyle factors"
    )
    prediction_horizon: int = Field(
        7, description="Days ahead to predict", ge=1, le=30
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "recent_symptoms": [
                    {
                        "date": "2024-01-15",
                        "symptoms": {"abdominal_pain": 6, "bloating": 7},
                        "triggers": ["stress", "dairy"],
                    }
                ],
                "lifestyle_factors": {
                    "stress_level": 7,
                    "sleep_quality": 5,
                    "exercise_frequency": 2,
                    "diet_adherence": 0.8,
                },
                "prediction_horizon": 7,
            }
        }
    }


class FlareupPredictionResponse(BaseModel):
    flareup_probability: float = Field(
        ..., description="Probability of flareup (0-1)"
    )
    risk_level: str = Field(..., description="Risk level (low/moderate/high)")
    peak_risk_days: List[int] = Field(
        ..., description="Days with highest risk"
    )
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    prevention_strategies: List[str] = Field(
        ..., description="Recommended prevention strategies"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "flareup_probability": 0.65,
                "risk_level": "moderate",
                "peak_risk_days": [3, 5, 7],
                "risk_factors": ["increasing_stress", "dietary_inconsistency"],
                "prevention_strategies": [
                    "stress_reduction", "dietary_monitoring"
                ],
            }
        }
    }


class RecommendationRequest(BaseModel):
    user_profile: Dict[str, Any] = Field(..., description="User profile data")
    current_symptoms: Dict[str, float] = Field(
        ..., description="Current symptom levels"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="User preferences"
    )
    recommendation_types: List[str] = Field(
        ..., description="Types of recommendations requested"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_profile": {
                    "age": 28,
                    "ibs_type": "IBS-M",
                    "dietary_restrictions": ["lactose_intolerant"],
                    "activity_level": "moderate",
                },
                "current_symptoms": {
                    "abdominal_pain": 5.5,
                    "bloating": 7.0,
                    "gas": 4.0,
                },
                "preferences": {
                    "dietary_approach": "low_fodmap",
                    "exercise_preference": "yoga",
                    "supplement_tolerance": "high",
                },
                "recommendation_types": [
                    "dietary", "lifestyle", "supplements"
                ],
            }
        }
    }


class RecommendationResponse(BaseModel):
    recommendations: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Categorized recommendations"
    )
    personalization_score: float = Field(
        ..., description="How personalized the recommendations are (0-1)"
    )
    implementation_priority: List[str] = Field(
        ..., description="Recommended implementation order"
    )
    expected_timeline: Dict[str, str] = Field(
        ..., description="Expected timeline for each category"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": {
                    "dietary": [
                        {
                            "id": "reduce_fodmaps",
                            "title": "Reduce High FODMAP Foods",
                            "description": "Limit onions, garlic, wheat",
                            "priority": "high",
                        }
                    ],
                    "lifestyle": [
                        {
                            "id": "stress_management",
                            "title": "Daily Stress Management",
                            "description": "Practice 10 min meditation daily",
                            "priority": "medium",
                        }
                    ],
                },
                "personalization_score": 0.92,
                "implementation_priority": [
                    "dietary", "lifestyle", "supplements"
                ],
                "expected_timeline": {
                    "dietary": "1-2 weeks",
                    "lifestyle": "2-4 weeks",
                    "supplements": "4-6 weeks",
                },
            }
        }
    }


class ModelMetrics(BaseModel):
    name: str = Field(..., description="Name of the ML model")
    type: str = Field(..., description="Model type (classifier/regressor)")
    accuracy: Optional[float] = Field(
        None, description="Accuracy for classifiers"
    )
    r2_score: Optional[float] = Field(
        None, description="R² score for regressors"
    )
    rmse: Optional[float] = Field(None, description="RMSE for regressors")
    status: str = Field(
        ..., description="Model status (active/training/error/outdated)"
    )
    last_trained: str = Field(..., description="Last training date")
    version: str = Field(..., description="Model version")
    features_count: int = Field(..., description="Number of features")
    training_samples: int = Field(..., description="Number of training samples")
    confidence_threshold: Optional[float] = Field(
        None, description="Confidence threshold for predictions"
    )

    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "name": "Severity Classifier",
                "type": "classifier",
                "accuracy": 0.988,
                "status": "active",
                "last_trained": "2025-10-03T12:18:35.126478",
                "version": "v1.0.0",
                "features_count": 15,
                "training_samples": 1000,
                "confidence_threshold": 0.8
            }
        }
    }


class ModelInfoResponse(BaseModel):
    models: List[ModelMetrics] = Field(
        ..., description="List of all available models"
    )
    total_models: int = Field(..., description="Total number of models")
    active_models: int = Field(..., description="Number of active models")
    average_performance: float = Field(
        ..., description="Average performance across all models"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "models": [
                    {
                        "name": "Severity Classifier",
                        "type": "classifier",
                        "accuracy": 0.988,
                        "status": "active",
                        "last_trained": "2025-10-03T12:18:35.126478",
                        "version": "v1.0.0",
                        "features_count": 15,
                        "training_samples": 1000,
                        "confidence_threshold": 0.8
                    }
                ],
                "total_models": 9,
                "active_models": 9,
                "average_performance": 0.985,
                "last_updated": "2025-10-03T12:18:35.126478"
            }
        }
    }


class PredictionHistoryRequest(BaseModel):
    prediction_type: Optional[str] = Field(
        None,
        description="Filter by prediction type (severity, flareup, etc.)",
    )
    days_back: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days back to retrieve (1-365)"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of predictions to return"
    )


class PredictionHistoryItem(BaseModel):
    id: str = Field(..., description="Prediction ID")
    prediction_type: str = Field(..., description="Type of prediction")
    model_version: str = Field(..., description="Model version used")
    confidence_score: float = Field(..., description="Prediction confidence")
    predicted_at: datetime = Field(..., description="Prediction timestamp")
    prediction_data: Dict[str, Any] = Field(
        ..., description="Prediction results"
    )

    model_config = {"protected_namespaces": ()}


class PredictionHistoryResponse(BaseModel):
    predictions: List[Dict[str, Any]] = Field(
        ..., description="Historical predictions"
    )
    total_count: int = Field(..., description="Total number of predictions")
    date_range: Dict[str, datetime] = Field(
        ..., description="Date range of predictions"
    )
    accuracy_trend: List[Dict[str, Any]] = Field(
        ..., description="Accuracy trend over time"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "predictions": [
                    {
                        "date": "2024-01-15T10:30:00Z",
                        "type": "severity",
                        "prediction": "moderate",
                        "confidence": 0.85,
                        "actual_outcome": "moderate",
                    }
                ],
                "total_count": 45,
                "date_range": {
                    "start": "2023-12-01T00:00:00Z",
                    "end": "2024-01-15T23:59:59Z",
                },
                "accuracy_trend": [
                    {
                        "week": "2024-W02",
                        "accuracy": 0.87,
                        "prediction_count": 12
                    }
                ],
            }
        }
    }


# Legacy schemas for backward compatibility
class MLPredictionRequest(BaseModel):
    symptoms: Dict[str, float] = Field(
        ..., description="Symptom severity scores"
    )
    triggers: Optional[Dict[str, Any]] = Field(
        None, description="Potential triggers"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None, description="User context"
    )


class MLPredictionResponse(BaseModel):
    risk_level: str = Field(..., description="Risk level")
    confidence: float = Field(..., description="Confidence score")
    severity: str = Field(..., description="Severity level")
    timeline: str = Field(..., description="Timeline")
    key_factors: List[str] = Field(..., description="Key factors")
    recommendations: List[str] = Field(..., description="Recommendations")


class PersonalizedRecommendationsResponse(BaseModel):
    recommendations: List[Dict[str, Any]] = Field(
        ..., description="Personalized recommendations"
    )
    confidence: float = Field(..., description="Confidence score")


class RealtimePredictionResponse(BaseModel):
    prediction: str = Field(..., description="Real-time prediction")
    confidence: float = Field(..., description="Confidence score")
    timestamp: datetime = Field(..., description="Prediction timestamp")


class MedicationEffectivenessRequest(BaseModel):
    medication_history: List[Dict[str, Any]] = Field(
        ..., description="History of medications taken"
    )
    current_symptoms: Dict[str, float] = Field(
        ..., description="Current symptom levels"
    )
    user_profile: Dict[str, Any] = Field(
        ..., description="User profile information"
    )
    prediction_period: Optional[int] = Field(
        None, description="Prediction period in days"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "medication_history": [
                    {
                        "medication": "probiotics",
                        "dosage": "1 capsule daily",
                        "frequency": "once daily",
                        "adherence_rate": 0.9,
                        "effectiveness_score": 6,
                        "side_effects": [],
                        "duration_days": 28
                    }
                ],
                "current_symptoms": {
                    "abdominal_pain": 5.0,
                    "diarrhea": 3.0,
                    "bloating": 7.0,
                    "constipation": 2.0,
                    "nausea": 1.0
                },
                "user_profile": {
                    "age": 32,
                    "weight": 65,
                    "ibs_type": "IBS-D",
                    "comorbidities": []
                },
                "prediction_period": 30
            }
        }
    }


class MedicationEffectivenessResponse(BaseModel):
    effectiveness_score: float = Field(..., description="Effectiveness score (0-1)")
    predicted_improvement: Dict[str, float] = Field(..., description="Predicted symptom improvement")
    confidence: float = Field(..., description="Prediction confidence")


class DietaryTriggerRequest(BaseModel):
    foods_consumed: List[str] = Field(..., description="List of foods consumed")
    meal_timing: List[str] = Field(..., description="Meal timing information")
    symptoms: Dict[str, float] = Field(..., description="Symptom levels")


class DietaryTriggerResponse(BaseModel):
    trigger_foods: List[str] = Field(..., description="Identified trigger foods")
    trigger_probability: Dict[str, float] = Field(..., description="Probability for each trigger")
    recommendations: List[str] = Field(..., description="Dietary recommendations")


class StressSymptomCorrelationRequest(BaseModel):
    stress_levels: Dict[str, float] = Field(..., description="Stress level data")
    symptoms: Dict[str, float] = Field(..., description="Symptom data")
    timeframe_days: int = Field(7, description="Analysis timeframe in days")


class StressSymptomCorrelationResponse(BaseModel):
    correlation_score: float = Field(..., description="Stress-symptom correlation")
    stress_triggers: List[str] = Field(..., description="Identified stress triggers")
    management_strategies: List[str] = Field(..., description="Stress management strategies")


class SleepQualityImpactRequest(BaseModel):
    sleep_hours: float = Field(..., description="Hours of sleep")
    sleep_quality: float = Field(..., description="Sleep quality score (1-10)")
    symptoms: Dict[str, float] = Field(..., description="Symptom levels")


class SleepQualityImpactResponse(BaseModel):
    impact_score: float = Field(..., description="Sleep impact on symptoms")
    sleep_recommendations: List[str] = Field(..., description="Sleep improvement recommendations")
    predicted_improvement: Dict[str, float] = Field(..., description="Predicted symptom improvement")


class ExerciseToleranceRequest(BaseModel):
    exercise_type: str = Field(..., description="Type of exercise")
    duration_minutes: int = Field(..., description="Exercise duration")
    intensity: str = Field(..., description="Exercise intensity")
    symptoms: Dict[str, float] = Field(..., description="Symptom levels")


class ExerciseToleranceResponse(BaseModel):
    tolerance_score: float = Field(..., description="Exercise tolerance score")
    recommended_modifications: List[str] = Field(..., description="Exercise modifications")
    optimal_timing: str = Field(..., description="Optimal exercise timing")


class SymptomProgressionRequest(BaseModel):
    current_symptoms: Dict[str, float] = Field(..., description="Current symptom levels")
    historical_data: List[Dict[str, Any]] = Field(..., description="Historical symptom data")
    prediction_days: int = Field(7, description="Days to predict ahead")


class SymptomProgressionResponse(BaseModel):
    progression_forecast: Dict[str, List[float]] = Field(..., description="Symptom progression forecast")
    trend_analysis: Dict[str, str] = Field(..., description="Trend analysis for each symptom")
    intervention_recommendations: List[str] = Field(..., description="Recommended interventions")


class TreatmentResponseRequest(BaseModel):
    treatment_plan: Dict[str, Any] = Field(..., description="Current treatment plan")
    baseline_symptoms: Dict[str, float] = Field(..., description="Baseline symptom levels")
    treatment_duration: int = Field(..., description="Treatment duration in days")


class TreatmentResponseResponse(BaseModel):
    response_probability: float = Field(..., description="Treatment response probability")
    expected_timeline: Dict[str, str] = Field(..., description="Expected improvement timeline")
    monitoring_recommendations: List[str] = Field(..., description="Monitoring recommendations")
