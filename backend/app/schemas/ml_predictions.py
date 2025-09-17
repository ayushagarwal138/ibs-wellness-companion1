"""
ML Predictions Schemas

Pydantic schemas for ML prediction API requests and responses.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SeverityPredictionRequest(BaseModel):
    """Request schema for severity prediction."""
    symptoms: Optional[Dict[str, Any]] = Field(
        None,
        description="Current symptoms data. If not provided, uses most recent symptom log."
    )
    
    class Config:
        schema_extra = {
            "example": {
                "symptoms": {
                    "abdominal_pain": 2,
                    "bloating": 3,
                    "gas": 1,
                    "diarrhea": 2,
                    "constipation": 0,
                    "urgency": 2,
                    "incomplete_evacuation": 1,
                    "nausea": 1,
                    "fatigue": 2,
                    "mood_score": 4,
                    "stress_level": 7,
                    "sleep_quality": 3
                }
            }
        }


class SeverityPredictionResponse(BaseModel):
    """Response schema for severity prediction."""
    severity_score: float = Field(..., description="Predicted severity score (0-10)")
    severity_level: str = Field(..., description="Severity level (mild, moderate, severe)")
    confidence: float = Field(..., description="Model confidence (0-1)")
    model_version: str = Field(..., description="Version of the model used")
    predicted_at: datetime = Field(..., description="Timestamp of prediction")
    factors: List[str] = Field(..., description="Factors contributing to severity")
    
    class Config:
        schema_extra = {
            "example": {
                "severity_score": 6.2,
                "severity_level": "moderate",
                "confidence": 0.85,
                "model_version": "v1.2.0",
                "predicted_at": "2024-01-15T10:30:00Z",
                "factors": [
                    "High stress levels",
                    "Poor sleep quality",
                    "Significant bloating"
                ]
            }
        }


class FlareupPredictionRequest(BaseModel):
    """Request schema for flareup prediction."""
    days_ahead: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days ahead to predict (1-30)"
    )
    symptoms: Optional[Dict[str, Any]] = Field(
        None,
        description="Current symptoms data. If not provided, uses most recent symptom log."
    )
    
    class Config:
        schema_extra = {
            "example": {
                "days_ahead": 7,
                "symptoms": {
                    "abdominal_pain": 1,
                    "bloating": 2,
                    "stress_level": 8,
                    "sleep_quality": 4
                }
            }
        }


class FlareupPredictionResponse(BaseModel):
    """Response schema for flareup prediction."""
    risk_score: float = Field(..., description="Flareup risk score (0-1)")
    risk_level: str = Field(..., description="Risk level (low, medium, high)")
    days_ahead: int = Field(..., description="Number of days ahead predicted")
    confidence: float = Field(..., description="Model confidence (0-1)")
    model_version: str = Field(..., description="Version of the model used")
    predicted_at: datetime = Field(..., description="Timestamp of prediction")
    risk_factors: List[str] = Field(..., description="Factors contributing to risk")
    
    class Config:
        schema_extra = {
            "example": {
                "risk_score": 0.72,
                "risk_level": "high",
                "days_ahead": 7,
                "confidence": 0.78,
                "model_version": "v1.2.0",
                "predicted_at": "2024-01-15T10:30:00Z",
                "risk_factors": [
                    "Increasing symptom severity trend",
                    "Elevated stress levels",
                    "Frequent trigger food consumption"
                ]
            }
        }


class RecommendationRequest(BaseModel):
    """Request schema for personalized recommendations."""
    symptoms: Optional[Dict[str, Any]] = Field(
        None,
        description="Current symptoms data. If not provided, uses most recent symptom log."
    )
    focus_area: Optional[str] = Field(
        None,
        description="Specific area to focus recommendations on (diet, lifestyle, both)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "symptoms": {
                    "abdominal_pain": 2,
                    "bloating": 3,
                    "stress_level": 6
                },
                "focus_area": "diet"
            }
        }


class DietRecommendation(BaseModel):
    """Schema for diet recommendation."""
    category: str = Field(..., description="Recommendation category")
    recommendation: str = Field(..., description="Specific recommendation")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    rationale: str = Field(..., description="Explanation for the recommendation")


class LifestyleRecommendation(BaseModel):
    """Schema for lifestyle recommendation."""
    category: str = Field(..., description="Recommendation category")
    recommendation: str = Field(..., description="Specific recommendation")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    rationale: str = Field(..., description="Explanation for the recommendation")


class RecommendationResponse(BaseModel):
    """Response schema for personalized recommendations."""
    diet_recommendations: List[DietRecommendation] = Field(
        ..., description="Personalized diet recommendations"
    )
    lifestyle_recommendations: List[LifestyleRecommendation] = Field(
        ..., description="Personalized lifestyle recommendations"
    )
    diet_score: float = Field(..., description="Current diet adherence score (0-10)")
    lifestyle_score: float = Field(..., description="Current lifestyle score (0-10)")
    model_version: str = Field(..., description="Version of the model used")
    generated_at: datetime = Field(..., description="Timestamp of generation")
    
    class Config:
        schema_extra = {
            "example": {
                "diet_recommendations": [
                    {
                        "category": "FODMAP Management",
                        "recommendation": "Reduce high-FODMAP foods like onions and garlic",
                        "priority": "high",
                        "rationale": "Your recent bloating symptoms correlate with high-FODMAP intake"
                    },
                    {
                        "category": "Fiber Intake",
                        "recommendation": "Gradually increase soluble fiber intake",
                        "priority": "medium",
                        "rationale": "Soluble fiber can help regulate bowel movements"
                    }
                ],
                "lifestyle_recommendations": [
                    {
                        "category": "Stress Management",
                        "recommendation": "Practice daily meditation or deep breathing exercises",
                        "priority": "high",
                        "rationale": "High stress levels are strongly correlated with your symptom flares"
                    },
                    {
                        "category": "Sleep Hygiene",
                        "recommendation": "Maintain consistent sleep schedule with 7-8 hours nightly",
                        "priority": "medium",
                        "rationale": "Poor sleep quality is affecting your symptom severity"
                    }
                ],
                "diet_score": 6.5,
                "lifestyle_score": 4.2,
                "model_version": "v1.2.0",
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


class ModelInfoResponse(BaseModel):
    """Response schema for model information."""
    models_loaded: Dict[str, bool] = Field(..., description="Status of loaded models")
    model_versions: Dict[str, str] = Field(..., description="Version of each model")
    last_updated: Dict[str, datetime] = Field(..., description="Last update time for each model")
    fallback_active: Dict[str, bool] = Field(..., description="Whether fallback models are active")
    
    class Config:
        schema_extra = {
            "example": {
                "models_loaded": {
                    "severity_model": True,
                    "flareup_model": True,
                    "recommendation_model": True
                },
                "model_versions": {
                    "severity_model": "v1.2.0",
                    "flareup_model": "v1.1.5",
                    "recommendation_model": "v1.0.8"
                },
                "last_updated": {
                    "severity_model": "2024-01-10T15:30:00Z",
                    "flareup_model": "2024-01-08T12:00:00Z",
                    "recommendation_model": "2024-01-05T09:15:00Z"
                },
                "fallback_active": {
                    "severity_model": False,
                    "flareup_model": False,
                    "recommendation_model": True
                }
            }
        }


class PredictionHistoryRequest(BaseModel):
    """Request schema for prediction history."""
    prediction_type: Optional[str] = Field(
        None,
        description="Filter by prediction type (severity, flareup, recommendations)"
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
    """Schema for prediction history item."""
    id: str = Field(..., description="Prediction ID")
    prediction_type: str = Field(..., description="Type of prediction")
    model_version: str = Field(..., description="Model version used")
    confidence_score: float = Field(..., description="Confidence score")
    predicted_at: datetime = Field(..., description="Prediction timestamp")
    prediction_summary: Dict[str, Any] = Field(..., description="Summary of prediction results")


class PredictionHistoryResponse(BaseModel):
    """Response schema for prediction history."""
    predictions: List[PredictionHistoryItem] = Field(..., description="List of predictions")
    total_count: int = Field(..., description="Total number of predictions available")
    page_info: Dict[str, Any] = Field(..., description="Pagination information")
    
    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "id": "pred_123456",
                        "prediction_type": "severity",
                        "model_version": "v1.2.0",
                        "confidence_score": 0.85,
                        "predicted_at": "2024-01-15T10:30:00Z",
                        "prediction_summary": {
                            "severity_score": 6.2,
                            "severity_level": "moderate"
                        }
                    }
                ],
                "total_count": 45,
                "page_info": {
                    "has_more": True,
                    "next_cursor": "cursor_abc123"
                }
            }
        }