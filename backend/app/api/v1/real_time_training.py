"""
Real-Time Training API

API endpoints for managing real-time model training, monitoring model performance,
and controlling the continuous learning system.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_doctor_or_admin_user
from app.models import User
from app.services.enhanced_recommendation_service import EnhancedRecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-Time Training"])

# Global service instance
enhanced_recommendation_service = None


async def get_enhanced_recommendation_service(
    db: AsyncSession = Depends(get_db),
) -> EnhancedRecommendationService:
    """Get enhanced recommendation service instance."""
    global enhanced_recommendation_service
    if enhanced_recommendation_service is None:
        from app.services.enhanced_recommendation_service import (
            create_enhanced_recommendation_service,
        )
        enhanced_recommendation_service = create_enhanced_recommendation_service(db)
    return enhanced_recommendation_service


@router.post("/training/start")
async def start_training(
    current_user: User = Depends(get_doctor_or_admin_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Start the real-time training service for continuous model learning.
    
    This endpoint initializes the real-time training system that continuously
    learns from new user data to improve prediction accuracy.
    """
    try:
        logger.info(f"Starting real-time training for user {current_user.id}")
        
        # Start the real-time training service
        result = await service.real_time_training.start_training()
        
        return {
            "status": "success",
            "message": "Real-time training started successfully",
            "training_status": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting real-time training: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start real-time training: {str(e)}"
        )


@router.post("/training/stop")
async def stop_training(
    current_user: User = Depends(get_doctor_or_admin_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Stop the real-time training service.
    
    This endpoint stops the continuous learning system and saves the current
    model state.
    """
    try:
        logger.info(f"Stopping real-time training for user {current_user.id}")
        
        # Stop the real-time training service
        result = await service.real_time_training.stop_training()
        
        return {
            "status": "success",
            "message": "Real-time training stopped successfully",
            "final_status": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping real-time training: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop real-time training: {str(e)}"
        )


@router.get("/training/status")
async def get_training_status(
    current_user: User = Depends(get_current_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Get the current status of the real-time training system.
    
    Returns information about training progress, model performance,
    and system health.
    """
    try:
        logger.info(f"Getting training status for user {current_user.id}")
        
        # Get training status
        status_info = await service.real_time_training.get_training_status()
        
        return {
            "status": "success",
            "data": status_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training status: {str(e)}"
        )


@router.get("/models/health")
async def get_model_health(
    current_user: User = Depends(get_current_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Get comprehensive model health information.
    
    Returns detailed information about model performance, drift detection,
    and overall system health.
    """
    try:
        logger.info(f"Getting model health for user {current_user.id}")
        
        # Get model health status
        health_info = await service.real_time_training.get_model_health()
        
        return {
            "status": "success",
            "data": health_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model health: {str(e)}"
        )


@router.post("/models/retrain")
async def trigger_model_retrain(
    model_type: Optional[str] = None,
    current_user: User = Depends(get_doctor_or_admin_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Trigger manual model retraining.
    
    Args:
        model_type: Specific model to retrain (optional, retrains all if not specified)
        
    This endpoint manually triggers model retraining with the latest data.
    """
    try:
        logger.info(f"Triggering model retrain for user {current_user.id}")
        
        # Trigger model retraining
        result = await service.real_time_training.trigger_retrain(model_type)
        
        return {
            "status": "success",
            "message": "Model retraining triggered successfully",
            "retrain_info": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering model retrain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger model retrain: {str(e)}"
        )


@router.get("/performance/metrics")
async def get_performance_metrics(
    model_type: Optional[str] = None,
    timeframe_hours: int = 24,
    current_user: User = Depends(get_current_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Get detailed performance metrics for ML models.
    
    Args:
        model_type: Specific model to analyze (optional)
        timeframe_hours: Time window for metrics (default: 24 hours)
        
    Returns comprehensive performance metrics and analytics.
    """
    try:
        logger.info(f"Getting performance metrics for user {current_user.id}")
        
        # Get performance metrics
        metrics = await service.ml_optimization.get_performance_metrics(
            model_type, timeframe_hours
        )
        
        return {
            "status": "success",
            "data": metrics,
            "timeframe_hours": timeframe_hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.post("/data/queue")
async def queue_training_data(
    prediction_type: str,
    training_data: Dict[str, Any],
    current_user: User = Depends(get_doctor_or_admin_user),
    service: EnhancedRecommendationService = Depends(
        get_enhanced_recommendation_service
    ),
):
    """
    Manually queue data for real-time training.
    
    Args:
        prediction_type: Type of prediction model to train
        training_data: Data to be used for training
        
    This endpoint allows manual queuing of training data for specific models.
    """
    try:
        logger.info(f"Queuing training data for user {current_user.id}")
        
        # Queue training data
        result = await service.real_time_training.queue_training_data(
            prediction_type, training_data
        )
        
        return {
            "status": "success",
            "message": "Training data queued successfully",
            "queue_info": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error queuing training data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue training data: {str(e)}"
        )