"""
ML Optimization Service for IBS Wellness Companion

This service provides:
1. Model performance optimization
2. Comprehensive error handling and fallback mechanisms
3. Data validation and preprocessing
4. Model monitoring and health checks
5. Caching for improved performance
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from functools import wraps
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.medication import MedicationLog
from app.models.diet import DietLog

logger = logging.getLogger(__name__)


class MLOptimizationService:
    """Service for optimizing ML model performance and handling errors."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.model_health_status = {
            "medication_effectiveness": True,
            "dietary_triggers": True,
            "stress_correlation": True,
            "sleep_quality": True,
            "exercise_tolerance": True,
            "symptom_progression": True,
            "treatment_response": True
        }
        self.performance_metrics = {}
        
    def performance_monitor(self, model_name: str):
        """Decorator to monitor model performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Update performance metrics
                    if model_name not in self.performance_metrics:
                        self.performance_metrics[model_name] = {
                            "total_calls": 0,
                            "total_time": 0,
                            "avg_time": 0,
                            "success_rate": 0,
                            "errors": 0
                        }
                    
                    metrics = self.performance_metrics[model_name]
                    metrics["total_calls"] += 1
                    metrics["total_time"] += execution_time
                    metrics["avg_time"] = metrics["total_time"] / metrics["total_calls"]
                    metrics["success_rate"] = (metrics["total_calls"] - metrics["errors"]) / metrics["total_calls"]
                    
                    logger.info(f"Model {model_name} executed in {execution_time:.3f}s")
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    if model_name in self.performance_metrics:
                        self.performance_metrics[model_name]["errors"] += 1
                    
                    logger.error(f"Model {model_name} failed after {execution_time:.3f}s: {str(e)}")
                    raise
                    
            return wrapper
        return decorator
    
    def validate_features(self, features: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Validate input features for ML models."""
        missing_fields = []
        
        for field in required_fields:
            if field not in features or features[field] is None:
                missing_fields.append(field)
        
        # Check for data quality issues
        quality_issues = []
        
        # Check for reasonable ranges
        if "age" in features:
            age = features.get("age", 0)
            if not isinstance(age, (int, float)) or age < 0 or age > 120:
                quality_issues.append("age_out_of_range")
        
        if "symptom_severity" in features:
            severity = features.get("symptom_severity", 0)
            if not isinstance(severity, (int, float)) or severity < 0 or severity > 10:
                quality_issues.append("severity_out_of_range")
        
        if "stress_level" in features:
            stress = features.get("stress_level", 0)
            if not isinstance(stress, (int, float)) or stress < 0 or stress > 10:
                quality_issues.append("stress_out_of_range")
        
        is_valid = len(missing_fields) == 0 and len(quality_issues) == 0
        all_issues = missing_fields + quality_issues
        
        return is_valid, all_issues
    
    def preprocess_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess and normalize features for ML models."""
        processed = features.copy()
        
        # Handle missing values with defaults
        defaults = {
            "age": 30,
            "symptom_severity": 5,
            "stress_level": 5,
            "sleep_quality": 5,
            "exercise_frequency": 3,
            "medication_adherence": 0.8
        }
        
        for key, default_value in defaults.items():
            if key not in processed or processed[key] is None:
                processed[key] = default_value
                logger.warning(f"Missing feature {key}, using default value {default_value}")
        
        # Normalize numerical features
        normalizations = {
            "age": (0, 100),
            "symptom_severity": (0, 10),
            "stress_level": (0, 10),
            "sleep_quality": (0, 10),
            "exercise_frequency": (0, 7)
        }
        
        for key, (min_val, max_val) in normalizations.items():
            if key in processed:
                value = processed[key]
                if isinstance(value, (int, float)):
                    # Clamp to valid range
                    processed[key] = max(min_val, min(max_val, value))
        
        return processed
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_data["result"]
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        return None
    
    def set_cached_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache result with timestamp."""
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        logger.info(f"Cached result for key: {cache_key}")
    
    def generate_cache_key(self, model_name: str, features: Dict[str, Any]) -> str:
        """Generate cache key from model name and features."""
        # Create a deterministic key from features
        feature_str = "_".join([f"{k}:{v}" for k, v in sorted(features.items())])
        return f"{model_name}_{hash(feature_str)}"
    
    async def safe_database_query(self, db: Session, query_func, *args, **kwargs) -> Optional[Any]:
        """Safely execute database queries with error handling."""
        try:
            return await asyncio.to_thread(query_func, *args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in database query: {str(e)}")
            return None
    
    def get_fallback_prediction(self, model_name: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Get structured error response when model fails."""
        logger.error(f"Model prediction failed for: {model_name}")
        
        # Model-specific error messages and guidance
        model_error_info = {
            "medication_effectiveness": {
                "error_message": (
                    "Medication effectiveness prediction is temporarily "
                    "unavailable. Please consult your healthcare provider "
                    "for personalized medication guidance."
                ),
                "user_guidance": (
                    "Continue taking prescribed medications as directed and "
                    "monitor your symptoms. Contact your healthcare provider "
                    "if you experience any concerning changes."
                )
            },
            "dietary_triggers": {
                "error_message": (
                    "Dietary trigger analysis is temporarily unavailable. "
                    "Please use general IBS dietary guidelines."
                ),
                "user_guidance": (
                    "Follow a low-FODMAP diet if recommended by your "
                    "healthcare provider, keep a food diary, and avoid "
                    "known trigger foods."
                )
            },
            "stress_correlation": {
                "error_message": (
                    "Stress correlation analysis is temporarily unavailable. "
                    "Please use general stress management techniques."
                ),
                "user_guidance": (
                    "Practice stress reduction techniques such as meditation, "
                    "deep breathing, or gentle exercise. Consider speaking "
                    "with a mental health professional if stress is severe."
                )
            },
            "sleep_quality": {
                "error_message": (
                    "Sleep quality analysis is temporarily unavailable. "
                    "Please follow general sleep hygiene practices."
                ),
                "user_guidance": (
                    "Maintain a regular sleep schedule, create a comfortable "
                    "sleep environment, and avoid screens before bedtime."
                )
            },
            "exercise_tolerance": {
                "error_message": (
                    "Exercise tolerance analysis is temporarily unavailable. "
                    "Please follow general exercise guidelines for IBS."
                ),
                "user_guidance": (
                    "Start with gentle activities like walking or yoga. "
                    "Listen to your body and avoid intense exercise during "
                    "flare-ups. Consult your healthcare provider for "
                    "personalized exercise recommendations."
                )
            },
            "symptom_progression": {
                "error_message": (
                    "Symptom progression analysis is temporarily unavailable. "
                    "Please monitor symptoms manually."
                ),
                "user_guidance": (
                    "Keep a detailed symptom diary and track patterns. "
                    "Contact your healthcare provider if symptoms worsen "
                    "or new symptoms develop."
                )
            },
            "treatment_response": {
                "error_message": (
                    "Treatment response prediction is temporarily unavailable. "
                    "Please follow your current treatment plan."
                ),
                "user_guidance": (
                    "Continue with your prescribed treatment plan and "
                    "monitor your response. Report any concerns or lack "
                    "of improvement to your healthcare provider."
                )
            }
        }
        
        # Get model-specific error info or use default
        error_info = model_error_info.get(model_name, {
            "error_message": (
                f"The {model_name} prediction service is temporarily "
                "unavailable. Please try again later or contact support."
            ),
            "user_guidance": (
                "Continue with your current IBS management plan and "
                "consult your healthcare provider for personalized guidance."
            )
        })
        
        return {
            "error": True,
            "error_message": error_info["error_message"],
            "user_guidance": error_info["user_guidance"],
            "status": "FAILED",
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "retry_suggested": True,
            "support_contact": "Please contact support if this issue persists"
        }
    
    def check_model_health(self, model_name: str) -> bool:
        """Check if a specific model is healthy."""
        if model_name in self.performance_metrics:
            metrics = self.performance_metrics[model_name]
            # Consider model unhealthy if error rate > 50% or avg time > 10s
            if metrics["success_rate"] < 0.5 or metrics["avg_time"] > 10.0:
                self.model_health_status[model_name] = False
                logger.warning(f"Model {model_name} marked as unhealthy")
                return False
        
        return self.model_health_status.get(model_name, True)
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        total_cache_entries = len(self.cache)
        cache_hit_rate = 0.0  # Would need to track hits/misses for accurate rate
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "model_health": self.model_health_status,
            "performance_metrics": self.performance_metrics,
            "cache_stats": {
                "total_entries": total_cache_entries,
                "hit_rate": cache_hit_rate,
                "ttl_seconds": self.cache_ttl
            },
            "system_status": "healthy" if all(self.model_health_status.values()) else "degraded"
        }
    
    def optimize_feature_selection(self, features: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """Optimize feature selection based on model requirements."""
        # Define important features for each model
        model_features = {
            "medication_effectiveness": [
                "age", "symptom_severity", "medication_history", "adherence_rate"
            ],
            "dietary_triggers": [
                "symptom_severity", "food_diary", "meal_timing", "portion_sizes"
            ],
            "stress_correlation": [
                "stress_level", "symptom_severity", "lifestyle_factors", "sleep_quality"
            ],
            "sleep_quality": [
                "sleep_duration", "sleep_quality", "symptom_severity", "stress_level"
            ],
            "exercise_tolerance": [
                "fitness_level", "exercise_history", "symptom_severity", "age"
            ],
            "symptom_progression": [
                "symptom_history", "age", "stress_level", "medication_adherence"
            ],
            "treatment_response": [
                "medication_history", "age", "symptom_severity", "comorbidities"
            ]
        }
        
        important_features = model_features.get(model_name, list(features.keys()))
        
        # Select only important features and add derived features
        optimized = {}
        for feature in important_features:
            if feature in features:
                optimized[feature] = features[feature]
        
        # Add derived features
        if "age" in optimized and "symptom_severity" in optimized:
            optimized["age_severity_interaction"] = optimized["age"] * optimized["symptom_severity"] / 100
        
        if "stress_level" in optimized and "sleep_quality" in optimized:
            optimized["stress_sleep_ratio"] = optimized["stress_level"] / max(optimized["sleep_quality"], 1)
        
        return optimized


# Global instance
ml_optimization_service = MLOptimizationService()


def get_ml_optimization_service() -> MLOptimizationService:
    """Get the ML optimization service instance."""
    return ml_optimization_service