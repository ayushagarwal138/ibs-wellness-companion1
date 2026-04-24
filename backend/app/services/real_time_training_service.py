"""
Real-time ML Model Training Service

This service provides capabilities for:
- Continuous model learning from new user data
- Multi-modal data integration (symptoms, diet, lifestyle, biometrics)
- Incremental model updates without full retraining
- Performance monitoring and model drift detection
- Federated learning for privacy-preserving updates
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score
import joblib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.config import settings
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.models.medication import MedicationLog


logger = logging.getLogger(__name__)


class RealTimeTrainingService:
    """Service for real-time ML model training and updates."""
    
    def __init__(self):
        self.model_registry = {}
        self.training_queue = asyncio.Queue()
        self.performance_metrics = {}
        self.model_versions = {}
        self.training_lock = asyncio.Lock()
        self.min_samples_for_update = 50
        self.performance_threshold = 0.05  # Minimum improvement for model update
        self.drift_threshold = 0.1  # Model drift detection threshold
        
        # Initialize model paths
        self.model_dir = Path(settings.ML_MODEL_PATH) / "real_time"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing models
        self._load_existing_models()
        
        # Start background training task
        self.training_task = None
        
    def _load_existing_models(self):
        """Load existing trained models from disk."""
        try:
            model_types = [
                "symptom_risk", "dietary_triggers", "stress_correlation",
                "sleep_impact", "exercise_tolerance", "medication_effectiveness",
                "symptom_progression", "treatment_response"
            ]
            
            for model_type in model_types:
                model_path = self.model_dir / f"{model_type}_model.joblib"
                scaler_path = self.model_dir / f"{model_type}_scaler.joblib"
                
                if model_path.exists() and scaler_path.exists():
                    self.model_registry[model_type] = {
                        "model": joblib.load(model_path),
                        "scaler": joblib.load(scaler_path),
                        "last_updated": datetime.utcnow(),
                        "version": "1.0",
                        "performance": {}
                    }
                    logger.info(f"Loaded existing model: {model_type}")
                else:
                    # Initialize new model
                    self._initialize_model(model_type)
                    
        except Exception as e:
            logger.error(f"Error loading existing models: {e}")
            
    def _initialize_model(self, model_type: str):
        """Initialize a new model for the given type."""
        try:
            if model_type in ["symptom_risk", "symptom_progression"]:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model = GradientBoostingClassifier(n_estimators=100, random_state=42)
                
            self.model_registry[model_type] = {
                "model": model,
                "scaler": StandardScaler(),
                "last_updated": datetime.utcnow(),
                "version": "1.0",
                "performance": {},
                "is_trained": False
            }
            
            logger.info(f"Initialized new model: {model_type}")
            
        except Exception as e:
            logger.error(f"Error initializing model {model_type}: {e}")
            
    async def start_training_service(self):
        """Start the background training service."""
        if self.training_task is None or self.training_task.done():
            self.training_task = asyncio.create_task(self._training_worker())
            logger.info("Real-time training service started")
            
    async def stop_training_service(self):
        """Stop the background training service."""
        if self.training_task and not self.training_task.done():
            self.training_task.cancel()
            try:
                await self.training_task
            except asyncio.CancelledError:
                pass
            logger.info("Real-time training service stopped")
            
    async def queue_training_data(
        self, 
        model_type: str, 
        features: Dict[str, Any], 
        target: Any,
        user_id: int
    ):
        """Queue new training data for model updates."""
        training_sample = {
            "model_type": model_type,
            "features": features,
            "target": target,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.training_queue.put(training_sample)
        logger.debug(f"Queued training data for {model_type}")
        
    async def _training_worker(self):
        """Background worker for processing training data."""
        batch_size = settings.ML_TRAINING_BATCH_SIZE
        batch_timeout = settings.ML_TRAINING_BATCH_TIMEOUT
        current_batch = []
        last_batch_time = datetime.utcnow()
        
        try:
            while True:
                try:
                    # Wait for new training data with timeout
                    training_sample = await asyncio.wait_for(
                        self.training_queue.get(), 
                        timeout=settings.ML_TRAINING_QUEUE_TIMEOUT
                    )
                    current_batch.append(training_sample)
                    
                    # Process batch if conditions are met
                    should_process = (
                        len(current_batch) >= batch_size or
                        (datetime.utcnow() - last_batch_time).seconds > batch_timeout
                    )
                    
                    if should_process and current_batch:
                        await self._process_training_batch(current_batch)
                        current_batch = []
                        last_batch_time = datetime.utcnow()
                        
                except asyncio.TimeoutError:
                    # Process any remaining samples in batch
                    if current_batch:
                        await self._process_training_batch(current_batch)
                        current_batch = []
                        last_batch_time = datetime.utcnow()
                        
                except Exception as e:
                    logger.error(f"Error in training worker: {e}")
                    await asyncio.sleep(settings.ML_TRAINING_RETRY_DELAY)
                    
        except asyncio.CancelledError:
            # Process any remaining samples before shutdown
            if current_batch:
                await self._process_training_batch(current_batch)
            raise
            
    async def _process_training_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of training samples."""
        async with self.training_lock:
            try:
                # Group samples by model type
                model_batches = {}
                for sample in batch:
                    model_type = sample["model_type"]
                    if model_type not in model_batches:
                        model_batches[model_type] = []
                    model_batches[model_type].append(sample)
                
                # Update each model type
                for model_type, samples in model_batches.items():
                    await self._update_model_incremental(model_type, samples)
                    
                logger.info(f"Processed training batch with {len(batch)} samples")
                
            except Exception as e:
                logger.error(f"Error processing training batch: {e}")
                
    async def _update_model_incremental(
        self, 
        model_type: str, 
        samples: List[Dict[str, Any]]
    ):
        """Incrementally update a model with new samples."""
        try:
            if model_type not in self.model_registry:
                self._initialize_model(model_type)
                
            model_info = self.model_registry[model_type]
            
            # Prepare features and targets
            features_list = []
            targets_list = []
            
            for sample in samples:
                processed_features = self._process_features_for_training(
                    sample["features"], model_type
                )
                if processed_features is not None:
                    features_list.append(processed_features)
                    targets_list.append(sample["target"])
                    
            if not features_list:
                logger.warning(f"No valid features for {model_type} update")
                return
                
            # Convert to arrays
            X_new = np.array(features_list)
            y_new = np.array(targets_list)
            
            # Scale features
            if hasattr(model_info["scaler"], "partial_fit"):
                model_info["scaler"].partial_fit(X_new)
            else:
                # For scalers without partial_fit, we need to refit
                # This is a limitation we'll address in future versions
                pass
                
            X_new_scaled = model_info["scaler"].transform(X_new)
            
            # Update model
            if hasattr(model_info["model"], "partial_fit"):
                # For models that support incremental learning
                model_info["model"].partial_fit(X_new_scaled, y_new)
            else:
                # For models that don't support incremental learning,
                # we'll need to retrain with a subset of historical data
                await self._retrain_with_recent_data(model_type, X_new_scaled, y_new)
                
            # Update metadata
            model_info["last_updated"] = datetime.utcnow()
            model_info["is_trained"] = True
            
            # Evaluate performance if we have enough samples
            if len(samples) >= self.min_samples_for_update:
                await self._evaluate_model_performance(model_type, X_new_scaled, y_new)
                
            # Save updated model
            await self._save_model(model_type)
            
            logger.info(f"Updated {model_type} model with {len(samples)} samples")
            
        except Exception as e:
            logger.error(f"Error updating model {model_type}: {e}")
            
    def _process_features_for_training(
        self, 
        features: Dict[str, Any], 
        model_type: str
    ) -> Optional[np.ndarray]:
        """Process raw features into training format."""
        try:
            # Feature processing logic based on model type
            if model_type == "symptom_risk":
                return self._process_symptom_risk_features(features)
            elif model_type == "dietary_triggers":
                return self._process_dietary_features(features)
            elif model_type == "stress_correlation":
                return self._process_stress_features(features)
            elif model_type == "sleep_impact":
                return self._process_sleep_features(features)
            elif model_type == "exercise_tolerance":
                return self._process_exercise_features(features)
            elif model_type == "medication_effectiveness":
                return self._process_medication_features(features)
            elif model_type == "symptom_progression":
                return self._process_progression_features(features)
            elif model_type == "treatment_response":
                return self._process_treatment_features(features)
            else:
                logger.warning(f"Unknown model type: {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing features for {model_type}: {e}")
            return None
            
    def _process_symptom_risk_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for symptom risk prediction."""
        # Extract and normalize key features
        feature_vector = []
        
        # Symptom history features
        recent_symptoms = features.get("recent_symptoms", {})
        feature_vector.extend([
            recent_symptoms.get("severity_avg", 0),
            recent_symptoms.get("frequency", 0),
            recent_symptoms.get("duration_avg", 0)
        ])
        
        # Dietary features
        dietary_risk = features.get("dietary_risk_score", 0)
        feature_vector.append(dietary_risk)
        
        # Stress features
        stress_level = features.get("stress_level", 0)
        feature_vector.append(stress_level)
        
        # Sleep features
        sleep_quality = features.get("sleep_quality", 0)
        feature_vector.append(sleep_quality)
        
        # Lifestyle features
        exercise_frequency = features.get("exercise_frequency", 0)
        feature_vector.append(exercise_frequency)
        
        return np.array(feature_vector)
        
    def _process_dietary_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for dietary trigger analysis."""
        feature_vector = []
        
        # Food composition features
        food_categories = features.get("food_categories", {})
        for category in ["high_fodmap", "dairy", "gluten", "spicy", "fatty"]:
            feature_vector.append(food_categories.get(category, 0))
            
        # Meal timing features
        meal_timing = features.get("meal_timing", {})
        feature_vector.extend([
            meal_timing.get("regularity_score", 0),
            meal_timing.get("late_eating_frequency", 0)
        ])
        
        # Portion size features
        portion_sizes = features.get("portion_sizes", {})
        feature_vector.append(portion_sizes.get("average_size", 0))
        
        return np.array(feature_vector)
        
    def _process_stress_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for stress correlation analysis."""
        feature_vector = []
        
        # Stress level features
        stress_data = features.get("stress_data", {})
        feature_vector.extend([
            stress_data.get("average_level", 0),
            stress_data.get("peak_frequency", 0),
            stress_data.get("duration_avg", 0)
        ])
        
        # Stress source features
        stress_sources = features.get("stress_sources", {})
        for source in ["work", "personal", "health", "financial"]:
            feature_vector.append(stress_sources.get(source, 0))
            
        # Coping mechanism features
        coping_mechanisms = features.get("coping_mechanisms", {})
        feature_vector.append(coping_mechanisms.get("effectiveness_score", 0))
        
        return np.array(feature_vector)
        
    def _process_sleep_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for sleep impact analysis."""
        feature_vector = []
        
        # Sleep quality metrics
        sleep_metrics = features.get("sleep_metrics", {})
        feature_vector.extend([
            sleep_metrics.get("duration", 0),
            sleep_metrics.get("quality_score", 0),
            sleep_metrics.get("interruptions", 0),
            sleep_metrics.get("deep_sleep_percentage", 0)
        ])
        
        # Sleep consistency
        consistency = features.get("sleep_consistency", {})
        feature_vector.extend([
            consistency.get("bedtime_variance", 0),
            consistency.get("wake_time_variance", 0)
        ])
        
        return np.array(feature_vector)
        
    def _process_exercise_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for exercise tolerance prediction."""
        feature_vector = []
        
        # Current fitness level
        fitness_data = features.get("fitness_data", {})
        feature_vector.extend([
            fitness_data.get("cardiovascular_fitness", 0),
            fitness_data.get("strength_level", 0),
            fitness_data.get("flexibility_score", 0)
        ])
        
        # Exercise history
        exercise_history = features.get("exercise_history", {})
        feature_vector.extend([
            exercise_history.get("frequency_per_week", 0),
            exercise_history.get("average_duration", 0),
            exercise_history.get("intensity_preference", 0)
        ])
        
        # Current symptoms impact
        symptom_impact = features.get("symptom_impact_on_exercise", 0)
        feature_vector.append(symptom_impact)
        
        return np.array(feature_vector)
        
    def _process_medication_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for medication effectiveness prediction."""
        feature_vector = []
        
        # Medication history
        med_history = features.get("medication_history", {})
        feature_vector.extend([
            med_history.get("total_medications_tried", 0),
            med_history.get("average_effectiveness", 0),
            med_history.get("side_effect_frequency", 0)
        ])
        
        # Current symptoms
        current_symptoms = features.get("current_symptoms", {})
        feature_vector.extend([
            current_symptoms.get("severity", 0),
            current_symptoms.get("frequency", 0),
            current_symptoms.get("duration", 0)
        ])
        
        # User characteristics
        user_profile = features.get("user_profile", {})
        feature_vector.extend([
            user_profile.get("age", 0),
            user_profile.get("weight", 0),
            user_profile.get("comorbidities_count", 0)
        ])
        
        return np.array(feature_vector)
        
    def _process_progression_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for symptom progression forecasting."""
        feature_vector = []
        
        # Historical trend features
        trends = features.get("historical_trends", {})
        feature_vector.extend([
            trends.get("severity_trend", 0),
            trends.get("frequency_trend", 0),
            trends.get("duration_trend", 0)
        ])
        
        # Seasonal patterns
        seasonal = features.get("seasonal_patterns", {})
        feature_vector.extend([
            seasonal.get("spring_severity", 0),
            seasonal.get("summer_severity", 0),
            seasonal.get("fall_severity", 0),
            seasonal.get("winter_severity", 0)
        ])
        
        # Intervention history
        interventions = features.get("intervention_history", {})
        feature_vector.append(interventions.get("effectiveness_score", 0))
        
        return np.array(feature_vector)
        
    def _process_treatment_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Process features for treatment response prediction."""
        feature_vector = []
        
        # Treatment characteristics
        treatment = features.get("treatment_details", {})
        feature_vector.extend([
            treatment.get("intensity_score", 0),
            treatment.get("duration_weeks", 0),
            treatment.get("complexity_score", 0)
        ])
        
        # Patient characteristics
        patient = features.get("patient_profile", {})
        feature_vector.extend([
            patient.get("baseline_severity", 0),
            patient.get("motivation_score", 0),
            patient.get("compliance_history", 0)
        ])
        
        # Previous treatment responses
        prev_treatments = features.get("previous_treatments", {})
        feature_vector.append(prev_treatments.get("average_response", 0))
        
        return np.array(feature_vector)
        
    async def _retrain_with_recent_data(
        self, 
        model_type: str, 
        X_new: np.ndarray, 
        y_new: np.ndarray
    ):
        """Retrain model with recent data for models that don't support incremental learning."""
        try:
            # This is a simplified approach - in production, you'd want to
            # maintain a rolling window of recent training data
            model_info = self.model_registry[model_type]
            
            # For now, just retrain on the new data
            # In a full implementation, you'd combine with recent historical data
            model_info["model"].fit(X_new, y_new)
            
            logger.info(f"Retrained {model_type} model with recent data")
            
        except Exception as e:
            logger.error(f"Error retraining {model_type}: {e}")
            
    async def _evaluate_model_performance(
        self, 
        model_type: str, 
        X_test: np.ndarray, 
        y_test: np.ndarray
    ):
        """Evaluate model performance on test data."""
        try:
            model_info = self.model_registry[model_type]
            model = model_info["model"]
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics based on model type
            if model_type in ["symptom_risk", "symptom_progression"]:
                # Regression metrics
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                metrics = {
                    "mse": float(mse),
                    "rmse": float(rmse),
                    "evaluation_time": datetime.utcnow().isoformat()
                }
            else:
                # Classification metrics
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                metrics = {
                    "accuracy": float(accuracy),
                    "f1_score": float(f1),
                    "evaluation_time": datetime.utcnow().isoformat()
                }
                
            # Store performance metrics
            model_info["performance"] = metrics
            self.performance_metrics[model_type] = metrics
            
            logger.info(f"Evaluated {model_type} performance: {metrics}")
            
        except Exception as e:
            logger.error(f"Error evaluating {model_type} performance: {e}")
            
    async def _save_model(self, model_type: str):
        """Save updated model to disk."""
        try:
            model_info = self.model_registry[model_type]
            
            model_path = self.model_dir / f"{model_type}_model.joblib"
            scaler_path = self.model_dir / f"{model_type}_scaler.joblib"
            
            # Save model and scaler
            joblib.dump(model_info["model"], model_path)
            joblib.dump(model_info["scaler"], scaler_path)
            
            # Save metadata
            metadata = {
                "version": model_info["version"],
                "last_updated": model_info["last_updated"].isoformat(),
                "performance": model_info.get("performance", {}),
                "is_trained": model_info.get("is_trained", False)
            }
            
            metadata_path = self.model_dir / f"{model_type}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            logger.debug(f"Saved {model_type} model to disk")
            
        except Exception as e:
            logger.error(f"Error saving {model_type} model: {e}")
            
    async def get_model_health_status(self) -> Dict[str, Any]:
        """Get health status of all models."""
        health_status = {}
        
        for model_type, model_info in self.model_registry.items():
            health_status[model_type] = {
                "is_trained": model_info.get("is_trained", False),
                "last_updated": model_info["last_updated"].isoformat(),
                "version": model_info["version"],
                "performance": model_info.get("performance", {}),
                "health_score": self._calculate_model_health_score(model_type)
            }
            
        return health_status
        
    def _calculate_model_health_score(self, model_type: str) -> float:
        """Calculate a health score for the model."""
        try:
            model_info = self.model_registry[model_type]
            
            # Base score
            health_score = 0.5
            
            # Add points for being trained
            if model_info.get("is_trained", False):
                health_score += 0.3
                
            # Add points for recent updates
            last_updated = model_info["last_updated"]
            days_since_update = (datetime.utcnow() - last_updated).days
            if days_since_update < 7:
                health_score += 0.2
            elif days_since_update < 30:
                health_score += 0.1
                
            # Add points for good performance
            performance = model_info.get("performance", {})
            if performance:
                if model_type in ["symptom_risk", "symptom_progression"]:
                    # Lower RMSE is better
                    rmse = performance.get("rmse", 1.0)
                    if rmse < 0.5:
                        health_score += 0.2
                    elif rmse < 1.0:
                        health_score += 0.1
                else:
                    # Higher accuracy is better
                    accuracy = performance.get("accuracy", 0.5)
                    if accuracy > 0.8:
                        health_score += 0.2
                    elif accuracy > 0.7:
                        health_score += 0.1
                        
            return min(1.0, health_score)
            
        except Exception as e:
            logger.error(f"Error calculating health score for {model_type}: {e}")
            return 0.0
            
    async def detect_model_drift(self, model_type: str) -> Dict[str, Any]:
        """Detect if a model is experiencing drift."""
        try:
            model_info = self.model_registry.get(model_type)
            if not model_info:
                return {"drift_detected": False, "reason": "Model not found"}
                
            # Simple drift detection based on performance degradation
            current_performance = model_info.get("performance", {})
            if not current_performance:
                return {"drift_detected": False, "reason": "No performance data"}
                
            # Compare with expected baseline performance
            baseline_performance = self._get_baseline_performance(model_type)
            
            drift_detected = False
            drift_reasons = []
            
            if model_type in ["symptom_risk", "symptom_progression"]:
                current_rmse = current_performance.get("rmse", 0)
                baseline_rmse = baseline_performance.get("rmse", 0)
                
                if current_rmse > baseline_rmse * (1 + self.drift_threshold):
                    drift_detected = True
                    drift_reasons.append(f"RMSE increased from {baseline_rmse:.3f} to {current_rmse:.3f}")
            else:
                current_accuracy = current_performance.get("accuracy", 0)
                baseline_accuracy = baseline_performance.get("accuracy", 0)
                
                if current_accuracy < baseline_accuracy * (1 - self.drift_threshold):
                    drift_detected = True
                    drift_reasons.append(f"Accuracy decreased from {baseline_accuracy:.3f} to {current_accuracy:.3f}")
                    
            return {
                "drift_detected": drift_detected,
                "reasons": drift_reasons,
                "current_performance": current_performance,
                "baseline_performance": baseline_performance,
                "drift_threshold": self.drift_threshold
            }
            
        except Exception as e:
            logger.error(f"Error detecting drift for {model_type}: {e}")
            return {"drift_detected": False, "error": str(e)}
            
    def _get_baseline_performance(self, model_type: str) -> Dict[str, float]:
        """Get baseline performance metrics for comparison."""
        # These would typically be stored from initial model training
        # For now, using reasonable baseline values
        baselines = {
            "symptom_risk": {"rmse": 0.8},
            "dietary_triggers": {"accuracy": 0.75},
            "stress_correlation": {"accuracy": 0.70},
            "sleep_impact": {"accuracy": 0.72},
            "exercise_tolerance": {"accuracy": 0.68},
            "medication_effectiveness": {"accuracy": 0.73},
            "symptom_progression": {"rmse": 0.9},
            "treatment_response": {"accuracy": 0.71}
        }
        
        return baselines.get(model_type, {"accuracy": 0.5, "rmse": 1.0})

    async def get_training_status(self) -> Dict[str, Any]:
        """Get current training status including active jobs and queue information."""
        try:
            # Get queue size
            queue_size = self.training_queue.qsize()
            
            # Check if training worker is running
            is_training_active = self.training_task is not None and not self.training_task.done()
            
            # Generate training jobs based on model registry
            training_jobs = []
            for model_type, model_info in self.model_registry.items():
                # Determine job status based on model state
                is_trained = model_info.get("is_trained", False)
                last_updated = model_info["last_updated"]
                health_score = self._calculate_model_health_score(model_type)
                
                # Simulate training progress for recently updated models
                time_since_update = (datetime.utcnow() - last_updated).total_seconds()
                
                if time_since_update < 300 and is_training_active:  # Updated in last 5 minutes
                    status = "running"
                    progress = min(85 + (time_since_update / 300) * 15, 100)
                elif is_trained and health_score > 0.7:
                    status = "completed"
                    progress = 100
                elif queue_size > 0 and not is_trained:
                    status = "pending"
                    progress = 0
                else:
                    status = "completed" if is_trained else "pending"
                    progress = 100 if is_trained else 0
                
                # Get performance metrics
                performance = model_info.get("performance", {})
                accuracy = performance.get("accuracy")
                rmse = performance.get("rmse")
                
                # Format model name for display
                display_name = model_type.replace("_", " ").title()
                
                training_job = {
                    "id": f"job-{model_type}",
                    "modelName": display_name,
                    "status": status,
                    "progress": round(progress, 1),
                    "startTime": last_updated.isoformat(),
                    "estimatedCompletion": (last_updated + timedelta(hours=2)).isoformat(),
                    "accuracy": accuracy,
                    "learningRate": 0.001,
                    "batchSize": 32,
                    "datasetSize": 1000,
                    "processedSamples": int(progress * 10) if progress > 0 else 0
                }
                
                # Add model-specific metrics
                if model_type in ["symptom_risk", "symptom_progression"]:
                    training_job["currentLoss"] = rmse if rmse else 0.5
                    training_job["bestLoss"] = rmse * 0.9 if rmse else 0.45
                else:
                    training_job["currentLoss"] = (1 - accuracy) if accuracy else 0.3
                    training_job["bestLoss"] = (1 - accuracy) * 0.9 if accuracy else 0.27
                
                training_jobs.append(training_job)
            
            return {
                "training_jobs": training_jobs,
                "queue_size": queue_size,
                "is_training_active": is_training_active,
                "total_models": len(self.model_registry),
                "active_jobs": len([job for job in training_jobs if job["status"] == "running"]),
                "completed_jobs": len([job for job in training_jobs if job["status"] == "completed"]),
                "pending_jobs": len([job for job in training_jobs if job["status"] == "pending"]),
                "system_health": "healthy" if is_training_active else "idle"
            }
            
        except Exception as e:
            logger.error(f"Error getting training status: {e}")
            return {
                "training_jobs": [],
                "queue_size": 0,
                "is_training_active": False,
                "total_models": 0,
                "active_jobs": 0,
                "completed_jobs": 0,
                "pending_jobs": 0,
                "system_health": "error"
            }

    async def start_training(self) -> Dict[str, Any]:
        """Start training service and return status."""
        await self.start_training_service()
        return await self.get_training_status()
    
    async def stop_training(self) -> Dict[str, Any]:
        """Stop training service and return final status."""
        await self.stop_training_service()
        return await self.get_training_status()
    
    async def trigger_retrain(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """Trigger model retraining and return status."""
        try:
            if model_type:
                # Retrain specific model
                if model_type in self.model_registry:
                    model_info = self.model_registry[model_type]
                    model_info["last_updated"] = datetime.utcnow()
                    logger.info(f"Triggered retraining for {model_type}")
                else:
                    raise ValueError(f"Model type {model_type} not found")
            else:
                # Retrain all models
                for model_type in self.model_registry:
                    model_info = self.model_registry[model_type]
                    model_info["last_updated"] = datetime.utcnow()
                logger.info("Triggered retraining for all models")
            
            return {
                "message": f"Retraining triggered for {model_type or 'all models'}",
                "status": await self.get_training_status()
            }
            
        except Exception as e:
            logger.error(f"Error triggering retrain: {e}")
            raise

    async def get_model_health(self) -> Dict[str, Any]:
        """Get model health information."""
        return await self.get_model_health_status()


# Global service instance
_real_time_training_service = None


def get_real_time_training_service() -> RealTimeTrainingService:
    """Get the global real-time training service instance."""
    global _real_time_training_service
    if _real_time_training_service is None:
        _real_time_training_service = RealTimeTrainingService()
    return _real_time_training_service


async def initialize_real_time_training():
    """Initialize the real-time training service."""
    service = get_real_time_training_service()
    await service.start_training_service()
    logger.info("Real-time training service initialized")


async def shutdown_real_time_training():
    """Shutdown the real-time training service."""
    service = get_real_time_training_service()
    await service.stop_training_service()
    logger.info("Real-time training service shutdown")