"""
Real-time ML Predictions API

This module provides real-time prediction endpoints for IBS management,
including streaming predictions, real-time data processing, and enhanced ML features.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.services.enhanced_recommendation_service import EnhancedRecommendationService
from app.services.ml_integration_service import MLIntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml/realtime", tags=["Real-time ML Predictions"])

# Initialize enhanced ML services - will be initialized on first use
enhanced_recommendation_service = None


def get_enhanced_recommendation_service(db: Session = Depends(get_db)) -> EnhancedRecommendationService:
    """Get or create the enhanced recommendation service instance."""
    global enhanced_recommendation_service
    if enhanced_recommendation_service is None:
        enhanced_recommendation_service = EnhancedRecommendationService(db)
    return enhanced_recommendation_service


class RealTimePredictionRequest(BaseModel):
    """Request model for real-time predictions."""
    symptoms: Dict[str, Any]
    include_trends: bool = True
    include_recommendations: bool = True
    stream_updates: bool = False


class PredictionUpdate(BaseModel):
    """Model for streaming prediction updates."""
    timestamp: datetime
    prediction_type: str
    data: Dict[str, Any]
    confidence: float
    processing_time_ms: float


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""
    user_ids: List[str]
    prediction_types: List[str] = ["severity", "flareup", "recommendations"]
    days_ahead: int = 7


@router.post("/predict/stream")
async def stream_predictions(
    request: RealTimePredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: EnhancedRecommendationService = Depends(get_enhanced_recommendation_service)
):
    """Stream real-time predictions as they are computed."""
    
    async def generate_predictions():
        """Generate streaming predictions."""
        try:
            start_time = datetime.utcnow()
            
            # Prepare user data
            user_data = await _prepare_enhanced_user_data(current_user, db, request.symptoms)
            
            # Stream severity prediction
            yield _format_stream_response(
                "severity_start",
                {"message": "Computing severity prediction..."},
                0.0,
                0
            )
            
            severity_start = datetime.utcnow()
            severity_prediction = service.predict_symptom_risk(user_data)
            severity_time = (datetime.utcnow() - severity_start).total_seconds() * 1000
            
            yield _format_stream_response(
                "severity_complete",
                severity_prediction,
                severity_prediction.get('confidence', 0.8),
                severity_time
            )
            
            # Stream flareup prediction if requested
            if request.include_trends:
                yield _format_stream_response(
                    "flareup_start",
                    {"message": "Computing flareup risk..."},
                    0.0,
                    0
                )
                
                flareup_start = datetime.utcnow()
                # Add recent trends for better prediction
                user_data['recent_symptoms'] = await _get_enhanced_symptom_trends(
                    current_user.id, db
                )
                flareup_prediction = ml_service.predict_flareup_risk(user_data, 7)
                flareup_time = (datetime.utcnow() - flareup_start).total_seconds() * 1000
                
                yield _format_stream_response(
                    "flareup_complete",
                    flareup_prediction,
                    flareup_prediction.get('confidence', 0.8),
                    flareup_time
                )
            
            # Stream recommendations if requested
            if request.include_recommendations:
                yield _format_stream_response(
                    "recommendations_start",
                    {"message": "Generating personalized recommendations..."},
                    0.0,
                    0
                )
                
                rec_start = datetime.utcnow()
                recommendations = ml_service.generate_recommendations(user_data)
                rec_time = (datetime.utcnow() - rec_start).total_seconds() * 1000
                
                yield _format_stream_response(
                    "recommendations_complete",
                    recommendations,
                    recommendations.get('confidence', 0.8),
                    rec_time
                )
            
            # Final summary
            total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            yield _format_stream_response(
                "prediction_complete",
                {
                    "message": "All predictions completed",
                    "total_processing_time_ms": total_time,
                    "user_id": current_user.id
                },
                1.0,
                total_time
            )
            
        except Exception as e:
            logger.error(f"Error in streaming predictions: {e}")
            yield _format_stream_response(
                "error",
                {"error": str(e), "message": "Prediction failed"},
                0.0,
                0
            )
    
    return StreamingResponse(
        generate_predictions(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache"}
    )


@router.post("/predict/enhanced")
async def enhanced_prediction(
    request: RealTimePredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced prediction with additional ML features and data processing."""
    try:
        start_time = datetime.utcnow()
        
        # Prepare enhanced user data with more features
        user_data = await _prepare_enhanced_user_data(current_user, db, request.symptoms)
        
        # Add temporal features
        user_data['temporal_features'] = await _extract_temporal_features(current_user.id, db)
        
        # Add environmental factors (mock data for now)
        user_data['environmental_factors'] = await _get_environmental_factors()
        
        # Run all predictions in parallel for better performance
        severity_task = asyncio.create_task(_async_severity_prediction(user_data))
        flareup_task = asyncio.create_task(_async_flareup_prediction(user_data))
        recommendations_task = asyncio.create_task(_async_recommendations(user_data))
        
        # Wait for all predictions to complete
        severity_result, flareup_result, recommendations_result = await asyncio.gather(
            severity_task, flareup_task, recommendations_task
        )
        
        # Combine results with enhanced insights
        combined_result = {
            "severity": severity_result,
            "flareup_risk": flareup_result,
            "recommendations": recommendations_result,
            "insights": await _generate_insights(severity_result, flareup_result, user_data),
            "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "timestamp": datetime.utcnow(),
            "user_id": current_user.id
        }
        
        # Store enhanced prediction in background
        background_tasks.add_task(
            _store_enhanced_prediction,
            db, current_user.id, combined_result, request.dict()
        )
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Error in enhanced prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating enhanced predictions"
        )


@router.post("/predict/batch")
async def batch_predictions(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process batch predictions for multiple users or scenarios."""
    try:
        # For now, limit to current user for security
        if len(request.user_ids) > 1 or request.user_ids[0] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Batch predictions limited to current user"
            )
        
        results = []
        
        for user_id in request.user_ids:
            if user_id != current_user.id:
                continue
                
            user_data = await _prepare_enhanced_user_data(current_user, db)
            
            batch_result = {
                "user_id": user_id,
                "predictions": {},
                "timestamp": datetime.utcnow()
            }
            
            # Run requested predictions
            for pred_type in request.prediction_types:
                if pred_type == "severity":
                    batch_result["predictions"]["severity"] = ml_service.predict_severity(user_data)
                elif pred_type == "flareup":
                    user_data['recent_symptoms'] = await _get_enhanced_symptom_trends(user_id, db)
                    batch_result["predictions"]["flareup"] = ml_service.predict_flareup_risk(
                        user_data, request.days_ahead
                    )
                elif pred_type == "recommendations":
                    batch_result["predictions"]["recommendations"] = ml_service.generate_recommendations(user_data)
            
            results.append(batch_result)
        
        # Store batch results in background
        background_tasks.add_task(_store_batch_results, db, results)
        
        return {
            "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "results": results,
            "processed_count": len(results),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error in batch predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing batch predictions"
        )


# Helper functions

async def _prepare_enhanced_user_data(
    user: User, 
    db: Session, 
    symptoms: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Prepare enhanced user data with additional features."""
    # Get recent symptom logs (last 30 days)
    recent_symptoms = db.query(SymptomLog).filter(
        SymptomLog.user_id == user.id,
        SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    # Get recent diet logs
    recent_diet = db.query(DietLog).filter(
        DietLog.user_id == user.id,
        DietLog.logged_at >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    return {
        'profile': {
            'age': getattr(user, 'age', 30),
            'gender': getattr(user, 'gender', 'unknown'),
            'bmi': getattr(user, 'bmi', 25.0),
            'years_since_diagnosis': getattr(user, 'years_since_diagnosis', 1),
            'user_id': user.id
        },
        'symptoms': symptoms or {},
        'recent_symptoms_count': len(recent_symptoms),
        'recent_diet_count': len(recent_diet),
        'symptom_history': [
            {
                'severity': symptom.severity.value if symptom.severity else 'mild',
                'logged_at': symptom.logged_at,
                'symptoms': symptom.symptoms or {}
            }
            for symptom in recent_symptoms[-10:]  # Last 10 entries
        ],
        'diet_history': [
            {
                'foods': diet.foods or [],
                'logged_at': diet.logged_at,
                'reactions': getattr(diet, 'reactions', [])
            }
            for diet in recent_diet[-10:]  # Last 10 entries
        ]
    }


async def _get_enhanced_symptom_trends(user_id: str, db: Session) -> Dict[str, Any]:
    """Get enhanced symptom trends with more detailed analysis."""
    # Get symptoms from last 14 days
    recent_symptoms = db.query(SymptomLog).filter(
        SymptomLog.user_id == user_id,
        SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=14)
    ).all()
    
    if not recent_symptoms:
        return {
            'avg_severity_7d': 0,
            'avg_severity_14d': 0,
            'symptom_frequency_7d': 0,
            'symptom_frequency_14d': 0,
            'trend_direction': 'stable',
            'worst_day_severity': 0
        }
    
    # Calculate trends
    last_7_days = [s for s in recent_symptoms if s.logged_at >= datetime.utcnow() - timedelta(days=7)]
    
    severity_map = {'mild': 1, 'moderate': 2, 'severe': 3}
    
    avg_severity_7d = sum(severity_map.get(s.severity.value if s.severity else 'mild', 1) for s in last_7_days) / max(len(last_7_days), 1)
    avg_severity_14d = sum(severity_map.get(s.severity.value if s.severity else 'mild', 1) for s in recent_symptoms) / len(recent_symptoms)
    
    return {
        'avg_severity_7d': avg_severity_7d,
        'avg_severity_14d': avg_severity_14d,
        'symptom_frequency_7d': len(last_7_days),
        'symptom_frequency_14d': len(recent_symptoms),
        'trend_direction': 'improving' if avg_severity_7d < avg_severity_14d else 'worsening' if avg_severity_7d > avg_severity_14d else 'stable',
        'worst_day_severity': max(severity_map.get(s.severity.value if s.severity else 'mild', 1) for s in recent_symptoms)
    }


async def _extract_temporal_features(user_id: str, db: Session) -> Dict[str, Any]:
    """Extract temporal features for enhanced predictions."""
    now = datetime.utcnow()
    
    return {
        'hour_of_day': now.hour,
        'day_of_week': now.weekday(),
        'is_weekend': now.weekday() >= 5,
        'is_morning': 6 <= now.hour < 12,
        'is_afternoon': 12 <= now.hour < 18,
        'is_evening': 18 <= now.hour < 22,
        'is_night': now.hour >= 22 or now.hour < 6,
        'days_since_epoch': (now - datetime(2024, 1, 1)).days
    }


async def _get_environmental_factors() -> Dict[str, Any]:
    """Get environmental factors (mock data for now)."""
    return {
        'weather_pressure': 1013.25,  # Standard atmospheric pressure
        'temperature': 22.0,  # Celsius
        'humidity': 50.0,  # Percentage
        'air_quality_index': 50,  # Good air quality
        'pollen_count': 'low',
        'season': 'spring'  # Could be calculated from date
    }


async def _async_severity_prediction(user_data: Dict[str, Any], service: EnhancedRecommendationService) -> Dict[str, Any]:
    """Async wrapper for severity prediction using enhanced service."""
    return service.predict_symptom_risk(user_data)


async def _async_flareup_prediction(user_data: Dict[str, Any], service: EnhancedRecommendationService) -> Dict[str, Any]:
    """Async wrapper for flareup prediction using enhanced service."""
    return service.predict_symptom_risk(user_data)


async def _async_recommendations(user_data: Dict[str, Any], service: EnhancedRecommendationService) -> Dict[str, Any]:
    """Async wrapper for recommendations using enhanced service."""
    # Need to create a mock user object for the enhanced service
    from app.models.user import User
    mock_user = User(id=user_data.get('user_id', ''))
    return service.generate_enhanced_recommendations(mock_user, user_data)


async def _generate_insights(
    severity_result: Dict[str, Any],
    flareup_result: Dict[str, Any],
    user_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate additional insights from prediction results."""
    insights = {
        'risk_assessment': 'low',
        'key_factors': [],
        'recommendations_priority': 'medium',
        'next_check_in': 'in_3_days'
    }
    
    # Assess overall risk
    severity_score = severity_result.get('severity_score', 0)
    flareup_score = flareup_result.get('risk_score', 0)
    
    if severity_score > 0.7 or flareup_score > 0.7:
        insights['risk_assessment'] = 'high'
        insights['recommendations_priority'] = 'high'
        insights['next_check_in'] = 'daily'
    elif severity_score > 0.4 or flareup_score > 0.4:
        insights['risk_assessment'] = 'medium'
        insights['recommendations_priority'] = 'medium'
        insights['next_check_in'] = 'in_2_days'
    
    # Identify key factors
    if severity_score > 0.5:
        insights['key_factors'].append('Current symptom severity is elevated')
    if flareup_score > 0.5:
        insights['key_factors'].append('Flareup risk is increased')
    
    # Add temporal insights
    temporal = user_data.get('temporal_features', {})
    if temporal.get('is_weekend'):
        insights['key_factors'].append('Weekend patterns may affect symptoms')
    if temporal.get('is_evening'):
        insights['key_factors'].append('Evening symptoms may indicate dietary triggers')
    
    return insights


def _format_stream_response(
    prediction_type: str,
    data: Dict[str, Any],
    confidence: float,
    processing_time_ms: float
) -> str:
    """Format streaming response as NDJSON."""
    response = PredictionUpdate(
        timestamp=datetime.utcnow(),
        prediction_type=prediction_type,
        data=data,
        confidence=confidence,
        processing_time_ms=processing_time_ms
    )
    return json.dumps(response.dict(), default=str) + "\n"


async def _store_enhanced_prediction(
    db: Session,
    user_id: str,
    prediction_data: Dict[str, Any],
    input_data: Dict[str, Any]
):
    """Store enhanced prediction results."""
    # Implementation would store in database
    logger.info(f"Stored enhanced prediction for user {user_id}")


async def _store_batch_results(db: Session, results: List[Dict[str, Any]]):
    """Store batch prediction results."""
    # Implementation would store in database
    logger.info(f"Stored batch results for {len(results)} predictions")