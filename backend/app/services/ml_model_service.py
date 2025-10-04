"""
ML Model Service

Service for loading, managing, and using trained ML models for IBS predictions.
This service handles model loading, feature preparation, and predictions.
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import traceback
from datetime import datetime
from enum import Enum

import joblib

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Enum for model status tracking."""
    LOADED = "loaded"
    FAILED = "failed"
    FALLBACK = "fallback"
    NOT_FOUND = "not_found"


class MLModelError(Exception):
    """Custom exception for ML model errors."""
    pass


class MLModelService:
    """Service for managing and using trained ML models."""

    def __init__(self):
        self.models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
        self.checkpoints_path = self.models_path / "checkpoints"
        self.models = {}
        self.model_metadata = {}
        self.model_status = {}
        self.error_counts = {}
        self.last_errors = {}
        self._load_latest_models()

    def _log_model_error(
        self, model_name: str, error: Exception, context: str = ""
    ):
        """Log model errors with detailed context."""
        error_msg = f"Model '{model_name}' error in {context}: {str(error)}"
        logger.error(error_msg)
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        # Track error counts
        if model_name not in self.error_counts:
            self.error_counts[model_name] = 0
        self.error_counts[model_name] += 1
        
        # Store last error for diagnostics
        self.last_errors[model_name] = {
            "error": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }

    def _validate_input_data(
        self, user_data: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """Validate input data has required fields."""
        try:
            if not isinstance(user_data, dict):
                raise MLModelError("Input data must be a dictionary")
            
            missing_fields = [
                field for field in required_fields if field not in user_data
            ]
            if missing_fields:
                raise MLModelError(
                    f"Missing required fields: {missing_fields}"
                )
            
            return True
        except Exception as e:
            logger.warning(f"Input validation failed: {e}")
            return False

    def _load_latest_models(self):
        """Load the latest trained models from checkpoints directory."""
        try:
            logger.info("Starting model loading process...")
            
            # Check for models directly in checkpoints directory (new format)
            direct_models = [
                "severity_classifier.pkl",
                "flareup_predictor.pkl", 
                "recommendation_engine.pkl",
                "feature_scaler.pkl"
            ]
            
            all_exist = all((self.checkpoints_path / model).exists() for model in direct_models)
            
            if all_exist:
                logger.info("Loading models from checkpoints directory")
                self._load_direct_models()
                
                # Load metadata if available
                metadata_path = self.checkpoints_path / "model_metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r") as f:
                            self.model_metadata = json.load(f)
                        logger.info("Model metadata loaded successfully")
                    except Exception as e:
                        self._log_model_error("metadata", e, "loading metadata")
                        self.model_metadata = {}
                else:
                    logger.warning("No model metadata found")
                    self.model_metadata = {}
            else:
                logger.warning(
                    "Not all direct models found, checking for checkpoint "
                    "subdirectories"
                )
                # Fallback to checkpoint subdirectories
                latest_checkpoint = self._get_latest_checkpoint()
                if latest_checkpoint:
                    checkpoint_path = self.checkpoints_path / latest_checkpoint
                    self._load_severity_classifier(checkpoint_path)
                    self._load_flareup_predictor(checkpoint_path)
                    self._load_recommendation_engine(checkpoint_path)
                else:
                    logger.warning(
                        "No checkpoints found, initializing fallback models"
                    )
                    self._initialize_fallback_models()
                    
        except Exception as e:
            self._log_model_error("system", e, "model loading initialization")
            logger.error("Failed to load models, initializing fallback models")
            self._initialize_fallback_models()

    def _load_direct_models(self):
        """Load models directly from checkpoints directory with error handling."""
        model_files = {
            "severity_classifier": "severity_classifier.pkl",
            "flareup_predictor": "flareup_predictor.pkl",
            "recommendation_engine": "recommendation_engine.pkl",
            "feature_scaler": "feature_scaler.pkl"
        }
        
        for model_name, filename in model_files.items():
            try:
                model_path = self.checkpoints_path / filename
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
                    self.model_status[model_name] = ModelStatus.LOADED
                    logger.info(f"Successfully loaded {model_name} from {filename}")
                else:
                    self.model_status[model_name] = ModelStatus.NOT_FOUND
                    logger.warning(f"Model file not found: {filename}")
                    
            except Exception as e:
                self._log_model_error(model_name, e, f"loading from {filename}")
                self.model_status[model_name] = ModelStatus.FAILED
                
        # If critical models failed to load, initialize fallbacks
        critical_models = [
            "severity_classifier", "flareup_predictor", "recommendation_engine"
        ]
        failed_critical = [
            m for m in critical_models 
            if self.model_status.get(m) != ModelStatus.LOADED
        ]
        
        if failed_critical:
            logger.warning(
                f"Critical models failed to load: {failed_critical}"
            )
            self._initialize_fallback_models()

    def _get_latest_checkpoint(self) -> Optional[str]:
        """Get the name of the latest checkpoint directory."""
        if not self.checkpoints_path.exists():
            return None

        # Look for 'latest' symlink first
        latest_link = self.checkpoints_path / "latest"
        if latest_link.exists() and latest_link.is_symlink():
            return latest_link.readlink().name

        # Otherwise, find the most recent directory
        checkpoint_dirs = [
            d
            for d in self.checkpoints_path.iterdir()
            if d.is_dir() and d.name.startswith("models_")
        ]
        if not checkpoint_dirs:
            return None

        # Sort by modification time and return the latest
        latest_dir = max(checkpoint_dirs, key=lambda d: d.stat().st_mtime)
        return latest_dir.name

    def _load_severity_classifier(self, checkpoint_path: Path):
        """Load the severity classifier model."""
        model_path = checkpoint_path / "severity_classifier.pkl"
        if model_path.exists():
            try:
                self.models["severity_classifier"] = joblib.load(model_path)
                logger.info("Loaded severity classifier model")
            except Exception as e:
                logger.error(f"Error loading severity classifier: {e}")

    def _load_flareup_predictor(self, checkpoint_path: Path):
        """Load the flareup predictor model."""
        model_path = checkpoint_path / "flareup_predictor.pkl"
        if model_path.exists():
            try:
                self.models["flareup_predictor"] = joblib.load(model_path)
                logger.info("Loaded flareup predictor model")
            except Exception as e:
                logger.error(f"Error loading flareup predictor: {e}")

    def _load_recommendation_engine(self, checkpoint_path: Path):
        """Load the recommendation engine model."""
        model_path = checkpoint_path / "recommendation_engine.pkl"
        if model_path.exists():
            try:
                self.models["recommendation_engine"] = joblib.load(model_path)
                logger.info("Loaded recommendation engine model")
            except Exception as e:
                logger.error(f"Error loading recommendation engine: {e}")

    def _initialize_fallback_models(self):
        """Initialize simple fallback models if trained models aren't available."""
        logger.warning("Initializing fallback models - trained models not available")
        # Fallback models would be implemented here if needed
        pass

    def predict_severity(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict IBS severity based on user data with comprehensive error handling.

        Args:
            user_data: Dictionary containing user features

        Returns:
            Dictionary with severity prediction and confidence
        """
        model_name = "severity_classifier"
        
        try:
            # Validate input data
            required_fields = ["symptoms"]
            if not self._validate_input_data(user_data, required_fields):
                logger.warning("Invalid input data for severity prediction, using fallback")
                return self._fallback_severity_prediction(user_data)
            
            if model_name not in self.models:
                logger.info(f"Model {model_name} not available, using fallback")
                return self._fallback_severity_prediction(user_data)

            # Prepare features for the model
            features = self._prepare_severity_features(user_data)
            
            if not features or len(features) == 0:
                raise MLModelError("Failed to prepare features from user data")
            
            # Scale features if scaler is available
            if "feature_scaler" in self.models:
                try:
                    features_scaled = self.models["feature_scaler"].transform([features])
                except Exception as e:
                    logger.warning(f"Feature scaling failed: {e}, using unscaled features")
                    features_scaled = [features]
            else:
                features_scaled = [features]

            # Make prediction
            model = self.models[model_name]
            
            # Handle different model types
            if hasattr(model, "predict_proba"):
                # Classification model - predict severity category
                probabilities = model.predict_proba(features_scaled)[0]
                
                if len(probabilities) == 0:
                    raise MLModelError("Model returned empty probabilities")
                
                prediction_idx = np.argmax(probabilities)
                
                # Map to severity categories
                severity_categories = ['none', 'mild', 'moderate', 'severe', 'very_severe']
                if prediction_idx < len(severity_categories):
                    severity_level = severity_categories[prediction_idx]
                    severity_score = prediction_idx * 2.5  # Scale to 0-10
                else:
                    severity_level = 'moderate'
                    severity_score = 5.0
                    
                confidence = float(np.max(probabilities))
                
                # Validate confidence
                if not (0 <= confidence <= 1):
                    logger.warning(f"Invalid confidence value: {confidence}, setting to 0.5")
                    confidence = 0.5
                    
            else:
                # Regression model - predict severity score directly
                prediction = model.predict(features_scaled)[0]
                
                if np.isnan(prediction) or np.isinf(prediction):
                    raise MLModelError(f"Model returned invalid prediction: {prediction}")
                
                severity_score = float(np.clip(prediction, 0, 10))
                severity_level = self._score_to_severity_level(severity_score)
                confidence = 0.8  # Default confidence for regression

            # Log successful prediction
            logger.debug(f"Severity prediction successful: {severity_level} (score: {severity_score:.2f})")

            return {
                "severity_score": severity_score,
                "severity_level": severity_level,
                "confidence": confidence,
                "model_version": self.model_metadata.get("model_versions", {}).get(
                    model_name, "unknown"
                ),
                "model_status": self.model_status.get(model_name, ModelStatus.LOADED).value,
                "prediction_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._log_model_error(model_name, e, "severity prediction")
            logger.error(f"Severity prediction failed: {e}")
            
            # Return error response with guidance for user
            return {
                "severity_score": None,
                "severity_level": "unknown",
                "confidence": 0.0,
                "model_version": "unavailable",
                "model_status": ModelStatus.FAILED.value,
                "error_message": (
                    "ML model temporarily unavailable. Please try again later or "
                    "consult with healthcare provider."
                ),
                "user_guidance": (
                    "Consider tracking symptoms manually and consulting with your "
                    "healthcare provider for personalized assessment."
                ),
                "prediction_timestamp": datetime.now().isoformat(),
                "retry_suggested": True
            }

    def predict_flareup_risk(
        self, user_data: Dict[str, Any], days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Predict flareup risk with comprehensive error handling.

        Args:
            user_data: Dictionary containing user features
            days_ahead: Number of days ahead to predict

        Returns:
            Dictionary with flareup risk prediction
        """
        model_name = "flareup_predictor"
        
        try:
            # Validate input data
            required_fields = ["recent_symptoms", "lifestyle_factors"]
            if not self._validate_input_data(user_data, required_fields):
                logger.warning("Invalid input data for flareup prediction, using fallback")
                return self._fallback_flareup_prediction(user_data)
            
            # Validate days_ahead parameter
            if not isinstance(days_ahead, int) or days_ahead < 1 or days_ahead > 30:
                logger.warning(f"Invalid days_ahead value: {days_ahead}, using default 7")
                days_ahead = 7
            
            if model_name not in self.models:
                logger.info(f"Model {model_name} not available, using fallback")
                return self._fallback_flareup_prediction(user_data)

            # Prepare features for the model
            features = self._prepare_flareup_features(user_data)
            
            if not features or len(features) == 0:
                raise MLModelError("Failed to prepare features from user data")
            
            # Scale features if scaler is available
            if "feature_scaler" in self.models:
                try:
                    features_scaled = self.models["feature_scaler"].transform([features])
                except Exception as e:
                    logger.warning(f"Feature scaling failed: {e}, using unscaled features")
                    features_scaled = [features]
            else:
                features_scaled = [features]

            # Make prediction
            model = self.models[model_name]
            
            # Handle different model types
            if hasattr(model, "predict_proba"):
                # Classification model
                probabilities = model.predict_proba(features_scaled)[0]
                
                if len(probabilities) == 0:
                    raise MLModelError("Model returned empty probabilities")
                
                # Assume binary classification (no flareup, flareup)
                risk_score = float(probabilities[-1]) * 10  # Scale to 0-10
                confidence = float(np.max(probabilities))
            else:
                # Regression model
                prediction = model.predict(features_scaled)[0]
                
                if np.isnan(prediction) or np.isinf(prediction):
                    raise MLModelError(f"Model returned invalid prediction: {prediction}")
                
                risk_score = float(np.clip(prediction, 0, 10))
                confidence = 0.8

            # Validate outputs
            if not (0 <= risk_score <= 10):
                logger.warning(f"Invalid risk score: {risk_score}, clipping to valid range")
                risk_score = np.clip(risk_score, 0, 10)
                
            if not (0 <= confidence <= 1):
                logger.warning(f"Invalid confidence value: {confidence}, setting to 0.5")
                confidence = 0.5

            risk_level = self._score_to_risk_level(risk_score)
            
            # Log successful prediction
            logger.debug(f"Flareup prediction successful: {risk_level} (score: {risk_score:.2f})")

            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "confidence": confidence,
                "days_ahead": days_ahead,
                "model_version": self.model_metadata.get("model_versions", {}).get(
                    model_name, "unknown"
                ),
                "model_status": self.model_status.get(model_name, ModelStatus.LOADED).value,
                "prediction_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._log_model_error(model_name, e, "flareup prediction")
            logger.error(f"Flareup prediction failed: {e}")
            
            # Return error response with guidance for user
            return {
                "risk_score": None,
                "risk_level": "unknown",
                "confidence": 0.0,
                "days_ahead": days_ahead,
                "model_version": "unavailable",
                "model_status": ModelStatus.FAILED.value,
                "error_message": (
                    "Risk prediction temporarily unavailable. Please try again "
                    "later or consult with healthcare provider."
                ),
                "user_guidance": (
                    "Continue monitoring symptoms and maintain your current "
                    "management plan. Contact healthcare provider if symptoms worsen."
                ),
                "prediction_timestamp": datetime.now().isoformat(),
                "retry_suggested": True
            }

    def generate_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations with comprehensive error handling.

        Args:
            user_data: Dictionary containing user profile and current state

        Returns:
            Dictionary with personalized recommendations
        """
        model_name = "recommendation_engine"
        
        try:
            # Validate input data
            required_fields = ["user_profile", "current_symptoms"]
            if not self._validate_input_data(user_data, required_fields):
                logger.warning("Invalid input data for recommendations, using fallback")
                return self._fallback_recommendations(user_data)
            
            if model_name not in self.models:
                logger.info(f"Model {model_name} not available, using fallback")
                return self._fallback_recommendations(user_data)

            # Prepare features for the model
            features = self._prepare_recommendation_features(user_data)
            
            if not features or len(features) == 0:
                raise MLModelError("Failed to prepare features from user data")
            
            # Scale features if scaler is available
            if "feature_scaler" in self.models:
                try:
                    features_scaled = self.models["feature_scaler"].transform([features])
                except Exception as e:
                    logger.warning(f"Feature scaling failed: {e}, using unscaled features")
                    features_scaled = [features]
            else:
                features_scaled = [features]

            # Make prediction
            model = self.models[model_name]
            prediction = model.predict(features_scaled)[0]
            
            if np.isnan(prediction) or np.isinf(prediction):
                raise MLModelError(f"Model returned invalid prediction: {prediction}")
            
            score = float(np.clip(prediction, 0, 10))

            # Generate recommendations based on score
            dietary_recs = self._generate_diet_recommendations(score, user_data)
            lifestyle_recs = self._generate_lifestyle_recommendations(score, user_data)
            
            # Calculate personalization score based on available user data
            personalization_factors = len([k for k in user_data.get("user_profile", {}).keys() if user_data["user_profile"][k]])
            personalization_score = min(personalization_factors * 10, 100)
            
            # Log successful recommendation generation
            logger.debug(f"Recommendations generated successfully with score: {score:.2f}")

            return {
                "recommendations": {
                    "dietary": dietary_recs,
                    "lifestyle": lifestyle_recs,
                    "immediate": [
                        {
                            "action": "Continue logging symptoms and food intake daily",
                            "priority": "high",
                            "explanation": "Consistent tracking is essential for identifying patterns",
                            "expected_benefit": "Better symptom management and more accurate future predictions",
                            "timeline": "Daily"
                        }
                    ],
                    "supplements": []
                },
                "personalization_score": personalization_score,
                "implementation_priority": ["dietary", "lifestyle", "immediate", "supplements"],
                "expected_timeline": {
                    "dietary": "1-2 weeks",
                    "lifestyle": "2-4 weeks", 
                    "immediate": "immediate",
                    "supplements": "4-6 weeks"
                },
                "model_version": self.model_metadata.get("model_versions", {}).get(
                    model_name, "unknown"
                ),
                "model_status": self.model_status.get(model_name, ModelStatus.LOADED).value,
                "prediction_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._log_model_error(model_name, e, "recommendation generation")
            logger.error(f"Recommendation generation failed: {e}")
            
            # Return error response with guidance for user
            return {
                "diet_recommendations": [],
                "lifestyle_recommendations": [],
                "immediate_actions": [],
                "supplements": [],
                "personalization_score": 0.0,
                "implementation_priority": [],
                "expected_timeline": {},
                "model_version": "unavailable",
                "model_status": ModelStatus.FAILED.value,
                "error_message": (
                    "Personalized recommendations temporarily unavailable. "
                    "Please try again later."
                ),
                "user_guidance": (
                    "Continue with your current management plan and consult "
                    "with healthcare provider for personalized guidance."
                ),
                "prediction_timestamp": datetime.now().isoformat(),
                "retry_suggested": True
            }

    def _prepare_severity_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Prepare features for severity classification."""
        features = []

        # Add symptom features
        symptoms = user_data.get("symptoms", {})
        features.extend(
            [
                symptoms.get("abdominal_pain", 0),
                symptoms.get("bloating", 0),
                symptoms.get("gas", 0),
                symptoms.get("diarrhea", 0),
                symptoms.get("constipation", 0),
                symptoms.get("urgency", 0),
                symptoms.get("incomplete_evacuation", 0),
                symptoms.get("nausea", 0),
                symptoms.get("fatigue", 0),
                symptoms.get("mood_score", 5),
                symptoms.get("stress_level", 5),
                symptoms.get("sleep_quality", 5),
            ]
        )

        # Add user profile features
        profile = user_data.get("profile", {})
        features.extend(
            [
                profile.get("age", 30),
                1 if profile.get("gender") == "female" else 0,
                profile.get("bmi", 25.0),
                profile.get("years_since_diagnosis", 1),
            ]
        )

        return features

    def _prepare_flareup_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Prepare features for flareup prediction."""
        # Similar to severity features but may include additional temporal features
        features = self._prepare_severity_features(user_data)

        # Add recent symptom trends
        recent_symptoms = user_data.get("recent_symptoms", {})
        features.extend(
            [
                recent_symptoms.get("avg_severity_7d", 0),
                recent_symptoms.get("symptom_frequency_7d", 0),
                recent_symptoms.get("stress_trend", 0),
            ]
        )

        return features

    def _prepare_recommendation_features(
        self, user_data: Dict[str, Any]
    ) -> List[float]:
        """Prepare features for recommendation generation."""
        # Use severity features as base
        features = self._prepare_severity_features(user_data)

        # Add dietary features
        diet = user_data.get("diet", {})
        features.extend(
            [
                diet.get("fodmap_adherence", 0.5),
                diet.get("fiber_intake", 25.0),
                diet.get("trigger_food_frequency", 0.1),
            ]
        )

        return features

    def _score_to_severity_level(self, score: float) -> str:
        """Convert severity score to level."""
        if score < 0.25:
            return "none"
        elif score < 0.5:
            return "mild"
        elif score < 0.75:
            return "moderate"
        else:
            return "severe"

    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "moderate"
        else:
            return "high"

    def _generate_diet_recommendations(
        self, score: float, user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate diet recommendations based on score."""
        recommendations = []

        if score > 0.7:
            recommendations.append(
                {
                    "category": "FODMAP Management",
                    "recommendation": "Consider following a strict low FODMAP diet for 2-6 weeks",
                    "priority": "high",
                    "rationale": "Your symptoms suggest high sensitivity to FODMAP foods",
                }
            )

        if score > 0.5:
            recommendations.append(
                {
                    "category": "Fiber Intake",
                    "recommendation": "Gradually increase soluble fiber intake to improve symptoms",
                    "priority": "medium",
                    "rationale": "Soluble fiber can help regulate bowel movements and reduce symptoms",
                }
            )

        return recommendations

    def _generate_lifestyle_recommendations(
        self, score: float, user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate lifestyle recommendations based on score."""
        recommendations = []

        stress_level = user_data.get("symptoms", {}).get("stress_level", 5)

        if stress_level > 6:
            recommendations.append(
                {
                    "category": "Stress Management",
                    "recommendation": "Practice stress reduction techniques like meditation or yoga",
                    "priority": "high",
                    "rationale": f"Your stress level ({stress_level}/10) is elevated, which can worsen IBS symptoms",
                }
            )

        if score > 0.6:
            recommendations.append(
                {
                    "category": "Exercise",
                    "recommendation": "Engage in regular, moderate exercise to improve gut health",
                    "priority": "medium",
                    "rationale": "Regular exercise can help regulate digestion and reduce IBS symptoms",
                }
            )

        return recommendations



    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models with health status."""
        return {
            "models_loaded": list(self.models.keys()),
            "model_metadata": self.model_metadata,
            "model_status": {k: v.value for k, v in self.model_status.items()},
            "error_counts": self.error_counts,
            "last_errors": self.last_errors,
            "health_check": self._perform_health_check()
        }

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform a health check on all loaded models."""
        health_status = {}
        
        for model_name, model in self.models.items():
            try:
                # Basic health check - ensure model can be called
                if hasattr(model, 'predict'):
                    # Create dummy data for testing
                    dummy_features = np.array([[0.5] * 10])  # 10 features with 0.5 values
                    _ = model.predict(dummy_features)
                    health_status[model_name] = "healthy"
                else:
                    health_status[model_name] = "no_predict_method"
            except Exception as e:
                health_status[model_name] = f"unhealthy: {str(e)}"
                
        return health_status

    def reload_models(self):
        """Reload all models and reset error tracking."""
        logger.info("Reloading all models...")
        self.models.clear()
        self.model_metadata.clear()
        self.model_status.clear()
        self.error_counts.clear()
        self.last_errors.clear()
        self._load_latest_models()
        logger.info("Model reload completed")
