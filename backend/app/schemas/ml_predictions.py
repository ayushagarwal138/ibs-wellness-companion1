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
    triggers: Optional[Dict[str, Any]] = Field(None, description="Potential triggers")
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
                "user_context": {"age": 32, "gender": "female", "ibs_type": "IBS-D"},
            }
        }
    }


class SeverityPredictionResponse(BaseModel):
    severity_level: str = Field(..., description="Predicted severity level")
    severity_score: float = Field(..., description="Numerical severity score (0-10)")
    confidence: float = Field(..., description="Model confidence (0-1)")
    contributing_factors: List[str] = Field(..., description="Key contributing factors")
    recommendations: List[str] = Field(..., description="Immediate recommendations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "severity_level": "moderate",
                "severity_score": 6.5,
                "confidence": 0.85,
                "contributing_factors": ["high_stress", "dietary_triggers"],
                "recommendations": ["stress_management", "dietary_modification"],
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
    prediction_horizon: int = Field(7, description="Days ahead to predict", ge=1, le=30)

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
    flareup_probability: float = Field(..., description="Probability of flareup (0-1)")
    risk_level: str = Field(..., description="Risk level (low/moderate/high)")
    peak_risk_days: List[int] = Field(..., description="Days with highest risk")
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
                "prevention_strategies": ["stress_reduction", "dietary_monitoring"],
            }
        }
    }


class RecommendationRequest(BaseModel):
    user_profile: Dict[str, Any] = Field(..., description="User profile data")
    current_symptoms: Dict[str, float] = Field(
        ..., description="Current symptom levels"
    )
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
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
                "recommendation_types": ["dietary", "lifestyle", "supplements"],
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
                            "description": "Limit onions, garlic, and wheat products",
                            "priority": "high",
                        }
                    ],
                    "lifestyle": [
                        {
                            "id": "stress_management",
                            "title": "Daily Stress Management",
                            "description": "Practice 10 minutes of meditation daily",
                            "priority": "medium",
                        }
                    ],
                },
                "personalization_score": 0.92,
                "implementation_priority": ["dietary", "lifestyle", "supplements"],
                "expected_timeline": {
                    "dietary": "1-2 weeks",
                    "lifestyle": "2-4 weeks",
                    "supplements": "4-6 weeks",
                },
            }
        }
    }


class ModelInfoResponse(BaseModel):
    model_name: str = Field(..., description="Name of the ML model")
    model_version: str = Field(..., description="Version of the model")
    last_trained: datetime = Field(..., description="Last training date")
    accuracy_metrics: Dict[str, float] = Field(
        ..., description="Model accuracy metrics"
    )
    supported_features: List[str] = Field(..., description="Supported input features")

    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "model_name": "IBS_Severity_Predictor_v2",
                "model_version": "2.1.0",
                "last_trained": "2024-01-10T15:30:00Z",
                "accuracy_metrics": {
                    "precision": 0.87,
                    "recall": 0.84,
                    "f1_score": 0.85,
                },
                "supported_features": [
                    "abdominal_pain",
                    "bloating",
                    "gas",
                    "diarrhea",
                    "constipation",
                    "stress_level",
                    "sleep_quality",
                ],
            }
        }
    }


class PredictionHistoryRequest(BaseModel):
    prediction_type: Optional[str] = Field(
        None,
        description="Filter by prediction type (severity, flareup, recommendations)",
    )
    days_back: int = Field(
        default=30, ge=1, le=365, description="Number of days back to retrieve (1-365)"
    )
    limit: int = Field(
        default=50, ge=1, le=200, description="Maximum number of predictions to return"
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
    predictions: List[Dict[str, Any]] = Field(..., description="Historical predictions")
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
                    {"week": "2024-W02", "accuracy": 0.87, "prediction_count": 12}
                ],
            }
        }
    }
