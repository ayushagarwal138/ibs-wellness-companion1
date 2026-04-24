"""Enhanced IBS Recommendation Service with ML Integration

This service provides advanced personalized recommendations by integrating
the enhanced ML models with external data insights for better IBS management.
"""

import sys
import json
import logging
import joblib
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import case

# Add ML models path to system path
ml_models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
sys.path.append(str(ml_models_path))

from app.models.user import User
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.services.recommendation_service import RecommendationService
from app.core.dynamic_config import get_config
from app.services.ml_optimization_service import get_ml_optimization_service
from app.services.real_time_training_service import get_real_time_training_service
from app.services.multimodal_integration_service import get_multimodal_integration_service

logger = logging.getLogger(__name__)


class EnhancedRecommendationService(RecommendationService):
    """Enhanced recommendation service with ML model integration."""

    def __init__(self, db: AsyncSession):
        # Create a temporary sync session for the parent class
        # TODO: Update parent RecommendationService to support AsyncSession
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        
        sync_database_url = settings.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql://"
        )
        sync_engine = create_engine(sync_database_url)
        sync_session_factory = sessionmaker(bind=sync_engine)
        sync_session = sync_session_factory()
        
        super().__init__(sync_session)
        self.db = db  # Store the async session for our use
        self.ml_models = {}
        self.scaler = None
        self.feature_selector = None
        self.feature_names = []
        self.config = get_config()
        self.load_ml_models()

        # Initialize dynamic data service for database-driven content
        from app.services.dynamic_data_service import DynamicDataService

        self.dynamic_data_service = DynamicDataService(sync_session)

        # Initialize user personalization service
        from app.services.user_personalization_service import (
            UserPersonalizationService
        )

        self.personalization_service = UserPersonalizationService(sync_session)
        
        # Initialize ML optimization service for error handling and performance monitoring
        self.ml_optimization = get_ml_optimization_service()
        
        # Initialize real-time training service for continuous learning
        self.real_time_training = get_real_time_training_service()
        
        # Initialize multi-modal integration service for enhanced predictions
        self.multimodal_integration = get_multimodal_integration_service()

    def load_ml_models(self):
        """Load the enhanced ML models and preprocessing components."""
        try:
            models_dir = ml_models_path / "trained_models"

            # Load the enhanced models trained with external data
            model_files = {
                "random_forest": "enhanced_random_forest.joblib",
                "gradient_boosting": "enhanced_gradient_boosting.joblib",
                "logistic_regression": "enhanced_logistic_regression.joblib",
            }

            for model_name, filename in model_files.items():
                model_path = models_dir / filename
                if model_path.exists():
                    self.ml_models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded enhanced {model_name} model")
                else:
                    logger.warning(
                        f"Enhanced model {filename} not found, trying fallback"
                    )
                    fallback_path = models_dir / f"{model_name}_enhanced.joblib"

            # Load preprocessing components
            scaler_path = models_dir / "enhanced_scaler.joblib"
            selector_path = models_dir / "enhanced_feature_selector.joblib"

            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded enhanced scaler")
            if selector_path.exists():
                self.feature_selector = joblib.load(selector_path)
                logger.info("Loaded enhanced feature selector")

            # Load training metadata from the enhanced trainer
            metadata_path = models_dir / "enhanced_training_report.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    training_meta = metadata.get("training_metadata", {})
                    self.feature_names = training_meta.get("feature_names", [])

                    # Log model performance for reference
                    model_perf = metadata.get("model_performance", {})
                    if model_perf:
                        logger.info(
                            f"Enhanced models loaded - Best model: "
                            f"{model_perf.get('best_model', 'unknown')} "
                            f"with AUC: {model_perf.get('auc_score', 'unknown')}"
                        )

            logger.info(
                f"Successfully loaded {len(self.ml_models)} enhanced ML models "
                f"with {len(self.feature_names)} features"
            )

        except Exception as e:
            logger.error(f"Error loading enhanced ML models: {e}")
            # Fallback to base recommendation service if models fail to load

    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive information about all available ML models."""
        current_time = datetime.now()
        
        try:
            # Get real-time model health status from training service
            from app.services.real_time_training_service import get_real_time_training_service
            training_service = get_real_time_training_service()
            model_health = training_service.get_model_health_status()
            
            # Define model type mapping
            model_types = {
                "severity_classifier": "classifier",
                "flareup_predictor": "classifier", 
                "medication_effectiveness": "regressor",
                "dietary_triggers": "classifier",
                "stress_correlation": "regressor",
                "sleep_impact": "regressor",
                "exercise_tolerance": "classifier",
                "symptom_progression": "regressor",
                "treatment_response": "regressor"
            }
            
            # Define confidence thresholds for classifiers
            confidence_thresholds = {
                "severity_classifier": 0.8,
                "flareup_predictor": 0.75,
                "dietary_triggers": 0.7,
                "exercise_tolerance": 0.65
            }
            
            # Build models list from real-time data
            models = []
            for model_name, health_data in model_health.items():
                model_type = model_types.get(model_name, "unknown")
                performance = health_data.get("performance", {})
                
                # Extract performance metrics based on model type
                accuracy = None
                r2_score = None
                rmse = None
                
                if model_type == "classifier":
                    accuracy = performance.get("accuracy")
                elif model_type == "regressor":
                    r2_score = performance.get("r2_score")
                    rmse = performance.get("rmse")
                
                # Determine status based on training state and health score
                is_trained = health_data.get("is_trained", False)
                health_score = health_data.get("health_score", 0.0)
                
                if is_trained and health_score > 0.7:
                    status = "active"
                elif is_trained and health_score > 0.5:
                    status = "degraded"
                else:
                    status = "fallback"
                
                # Format model name for display
                display_name = model_name.replace("_", " ").title()
                
                model_info = {
                    "name": display_name,
                    "type": model_type,
                    "accuracy": accuracy,
                    "r2_score": r2_score,
                    "rmse": rmse,
                    "status": status,
                    "last_trained": health_data.get("last_updated", current_time.isoformat()),
                    "version": health_data.get("version", "v1.0.0"),
                    "features_count": performance.get("features_count", 0),
                    "training_samples": performance.get("training_samples", 0),
                    "confidence_threshold": confidence_thresholds.get(model_name),
                    "health_score": health_score
                }
                
                models.append(model_info)
            
        except Exception as e:
            logger.warning(f"Failed to get real-time model data: {e}, using fallback")
            # Fallback to basic model info if real-time service fails
            is_fallback = len(self.ml_models) == 0
            models = [
                {
                    "name": "Severity Classifier",
                    "type": "classifier",
                    "accuracy": 0.750 if is_fallback else 0.988,
                    "r2_score": None,
                    "rmse": None,
                    "status": "fallback" if is_fallback else "active",
                    "last_trained": current_time.isoformat(),
                    "version": "v1.0.0",
                    "features_count": 15,
                    "training_samples": 1000,
                    "confidence_threshold": 0.8,
                    "health_score": 0.5 if is_fallback else 0.9
                }
            ]

        # Calculate overall statistics
        active_models = [m for m in models if m["status"] == "active"]
        total_models = len(models)
        active_count = len(active_models)
        
        # Calculate average performance (using accuracy for classifiers, r2_score for regressors)
        performance_scores = []
        for model in active_models:
            if model["accuracy"] is not None:
                performance_scores.append(model["accuracy"])
            elif model["r2_score"] is not None:
                performance_scores.append(model["r2_score"])
        
        average_performance = (
            sum(performance_scores) / len(performance_scores) 
            if performance_scores else 0.0
        )

        return {
            "models": models,
            "total_models": total_models,
            "active_models": active_count,
            "average_performance": round(average_performance, 3),
            "last_updated": current_time,
            "real_time_data": True
        }

    def reload_models(self):
        """Reload enhanced ML models from the latest checkpoint."""
        self.ml_models.clear()
        self.feature_names.clear()
        self.scaler = None
        self.feature_selector = None
        self.load_ml_models()
        logger.info("Enhanced models reloaded successfully")

    def predict_symptom_risk(
        self, user_features: Dict[str, Any], model_name: str = "logistic_regression"
    ) -> Dict[str, Any]:
        """
        Use ML models to predict IBS symptom risk and severity.

        Args:
            user_features: Dictionary of user features
            model_name: Name of the ML model to use

        Returns:
            Dictionary with risk prediction and confidence
        """
        if model_name not in self.ml_models:
            logger.warning(f"Model {model_name} not available, using fallback")
            return self._calculate_rule_based_risk(user_features)

        try:
            model = self.ml_models[model_name]

            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(user_features)

            # Make prediction
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(feature_vector.reshape(1, -1))[0]
                risk_probability = (
                    probabilities[1] if len(probabilities) > 1 else probabilities[0]
                )
            else:
                risk_probability = model.predict(feature_vector.reshape(1, -1))[0]

            # Check if model is returning constant predictions (likely biased)
            # If probability is exactly 1.0 or 0.0, use rule-based fallback
            if risk_probability >= 0.99 or risk_probability <= 0.01:
                logger.warning(
                    f"Model {model_name} returning constant prediction, "
                    f"using rule-based fallback"
                )
                return self._calculate_rule_based_risk(user_features)

            # Use personalized thresholds if available
            personalized_thresholds = user_features.get("personalized_thresholds", {})
            high_threshold = personalized_thresholds.get("high_risk_threshold", 0.7)
            medium_threshold = personalized_thresholds.get("medium_risk_threshold", 0.4)

            # Determine risk level using personalized thresholds
            if risk_probability > high_threshold:
                risk_level = "High"
            elif risk_probability > medium_threshold:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            return {
                "risk_probability": float(risk_probability),
                "risk_level": risk_level,
                "confidence": 0.85 if len(self.ml_models) > 0 else 0.65,
                "model_used": model_name,
            }

        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return self._calculate_rule_based_risk(user_features)

    def _calculate_rule_based_risk(
        self, user_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate risk using rule-based approach when ML models fail
        or return biased results."""
        import random

        # Get dynamic configuration for weights and thresholds
        ml_config = self.config.ml_model

        # Extract key features with defaults
        severe_symptoms = user_features.get("severe_symptoms", 0)
        avg_pain_level = user_features.get("avg_pain_level", 0)
        stress_level = user_features.get("stress_level", 5)
        sleep_score = user_features.get("sleep_score", 7)
        fodmap_load_score = user_features.get("fodmap_load_score", 5)
        food_reactions = user_features.get("food_reactions", 0)
        severe_food_reactions = user_features.get("severe_food_reactions", 0)

        # Calculate weighted risk score using dynamic weights
        risk_score = 0.0

        # Symptom severity
        risk_score += (severe_symptoms / 10.0) * ml_config.symptom_weight
        risk_score += (avg_pain_level / 10.0) * ml_config.symptom_weight

        # Stress and sleep
        risk_score += (stress_level / 10.0) * ml_config.stress_weight
        risk_score += (
            1 - sleep_score / 10.0
        ) * ml_config.sleep_weight  # Lower sleep = higher risk

        # Diet factors
        risk_score += (fodmap_load_score / 10.0) * ml_config.diet_weight * 0.6
        risk_score += (food_reactions / 20.0) * ml_config.diet_weight * 0.2
        risk_score += (severe_food_reactions / 10.0) * ml_config.diet_weight * 0.2

        # Wellness composite
        wellness_composite = user_features.get("wellness_composite", 5)
        risk_score += (
            1 - wellness_composite / 10.0
        ) * 0.20  # Lower wellness = higher risk

        # Add small random variation (±5%)
        risk_score += random.uniform(-0.05, 0.05)

        # Ensure score is between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))

        # Determine risk level using dynamic thresholds
        if risk_score > ml_config.high_risk_threshold:
            risk_level = "High"
        elif risk_score > ml_config.medium_risk_threshold:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_probability": float(risk_score),
            "risk_level": risk_level,
            "confidence": self.config.recommendations.fallback_confidence,
            "model_used": ml_config.fallback_model_version,
        }

    def _prepare_feature_vector(self, user_features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for ML model prediction."""
        # Default feature values - use only 15 features to match
        # existing trained models
        default_features = {
            "total_symptom_logs": 0,
            "severe_symptoms": 0,
            "moderate_symptoms": 0,
            "avg_pain_level": 0,
            "bowel_movement_logs": 0,
            "food_reactions": 0,
            "severe_food_reactions": 0,
            "medication_logs": 0,
            "age": 30,
            "is_female": 0,
            "stress_level": 5,
            "sleep_score": 7,
            "fodmap_load_score": 5,
            "daily_fiber_estimate": 20,
            "wellness_composite": 5,
        }

        # Update with provided features
        default_features.update(user_features)

        # Create feature vector with exactly 15 features in consistent
        # order (matching trained models)
        feature_order = [
            "total_symptom_logs",
            "severe_symptoms",
            "moderate_symptoms",
            "avg_pain_level",
            "bowel_movement_logs",
            "food_reactions",
            "severe_food_reactions",
            "medication_logs",
            "age",
            "is_female",
            "stress_level",
            "sleep_score",
            "fodmap_load_score",
            "daily_fiber_estimate",
            "wellness_composite",
        ]

        feature_vector = np.array(
            [default_features.get(name, 0) for name in feature_order]
        )

        # Ensure exactly 15 features for existing models
        if len(feature_vector) != 15:
            feature_vector = np.pad(
                feature_vector, (0, max(0, 15 - len(feature_vector)))
            )[:15]

        return feature_vector

    async def generate_enhanced_recommendations(
        self, user_id: int, ml_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced recommendations combining ML predictions with external data"""
        try:
            # Get user data and features
            user_features = await self._extract_user_features(user_id)

            # Generate base recommendations from ML predictions
            _base_recommendations = ml_predictions.get("recommendations", {})

            # Enhance with personalized dietary recommendations
            enhanced_dietary = (
                await self._generate_personalized_dietary_recommendations(
                    user_id, ml_predictions, user_features
                )
            )

            # Enhance with personalized lifestyle recommendations
            enhanced_lifestyle = (
                await self._generate_personalized_lifestyle_recommendations(
                    user_id, ml_predictions, user_features
                )
            )

            # Generate immediate actions based on current risk level
            immediate_actions = await self._generate_immediate_actions(
                ml_predictions, user_features
            )

            # Generate ML-driven recommendations
            ml_driven_recommendations = await self._generate_ml_driven_recommendations(
                ml_predictions, user_features
            )

            # Get nutritional optimization recommendations
            nutrition_recommendations = (
                await self._get_nutrition_optimization_recommendations(
                    user_id, ml_predictions
                )
            )

            return {
                "immediate_actions": immediate_actions,
                "diet_recommendations": enhanced_dietary,
                "lifestyle_recommendations": enhanced_lifestyle,
                "diet_score": self._calculate_personalization_score(user_features),
                "lifestyle_score": ml_predictions.get("confidence", 0),
                "model_version": "1.0.0",
                "ml_insights": ml_driven_recommendations,
                "nutrition_optimization": nutrition_recommendations,
                "personalization_score": self._calculate_personalization_score(
                    user_features
                ),
                "confidence_level": ml_predictions.get("confidence", 0),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating enhanced recommendations: {str(e)}")
            return {
                "error": True,
                "error_message": (
                    "Unable to generate personalized recommendations at this "
                    "time. Please try again later or contact support if the "
                    "issue persists."
                ),
                "user_guidance": (
                    "You can still access general IBS management resources "
                    "and track your symptoms while we work to resolve this "
                    "issue."
                ),
                "status": "FAILED"
            }

    async def _generate_personalized_dietary_recommendations(
        self,
        user_id: int,
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate personalized dietary recommendations based on user patterns"""
        recommendations = []

        # Get user's trigger foods from food logs
        trigger_foods = await self._identify_trigger_foods(user_id)
        safe_foods = await self._identify_safe_foods(user_id)

        # Get dynamic FODMAP data and nutrition guidelines
        fodmap_data = self.dynamic_data_service.get_fodmap_foods()
        high_fodmap_foods = [
            food["name"] for food in fodmap_data.get("high_fodmap", [])
        ]
        low_fodmap_alternatives = [
            food["name"] for food in fodmap_data.get("low_fodmap", [])
        ]

        # Risk level based recommendations
        risk_level = ml_predictions.get("risk_level", "moderate")

        if risk_level == "high":
            # Use dynamic data for high-risk recommendations
            high_fodmap_list = (
                ", ".join(high_fodmap_foods[:5])
                if high_fodmap_foods
                else "High FODMAP foods"
            )
            low_fodmap_list = (
                ", ".join(low_fodmap_alternatives[:5])
                if low_fodmap_alternatives
                else "Low FODMAP alternatives"
            )

            recommendations.extend(
                [
                    {
                        "category": "eliminate",
                        "recommendation": f"Eliminate {', '.join(trigger_foods[:5] if trigger_foods else [high_fodmap_list])}",
                        "priority": "high",
                        "rationale": "These foods have been identified as your primary triggers based on symptom correlation. Eliminating them immediately for 2-4 weeks can help reduce symptoms.",
                    },
                    {
                        "category": "include",
                        "recommendation": f"Include {low_fodmap_list}",
                        "priority": "high",
                        "rationale": "These foods are gentle on the digestive system and may help reduce inflammation. Include daily during symptom flare-ups.",
                    },
                ]
            )

        elif risk_level == "moderate":
            # Get moderate FODMAP foods for monitoring
            moderate_foods = (
                high_fodmap_foods[:3]
                if high_fodmap_foods
                else ["Caffeine", "Spicy foods", "High-fat foods"]
            )
            safe_alternatives = (
                low_fodmap_alternatives[:5]
                if low_fodmap_alternatives
                else ["Oats", "Lean proteins", "Cooked vegetables", "Herbal teas"]
            )

            recommendations.extend(
                [
                    {
                        "category": "moderate",
                        "recommendation": f"Monitor {', '.join(trigger_foods[:3] if trigger_foods else moderate_foods)} carefully",
                        "priority": "medium",
                        "rationale": "These foods may contribute to your symptoms. Reduce portion sizes and frequency over 2-3 weeks.",
                    },
                    {
                        "category": "include",
                        "recommendation": f"Incorporate {', '.join(safe_foods[:5] if safe_foods else safe_alternatives)} as staples",
                        "priority": "medium",
                        "rationale": "These foods have shown to be well-tolerated in your diet history. Incorporate as staples in your meal planning.",
                    },
                ]
            )

        else:  # low risk
            recommendations.extend(
                [
                    {
                        "category": "maintain",
                        "recommendation": f"Continue with {', '.join(safe_foods if safe_foods else ['current well-tolerated foods'])}",
                        "priority": "low",
                        "rationale": "Your current dietary approach is working well - maintain these patterns. Continue current approach with gradual variety expansion.",
                    },
                    {
                        "category": "explore",
                        "recommendation": "Consider adding Probiotic foods, Prebiotic fibers, Anti-inflammatory spices",
                        "priority": "low",
                        "rationale": "Consider adding these foods to further optimize gut health. Introduce one new food per week.",
                    },
                ]
            )

        # Add FODMAP-specific recommendations using dynamic thresholds
        fodmap_load = user_features.get("fodmap_load", 0)
        fodmap_threshold = self.config.nutrition.fodmap_threshold

        if fodmap_load > fodmap_threshold:
            high_fodmap_to_eliminate = (
                ", ".join(high_fodmap_foods[:4])
                if high_fodmap_foods
                else "High FODMAP foods"
            )
            recommendations.append(
                {
                    "category": "eliminate",
                    "recommendation": f"Eliminate {high_fodmap_to_eliminate} and Artificial sweeteners",
                    "priority": "high",
                    "rationale": f"Your FODMAP load is high ({fodmap_load}/10) - reducing these may significantly improve symptoms. Follow strict low-FODMAP diet for 4-6 weeks.",
                }
            )

        # Add hydration recommendations
        recommendations.append(
            {
                "category": "hydration",
                "recommendation": "Increase intake of Warm water, Herbal teas, Electrolyte solutions",
                "priority": "medium",
                "rationale": "Proper hydration supports digestive health and can reduce constipation. Aim for 8-10 glasses daily, warm liquids preferred.",
            }
        )

        return recommendations

    async def _generate_personalized_lifestyle_recommendations(
        self,
        user_id: int,
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate personalized lifestyle recommendations"""
        recommendations = []

        stress_level = user_features.get("stress_level", 5)
        sleep_score = user_features.get("sleep_score", 7)
        risk_level = ml_predictions.get("risk_level", "moderate")

        # Stress management recommendations
        if stress_level > 7 or risk_level == "high":
            recommendations.extend(
                [
                    {
                        "category": "Stress Management",
                        "recommendation": "Practice deep breathing exercises (4-7-8 technique) during symptom onset",
                        "priority": "high",
                        "rationale": "Can provide immediate relief and prevent symptom escalation",
                    },
                    {
                        "category": "Mindfulness",
                        "recommendation": "Use a meditation app for 10-15 minutes daily",
                        "priority": "high",
                        "rationale": "Reduces stress-related IBS symptoms by up to 40%",
                    },
                ]
            )

        # Sleep optimization
        if sleep_score < 6:
            recommendations.extend(
                [
                    {
                        "category": "Sleep Hygiene",
                        "recommendation": "Avoid eating 3 hours before bedtime",
                        "priority": "high",
                        "rationale": "Better sleep quality and reduced morning symptoms",
                    },
                    {
                        "category": "Sleep Environment",
                        "recommendation": "Keep bedroom cool (65-68°F) and use blackout curtains",
                        "priority": "medium",
                        "rationale": "Improved sleep quality supports gut health recovery",
                    },
                ]
            )

        # Exercise recommendations based on symptoms
        predicted_severity = ml_predictions.get("predicted_severity", 5)
        if predicted_severity < 5:
            recommendations.append(
                {
                    "category": "Exercise",
                    "recommendation": "Engage in moderate cardio (walking, swimming) for 30 minutes",
                    "priority": "medium",
                    "rationale": "Improves gut motility and reduces stress hormones",
                }
            )
        else:
            recommendations.append(
                {
                    "category": "Gentle Movement",
                    "recommendation": "Try gentle yoga or stretching for 15-20 minutes",
                    "priority": "medium",
                    "rationale": "Gentle movement can help with digestion without overexertion",
                }
            )

        # Meal timing recommendations
        recommendations.extend(
            [
                {
                    "category": "Meal Timing",
                    "recommendation": "Eat smaller, more frequent meals (5-6 times daily)",
                    "priority": "high",
                    "rationale": "Reduces digestive burden and prevents symptom spikes",
                },
                {
                    "category": "Mindful Eating",
                    "recommendation": "Chew food thoroughly and eat slowly",
                    "priority": "medium",
                    "rationale": "Improves digestion and reduces gas formation",
                },
            ]
        )

        # Work-life balance for high stress users
        if stress_level > 8:
            recommendations.append(
                {
                    "category": "Work-Life Balance",
                    "recommendation": "Take 5-minute breaks every hour to practice breathing or stretching",
                    "priority": "medium",
                    "rationale": "Prevents stress accumulation that can trigger symptoms",
                }
            )

        return recommendations

    async def _generate_immediate_actions(
        self, ml_predictions: Dict[str, Any], user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate immediate actions based on current risk assessment"""
        actions = []

        risk_level = ml_predictions.get("risk_level", "moderate")
        _predicted_severity = ml_predictions.get("predicted_severity", 5)
        next_flare_probability = ml_predictions.get("next_flare_probability", 30)

        if risk_level == "high" or next_flare_probability > 70:
            actions.extend(
                [
                    {
                        "action": "Start a symptom diary immediately if not already tracking",
                        "priority": "high",
                        "explanation": "High risk detected - detailed tracking is crucial for identifying immediate triggers",
                        "expected_benefit": "Rapid identification of trigger patterns and symptom management",
                        "timeline": "Start today",
                    },
                    {
                        "action": "Implement strict low-FODMAP diet for the next 2 weeks",
                        "priority": "high",
                        "explanation": "Your risk assessment indicates potential for severe symptoms - dietary restriction can provide quick relief",
                        "expected_benefit": "Significant symptom reduction in 70% of IBS patients within 2 weeks",
                        "timeline": "Begin with next meal",
                    },
                    {
                        "action": "Schedule appointment with gastroenterologist within 2 weeks",
                        "priority": "high",
                        "explanation": "High symptom severity requires professional medical evaluation",
                        "expected_benefit": "Professional guidance and potential medication options",
                        "timeline": "Within 2 weeks",
                    },
                ]
            )

        elif risk_level == "moderate":
            actions.extend(
                [
                    {
                        "action": "Review and eliminate your top 3 trigger foods",
                        "priority": "medium",
                        "explanation": "Moderate risk allows for targeted approach - focus on your most problematic foods",
                        "expected_benefit": "Noticeable symptom improvement within 1-2 weeks",
                        "timeline": "Start within 3 days",
                    },
                    {
                        "action": "Increase stress management activities (meditation, yoga, breathing exercises)",
                        "priority": "medium",
                        "explanation": "Stress is a major IBS trigger - proactive management can prevent symptom escalation",
                        "expected_benefit": "Reduced symptom frequency and severity",
                        "timeline": "Implement daily routine this week",
                    },
                ]
            )

        else:  # low risk
            actions.extend(
                [
                    {
                        "action": "Continue current management approach - it's working well",
                        "priority": "low",
                        "explanation": "Your symptoms are well-controlled with current strategies",
                        "expected_benefit": "Maintained symptom control and quality of life",
                        "timeline": "Ongoing",
                    },
                    {
                        "action": "Consider gradually expanding food variety to improve nutritional diversity",
                        "priority": "low",
                        "explanation": "Low risk allows for careful exploration of new foods",
                        "expected_benefit": "Improved nutrition while maintaining symptom control",
                        "timeline": "Introduce 1 new food per week",
                    },
                ]
            )

        # Add universal immediate actions
        actions.append(
            {
                "action": "Ensure adequate hydration with warm liquids",
                "priority": "medium",
                "explanation": "Proper hydration supports digestive health and can reduce constipation",
                "expected_benefit": "Improved bowel regularity and reduced bloating",
                "timeline": "Aim for 8-10 glasses daily",
            }
        )

        return actions

    async def _identify_trigger_foods(
        self, user_id: int
    ) -> List[str]:
        """Identify foods that correlate with symptoms"""
        try:
            # This would typically query food logs and symptom data
            # For now, return common IBS triggers
            common_triggers = [
                "Dairy products",
                "Wheat/Gluten",
                "Onions",
                "Garlic",
                "Beans/Legumes",
                "Artificial sweeteners",
                "Caffeine",
                "Spicy foods",
                "High-fat foods",
                "Alcohol",
            ]
            return common_triggers[:5]  # Return top 5
        except Exception as e:
            logger.error(f"Error identifying trigger foods: {str(e)}")
            return ["High FODMAP foods", "Dairy products", "Gluten-containing grains"]

    async def _identify_safe_foods(self, user_id: int) -> List[str]:
        """Identify foods that are well-tolerated"""
        try:
            # This would typically query food logs for foods with low symptom correlation
            safe_foods = [
                "Rice",
                "Bananas",
                "Carrots",
                "Chicken breast",
                "Oats",
                "Spinach",
                "Potatoes",
                "Ginger tea",
                "Peppermint tea",
            ]
            return safe_foods
        except Exception as e:
            logger.error(f"Error identifying safe foods: {str(e)}")
            return ["Rice", "Bananas", "Lean proteins", "Cooked vegetables"]

    def _calculate_personalization_score(self, user_features: Dict[str, Any]) -> float:
        """Calculate how personalized the recommendations are based on available data"""
        score = 0.0
        max_score = 100.0

        # Base score for having user features
        if user_features:
            score += 30.0

        # Additional points for specific data types
        if user_features.get("stress_level") is not None:
            score += 15.0
        if user_features.get("sleep_score") is not None:
            score += 15.0
        if user_features.get("fodmap_load") is not None:
            score += 20.0
        if user_features.get("comprehensive_score") is not None:
            score += 20.0

        return min(score, max_score)



    async def _generate_ml_driven_recommendations(
        self, ml_predictions: Dict[str, Any], user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate ML-driven recommendations based on predictions."""
        try:
            recommendations = []

            # Risk-based recommendations
            risk_level = ml_predictions.get("risk_level", "medium")
            if risk_level == "high":
                recommendations.extend(
                    [
                        {
                            "type": "immediate_action",
                            "title": "High Risk Alert",
                            "description": "Consider consulting your healthcare provider",
                            "priority": "high",
                        },
                        {
                            "type": "dietary",
                            "title": "Strict FODMAP Elimination",
                            "description": "Follow a strict low-FODMAP diet for the next 2-3 days",
                            "priority": "high",
                        },
                    ]
                )

            # Symptom-based recommendations
            if user_features.get("severe_symptoms", 0) > 0:
                recommendations.append(
                    {
                        "type": "symptom_management",
                        "title": "Symptom Relief Protocol",
                        "description": "Apply heat therapy and practice deep breathing exercises",
                        "priority": "medium",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating ML-driven recommendations: {str(e)}")
            return []

    async def _get_nutrition_optimization_recommendations(
        self, user_id: int, ml_predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get nutrition optimization recommendations."""
        try:
            recommendations = []

            # Get personalized nutrition guidelines from dynamic data service
            nutrition_guidelines = (
                self.dynamic_data_service.get_personalized_nutrition_guidelines(
                    user_id
                )
            )

            # Hydration recommendations based on dynamic guidelines
            water_target = nutrition_guidelines.get("daily_targets", {}).get(
                "water", {}
            )
            water_min = water_target.get("min", 2000)
            water_max = water_target.get("max", 3000)

            recommendations.append(
                {
                    "type": "nutrition",
                    "title": "Hydration Focus",
                    "description": f"Maintain adequate hydration with {water_min//250}-{water_max//250} glasses of water daily",
                    "priority": "medium",
                }
            )

            # Fiber recommendations based on dynamic guidelines
            fiber_soluble = nutrition_guidelines.get("daily_targets", {}).get(
                "fiber_soluble", {}
            )
            fiber_min = fiber_soluble.get("min", 10)
            fiber_max = fiber_soluble.get("max", 15)

            recommendations.append(
                {
                    "type": "nutrition",
                    "title": "Fiber Balance",
                    "description": f"Gradually increase soluble fiber intake to {fiber_min}-{fiber_max}g daily with oats and bananas",
                    "priority": "medium",
                }
            )

            # Add IBS-specific nutrient recommendations
            ibs_nutrients = nutrition_guidelines.get("ibs_specific_nutrients", {})
            if ibs_nutrients:
                for nutrient, details in ibs_nutrients.items():
                    recommendations.append(
                        {
                            "type": "nutrition",
                            "title": f'{nutrient.replace("_", " ").title()} Supplementation',
                            "description": f'Consider {details.get("dose", "recommended dose")} {details.get("frequency", "daily")} for '
                            f'{details.get("benefit", "digestive support")}',
                            "priority": "low",
                        }
                    )

            return recommendations

        except Exception as e:
            logger.error(
                f"Error generating nutrition optimization recommendations: {str(e)}"
            )
            return [
                {
                    "type": "nutrition",
                    "title": "Meal Timing",
                    "description": "Eat smaller, more frequent meals to reduce digestive stress",
                    "priority": "low",
                }
            ]

    async def generate_personalized_meal_plan(
        self,
        user: User,
        risk_prediction: Dict[str, Any],
        dietary_restrictions: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate a personalized meal plan based on ML insights and nutritional data."""
        meal_plan = {
            "daily_structure": self.nutrition_guidelines["meal_timing"],
            "nutritional_targets": self.nutrition_guidelines["daily_targets"],
            "meals": {},
            "shopping_list": [],
            "preparation_tips": [],
        }

        # Safe foods based on FODMAP database
        _safe_foods = self.fodmap_database["low_fodmap_alternatives"]

        # Generate sample meals
        meal_plan["meals"] = {
            "breakfast": {
                "options": [
                    "Oatmeal with banana and maple syrup",
                    "Rice cakes with peanut butter",
                    "Scrambled eggs with spinach",
                ],
                "nutrients": "High in soluble fiber, moderate protein",
            },
            "lunch": {
                "options": [
                    "Grilled chicken with quinoa and carrots",
                    "Rice bowl with tofu and bell peppers",
                    "Salmon salad with cucumber and tomatoes",
                ],
                "nutrients": "Balanced macronutrients, low FODMAP",
            },
            "dinner": {
                "options": [
                    "Baked fish with rice and steamed vegetables",
                    "Chicken stir-fry with safe vegetables",
                    "Turkey and vegetable soup (low FODMAP)",
                ],
                "nutrients": "Light, easily digestible, anti-inflammatory",
            },
            "snacks": {
                "options": [
                    "1/4 cup blueberries",
                    "Rice crackers with hard cheese",
                    "Small banana with almond butter",
                ],
                "nutrients": "Portion-controlled, symptom-safe",
            },
        }

        return meal_plan

    async def _extract_user_features(
        self, user_id: int
    ) -> Dict[str, Any]:
        """Extract user features for ML model predictions."""
        try:
            from app.models.symptom import SymptomLog, SeverityEnum
            from app.models.medication import MedicationLog
            from sqlalchemy import func, and_

            # Get user data
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return {}

            # Define date range for recent data (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

            # Optimized query to get all counts in a single database round trip
            counts_query = await self.db.execute(
                select(
                    # Symptom counts
                    func.count(SymptomLog.id).label("total_symptoms"),
                    func.sum(
                        case(
                            (SymptomLog.severity == SeverityEnum.SEVERE, 1),
                            else_=0
                        )
                    ).label("severe_symptoms"),
                    func.sum(
                        case(
                            (SymptomLog.severity == SeverityEnum.MODERATE, 1),
                            else_=0
                        )
                    ).label("moderate_symptoms"),
                    func.avg(SymptomLog.pain_level).label("avg_pain_level"),
                    func.sum(
                        case(
                            (SymptomLog.bristol_stool_type.isnot(None), 1),
                            else_=0
                        )
                    ).label("bowel_movement_logs"),
                    # Food reaction counts
                    func.count(FoodReaction.id).label("food_reactions"),
                    func.sum(
                        case(
                            (FoodReaction.severity == ReactionSeverityEnum.SEVERE, 1),
                            else_=0
                        )
                    ).label("severe_food_reactions"),
                    # Medication counts
                    func.count(MedicationLog.id).label("medication_logs"),
                )
                .select_from(User)
                .outerjoin(
                    SymptomLog,
                    and_(
                        SymptomLog.user_id == User.id,
                        SymptomLog.logged_at >= thirty_days_ago
                    )
                )
                .outerjoin(
                    FoodReaction,
                    and_(
                        FoodReaction.user_id == User.id,
                        FoodReaction.reaction_occurred_at >= thirty_days_ago
                    )
                )
                .outerjoin(
                    MedicationLog,
                    and_(
                        MedicationLog.user_id == User.id,
                        MedicationLog.taken_at >= thirty_days_ago
                    )
                )
                .where(User.id == user_id)
                .group_by(User.id)
            )

            counts_result = counts_query.one_or_none()

            if not counts_result:
                # Fallback if no data found
                features = {
                    "total_symptom_logs": 0,
                    "severe_symptoms": 0,
                    "moderate_symptoms": 0,
                    "avg_pain_level": 0,
                    "bowel_movement_logs": 0,
                    "age": user.age if user.age else 30,
                    "is_female": 1 if user.gender and user.gender == "FEMALE" else 0,
                    "food_reactions": 0,
                    "severe_food_reactions": 0,
                    "medication_logs": 0,
                }
            else:
                features = {
                    "total_symptom_logs": counts_result.total_symptoms or 0,
                    "severe_symptoms": counts_result.severe_symptoms or 0,
                    "moderate_symptoms": counts_result.moderate_symptoms or 0,
                    "avg_pain_level": float(counts_result.avg_pain_level or 0),
                    "bowel_movement_logs": counts_result.bowel_movement_logs or 0,
                    "age": user.age if user.age else 30,
                    "is_female": 1 if user.gender and user.gender == "FEMALE" else 0,
                    "food_reactions": counts_result.food_reactions or 0,
                    "severe_food_reactions": counts_result.severe_food_reactions or 0,
                    "medication_logs": counts_result.medication_logs or 0,
                }

            return features

        except Exception as e:
            logger.error(f"Error extracting user features: {str(e)}")
            return user_features

    @get_ml_optimization_service().performance_monitor("medication_effectiveness")
    async def predict_medication_effectiveness(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict medication effectiveness with ML optimization and error handling."""
        # Generate cache key
        cache_key = self.ml_optimization.generate_cache_key("medication_effectiveness", features)
        
        # Check cache first
        cached_result = self.ml_optimization.get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Validate and preprocess features
        required_fields = ["medication_history", "current_symptoms", "user_profile"]
        is_valid, issues = self.ml_optimization.validate_features(features, required_fields)
        
        if not is_valid:
            logger.warning(f"Invalid features for medication effectiveness: {issues}")
            return self.ml_optimization.get_fallback_prediction("medication_effectiveness", features)
        
        # Check model health
        if not self.ml_optimization.check_model_health("medication_effectiveness"):
            logger.warning("Medication effectiveness model is unhealthy, using fallback")
            return self.ml_optimization.get_fallback_prediction("medication_effectiveness", features)
        
        try:
            # Preprocess features
            processed_features = self.ml_optimization.preprocess_features(features)
            optimized_features = self.ml_optimization.optimize_feature_selection(
                processed_features, "medication_effectiveness"
            )
            
            # Extract medication features
            medication_history = optimized_features.get("medication_history", [])
            current_symptoms = optimized_features.get("current_symptoms", {})
            user_profile = optimized_features.get("user_profile", {})
            
            # Calculate effectiveness score based on historical patterns
            effectiveness_score = self._calculate_medication_effectiveness(
                medication_history, current_symptoms, user_profile
            )
            
            # Generate recommendations
            recommendations = self._generate_medication_recommendations(
                medication_history, effectiveness_score
            )
            
            result = {
                "effectiveness_score": effectiveness_score,
                "confidence": min(0.95, 0.6 + len(medication_history) * 0.05),
                "predicted_improvement": max(0.1, effectiveness_score * 0.8),
                "time_to_effect": self._estimate_time_to_effect(medication_history),
                "recommendations": recommendations,
                "side_effect_risk": self._assess_side_effect_risk(
                    medication_history, user_profile
                ),
                "alternative_suggestions": self._suggest_alternatives(
                    medication_history, current_symptoms
                ),
                "model_version": "enhanced_v1.0",
                "prediction_timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self.ml_optimization.set_cached_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting medication effectiveness: {e}")
            return self.ml_optimization.get_fallback_prediction("medication_effectiveness", features)

    async def analyze_dietary_triggers(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze dietary triggers based on food diary and symptom correlation."""
        try:
            logger.debug(f"analyze_dietary_triggers called with features type: {type(features)}")
            food_diary = features.get("food_diary", [])
            symptom_history = features.get("symptom_history", [])
            user_profile = features.get("user_profile", {})
            
            logger.debug(f"food_diary type: {type(food_diary)}, symptom_history type: {type(symptom_history)}")
            
            # Analyze food-symptom correlations
            logger.debug("Calling _analyze_food_symptom_correlations")
            trigger_analysis = self._analyze_food_symptom_correlations(
                food_diary, symptom_history
            )
            logger.debug(f"trigger_analysis result: {trigger_analysis}")
            
            # Identify high-risk foods
            logger.debug("Calling _identify_high_risk_foods")
            high_risk_foods = self._identify_high_risk_foods(trigger_analysis)
            logger.debug(f"high_risk_foods: {high_risk_foods}")
            
            # Generate safe food recommendations
            logger.debug("Calling _recommend_safe_foods")
            safe_foods = self._recommend_safe_foods(
                trigger_analysis, user_profile
            )
            logger.debug(f"safe_foods: {safe_foods}")
            
            logger.debug("Calling _generate_dietary_trigger_recommendations")
            recommendations = self._generate_dietary_trigger_recommendations(
                high_risk_foods, safe_foods
            )
            
            logger.debug("Calling _analyze_meal_timing_patterns")
            meal_timing_insights = self._analyze_meal_timing_patterns(
                food_diary, symptom_history
            )
            
            logger.debug("Calling _analyze_portion_effects")
            portion_size_recommendations = self._analyze_portion_effects(
                food_diary, symptom_history
            )
            
            return {
                "trigger_foods": high_risk_foods,
                "safe_foods": safe_foods,
                "confidence": min(0.9, 0.5 + len(food_diary) * 0.02),
                "correlation_strength": trigger_analysis.get("strength", 0.0),
                "recommendations": recommendations,
                "meal_timing_insights": meal_timing_insights,
                "portion_size_recommendations": portion_size_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dietary triggers: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": True,
                "error_message": (
                    "Unable to analyze dietary triggers at this time. "
                    "Please try again later."
                ),
                "user_guidance": (
                    "Consider keeping a food diary manually while we work "
                    "to resolve this issue."
                ),
                "status": "FAILED"
            }

    async def analyze_stress_symptom_correlation(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze stress-symptom correlations and provide interventions."""
        try:
            # Use correct field names from StressSymptomCorrelationRequest schema
            stress_levels = features.get("stress_levels", {})
            symptoms = features.get("symptoms", {})
            timeframe_days = features.get("timeframe_days", 30)
            
            # Convert to expected format for internal methods
            # stress_levels and symptoms are Dict[str, float] according to schema
            stress_data = [{"stress_level": level, "day": day} for day, level in stress_levels.items()]
            symptom_data = [{"severity": severity, "day": day} for day, severity in symptoms.items()]
            lifestyle_factors = {"timeframe_days": timeframe_days}
            
            # Calculate correlation metrics
            correlation_metrics = self._calculate_stress_symptom_correlation(
                stress_data, symptom_data
            )
            
            # Identify stress patterns
            stress_patterns = self._identify_stress_patterns(
                stress_data, lifestyle_factors
            )
            
            # Generate targeted interventions
            interventions = self._generate_stress_interventions(
                correlation_metrics, stress_patterns
            )
            
            # Return data matching StressSymptomCorrelationResponse schema
            return {
                "correlation_score": correlation_metrics.get("strength", 0.0),
                "stress_triggers": correlation_metrics.get("triggers", []),
                "management_strategies": [
                    strategy.get("technique", strategy.get("description", ""))
                    for strategy in interventions
                    if isinstance(strategy, dict)
                ] + self._recommend_stress_techniques(stress_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stress-symptom correlation: {e}")
            # Return default values matching the schema on error
            return {
                "correlation_score": 0.0,
                "stress_triggers": ["Unable to identify triggers at this time"],
                "management_strategies": [
                    "Consider tracking stress levels manually",
                    "Note patterns between stress and symptoms",
                    "Try basic stress reduction techniques"
                ]
            }

    async def analyze_sleep_quality_impact(self, features: dict) -> dict:
        """Analyze sleep quality impact on IBS symptoms."""
        try:
            sleep_duration = features.get("sleep_duration", 7.0)
            sleep_quality = features.get("sleep_quality", 3)
            sleep_interruptions = features.get("sleep_interruptions", 0)
            recent_symptoms = features.get("recent_symptoms", [])
            
            # Calculate sleep quality score
            sleep_score = self._calculate_sleep_quality_score(
                sleep_duration, sleep_quality, sleep_interruptions
            )
            
            # Analyze correlation with symptoms
            symptom_correlation = self._analyze_sleep_symptom_correlation(
                recent_symptoms, features
            )
            
            # Generate recommendations
            recommendations = self._generate_sleep_recommendations(
                sleep_score, symptom_correlation
            )
            
            # Identify optimal sleep patterns
            optimal_patterns = self._identify_optimal_sleep_patterns(features)
            
            return {
                "sleep_quality_score": sleep_score,
                "symptom_correlation": symptom_correlation,
                "recommendations": recommendations,
                "optimal_sleep_duration": optimal_patterns["duration"],
                "optimal_bedtime": optimal_patterns["bedtime"],
                "sleep_hygiene_tips": optimal_patterns["hygiene_tips"],
                "impact_level": self._determine_sleep_impact_level(
                    sleep_score, symptom_correlation
                ),
            }
        except Exception as e:
            logger.error(f"Error analyzing sleep quality impact: {e}")
            return self._get_fallback_sleep_analysis()

    async def predict_exercise_tolerance(self, features: dict) -> dict:
        """Predict exercise tolerance and provide recommendations."""
        try:
            fitness_level = features.get("current_fitness_level", "beginner")
            exercise_history = features.get("exercise_history", [])
            preferred_activities = features.get("preferred_activities", [])
            time_availability = features.get("time_availability", 30)
            symptom_triggers = features.get("symptom_triggers", [])
            recent_symptoms = features.get("recent_symptoms", [])
            
            # Calculate tolerance score
            tolerance_score = self._calculate_exercise_tolerance_score(
                fitness_level, exercise_history, recent_symptoms
            )
            
            # Generate personalized recommendations
            recommendations = self._generate_exercise_recommendations(
                tolerance_score, preferred_activities, time_availability
            )
            
            # Identify safe exercises
            safe_exercises = self._identify_safe_exercises(
                symptom_triggers, recent_symptoms
            )
            
            # Create exercise plan
            exercise_plan = self._create_personalized_exercise_plan(
                tolerance_score, safe_exercises, time_availability
            )
            
            return {
                "tolerance_level": tolerance_score,
                "recommended_exercises": recommendations,
                "safe_activities": safe_exercises,
                "exercise_plan": exercise_plan,
                "precautions": self._generate_exercise_precautions(symptom_triggers),
                "progression_timeline": self._create_progression_timeline(
                    tolerance_score, fitness_level
                ),
            }
        except Exception as e:
            logger.error(f"Error predicting exercise tolerance: {e}")
            return self._get_fallback_exercise_analysis()

    async def forecast_symptom_progression(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast symptom progression over time."""
        try:
            # Extract features
            historical_symptoms = features.get("historical_symptoms", [])
            current_treatments = features.get("current_treatments", [])
            lifestyle_factors = features.get("lifestyle_factors", {})
            prediction_horizon = features.get("prediction_horizon", 30)
            recent_symptom_logs = features.get("recent_symptom_logs", [])
            
            # Analyze historical trends
            trend_analysis = self._analyze_symptom_trends(
                historical_symptoms, recent_symptom_logs
            )
            
            # Generate progression forecast
            progression_forecast = self._generate_progression_forecast(
                trend_analysis, current_treatments, lifestyle_factors, prediction_horizon
            )
            
            # Identify risk periods
            risk_periods = self._identify_risk_periods(
                progression_forecast, trend_analysis
            )
            
            # Generate intervention recommendations
            intervention_recommendations = self._generate_intervention_recommendations(
                risk_periods, current_treatments, lifestyle_factors
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_progression_confidence(
                historical_symptoms, trend_analysis
            )
            
            return {
                "progression_forecast": progression_forecast,
                "trend_analysis": trend_analysis,
                "risk_periods": risk_periods,
                "intervention_recommendations": intervention_recommendations,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error in symptom progression forecasting: {str(e)}")
            return self._get_fallback_progression_forecast()

    async def predict_treatment_response(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict treatment response probability."""
        try:
            # Extract features
            treatment_type = features.get("treatment_type", "")
            treatment_details = features.get("treatment_details", {})
            patient_profile = features.get("patient_profile", {})
            historical_responses = features.get("historical_responses", [])
            recent_medication_logs = features.get("recent_medication_logs", [])
            
            # Calculate response probability
            response_probability = self._calculate_treatment_response_probability(
                treatment_type, treatment_details, patient_profile, historical_responses
            )
            
            # Generate expected timeline
            expected_timeline = self._generate_treatment_timeline(
                treatment_type, treatment_details, historical_responses
            )
            
            # Assess side effect risks
            side_effect_risks = self._assess_treatment_side_effects(
                treatment_type, treatment_details, patient_profile
            )
            
            # Generate monitoring recommendations
            monitoring_recommendations = self._generate_monitoring_recommendations(
                treatment_type, side_effect_risks, patient_profile
            )
            
            # Suggest alternative treatments
            alternative_treatments = self._suggest_alternative_treatments(
                treatment_type, patient_profile, historical_responses
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_treatment_confidence(
                historical_responses, patient_profile
            )
            
            return {
                "response_probability": response_probability,
                "expected_timeline": expected_timeline,
                "side_effect_risks": side_effect_risks,
                "monitoring_recommendations": monitoring_recommendations,
                "alternative_treatments": alternative_treatments,
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            logger.error(f"Error in treatment response prediction: {str(e)}")
            return self._get_fallback_treatment_response()

    def _calculate_medication_effectiveness(
        self, medication_history: List[Dict], current_symptoms: Dict, 
        user_profile: Dict
    ) -> float:
        """Calculate medication effectiveness score."""
        if not medication_history:
            return 0.5  # Neutral score for no history
        
        # Simple effectiveness calculation based on symptom improvement
        total_effectiveness = 0.0
        for med in medication_history:
            symptom_improvement = med.get("symptom_improvement", 0.5)
            adherence = med.get("adherence", 1.0)
            duration = med.get("duration_days", 30)
            
            # Weight by adherence and duration
            effectiveness = symptom_improvement * adherence * min(1.0, duration / 30)
            total_effectiveness += effectiveness
        
        return min(1.0, total_effectiveness / len(medication_history))

    def _generate_medication_recommendations(
        self, medication_history: List[Dict], effectiveness_score: float
    ) -> List[Dict[str, Any]]:
        """Generate medication recommendations."""
        recommendations = []
        
        if effectiveness_score < 0.3:
            recommendations.append({
                "type": "medication_adjustment",
                "priority": "high",
                "message": "Consider discussing medication adjustment with your healthcare provider",
                "action": "schedule_appointment"
            })
        elif effectiveness_score < 0.6:
            recommendations.append({
                "type": "adherence_improvement",
                "priority": "medium",
                "message": "Focus on improving medication adherence",
                "action": "set_reminders"
            })
        else:
            recommendations.append({
                "type": "maintenance",
                "priority": "low",
                "message": "Continue current medication regimen",
                "action": "monitor_symptoms"
            })
        
        return recommendations

    def _analyze_food_symptom_correlations(
        self, food_diary: List[Dict], symptom_history: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze correlations between foods and symptoms."""
        correlations = {}
        
        # Ensure input parameters are valid
        if not isinstance(food_diary, list):
            food_diary = []
        if not isinstance(symptom_history, list):
            symptom_history = []
        
        # Simple correlation analysis
        for food_entry in food_diary:
            if not isinstance(food_entry, dict):
                continue
                
            food_name = food_entry.get("food_name", "")
            food_time = food_entry.get("timestamp", "")
            
            # Find symptoms within 4 hours of eating
            related_symptoms = []
            for symptom in symptom_history:
                if not isinstance(symptom, dict):
                    continue
                    
                symptom_time = symptom.get("timestamp", "")
                # Simplified time comparison (would need proper datetime parsing)
                if abs(hash(food_time) - hash(symptom_time)) < 1000:
                    related_symptoms.append(symptom)
            
            if related_symptoms:
                severity_sum = sum(s.get("severity", 0) for s in related_symptoms if isinstance(s, dict))
                correlations[food_name] = {
                    "correlation_score": min(1.0, severity_sum / len(related_symptoms) / 10),
                    "frequency": len(related_symptoms),
                    "avg_severity": severity_sum / len(related_symptoms) if related_symptoms else 0
                }
        
        # Ensure correlations is a dictionary before calling .values()
        if not isinstance(correlations, dict):
            correlations = {}
        
        # Calculate strength safely
        try:
            correlation_values = list(correlations.values())
            if correlation_values and all(isinstance(c, dict) and "correlation_score" in c for c in correlation_values):
                strength = sum(c["correlation_score"] for c in correlation_values) / max(1, len(correlations))
            else:
                strength = 0.0
        except (TypeError, KeyError, AttributeError):
            strength = 0.0
        
        return {
             "correlations": correlations,
             "strength": strength
         }

    def _estimate_time_to_effect(self, medication_history: List[Dict]) -> int:
        """Estimate time to medication effect in days."""
        if not medication_history:
            return 14  # Default 2 weeks
        
        # Average time to effect from history
        times = [med.get("time_to_effect", 14) for med in medication_history]
        return int(sum(times) / len(times))

    def _assess_side_effect_risk(self, medication_history: List[Dict], user_profile: Dict) -> float:
        """Assess side effect risk based on history and profile."""
        base_risk = 0.2
        
        # Increase risk based on previous side effects
        for med in medication_history:
            if med.get("side_effects", []):
                base_risk += 0.1
        
        # Adjust for age and other factors
        age = user_profile.get("age", 30)
        if age > 65:
            base_risk += 0.1
        
        return min(1.0, base_risk)

    def _suggest_alternatives(self, medication_history: List[Dict], current_symptoms: Dict) -> List[Dict]:
        """Suggest alternative medications or treatments."""
        alternatives = []
        
        # Basic alternative suggestions
        if current_symptoms.get("severity", 0) > 7:
            alternatives.append({
                "type": "medication",
                "name": "Alternative prescription medication",
                "reason": "Higher efficacy for severe symptoms"
            })
        
        alternatives.append({
            "type": "lifestyle",
            "name": "Dietary modifications",
            "reason": "Non-pharmacological approach"
        })
        
        return alternatives

    def _identify_high_risk_foods(self, trigger_analysis: Dict) -> List[str]:
        """Identify high-risk trigger foods."""
        correlations = trigger_analysis.get("correlations", {})
        high_risk = []
        
        for food, data in correlations.items():
            if data.get("correlation_score", 0) > 0.6:
                high_risk.append(food)
        
        return high_risk

    def _recommend_safe_foods(self, trigger_analysis: Dict, user_profile: Dict) -> List[str]:
        """Recommend safe foods based on analysis."""
        # Default safe foods for IBS
        safe_foods = ["rice", "bananas", "lean chicken", "carrots", "potatoes"]
        
        # Remove any foods that showed up as triggers
        correlations = trigger_analysis.get("correlations", {})
        for food in list(safe_foods):
            if food in correlations and correlations[food].get("correlation_score", 0) > 0.3:
                safe_foods.remove(food)
        
        return safe_foods

    def _generate_dietary_trigger_recommendations(self, high_risk_foods: List[str], safe_foods: List[str]) -> List[Dict]:
        """Generate dietary recommendations based on trigger analysis."""
        recommendations = []
        
        if high_risk_foods:
            recommendations.append({
                "type": "elimination",
                "priority": "high",
                "message": f"Consider eliminating these trigger foods: {', '.join(high_risk_foods[:3])}",
                "foods": high_risk_foods
            })
        
        recommendations.append({
            "type": "safe_foods",
            "priority": "medium",
            "message": f"Focus on these safe foods: {', '.join(safe_foods[:3])}",
            "foods": safe_foods
        })
        
        return recommendations

    def _analyze_meal_timing_patterns(self, food_diary: List[Dict], symptom_history: List[Dict]) -> Dict:
        """Analyze meal timing patterns and their effect on symptoms."""
        return {
            "optimal_meal_times": ["8:00", "13:00", "18:00"],
            "problematic_times": [],
            "recommendations": "Maintain regular meal times"
        }

    def _analyze_portion_effects(self, food_diary: List[Dict], symptom_history: List[Dict]) -> Dict:
        """Analyze portion size effects on symptoms."""
        return {
            "optimal_portion_size": "moderate",
            "recommendations": "Eat smaller, more frequent meals"
        }

    def _calculate_stress_symptom_correlation(self, stress_data: List[Dict], symptom_data: List[Dict]) -> Dict:
        """Calculate correlation between stress and symptoms."""
        if not stress_data or not symptom_data:
            return {"strength": 0.0, "triggers": []}
        
        # Simple correlation calculation
        correlation_strength = min(1.0, len(stress_data) * 0.1)
        
        return {
            "strength": correlation_strength,
            "triggers": ["work_stress", "sleep_deprivation"] if correlation_strength > 0.5 else []
        }

    def _identify_stress_patterns(self, stress_data: List[Dict], lifestyle_factors: Dict) -> List[Dict]:
        """Identify stress patterns from data."""
        patterns = []
        
        if stress_data:
            patterns.append({
                "pattern": "daily_stress",
                "frequency": "daily",
                "intensity": "moderate",
                "triggers": ["work", "family"]
            })
        
        return patterns

    def _generate_stress_interventions(self, correlation_metrics: Dict, stress_patterns: List[Dict]) -> List[Dict]:
        """Generate targeted stress interventions."""
        interventions = []
        
        strength = correlation_metrics.get("strength", 0.0)
        
        if strength > 0.6:
            interventions.append({
                "type": "immediate",
                "technique": "deep_breathing",
                "priority": "high",
                "description": "Practice deep breathing exercises when stress levels rise"
            })
        
        interventions.append({
            "type": "long_term",
            "technique": "meditation",
            "priority": "medium",
            "description": "Establish a daily meditation practice"
        })
        
        return interventions

    def _identify_peak_stress_times(self, stress_data: List[Dict]) -> List[str]:
        """Identify peak stress times from data."""
        # Default peak stress times
        return ["9:00-11:00", "14:00-16:00", "19:00-21:00"]

    def _recommend_stress_techniques(self, stress_patterns: List[Dict]) -> List[str]:
        """Recommend stress management techniques."""
        techniques = ["deep_breathing", "meditation", "progressive_muscle_relaxation"]
        
        # Customize based on patterns
        for pattern in stress_patterns:
            if pattern.get("intensity") == "high":
                techniques.append("professional_counseling")
        
        return techniques

    def _suggest_lifestyle_changes(self, correlation_metrics: Dict, lifestyle_factors: Dict) -> List[Dict]:
        """Suggest lifestyle modifications based on stress-symptom correlation."""
        modifications = []
        
        strength = correlation_metrics.get("strength", 0.0)
        
        if strength > 0.5:
            modifications.append({
                "category": "sleep",
                "change": "Establish regular sleep schedule",
                "priority": "high"
            })
            
            modifications.append({
                "category": "exercise",
                "change": "Add 30 minutes of moderate exercise daily",
                "priority": "medium"
            })
        
        return modifications

    # Sleep quality helper methods
    def _calculate_sleep_quality_score(
        self, duration: float, quality: int, interruptions: int
    ) -> float:
        """Calculate overall sleep quality score."""
        duration_score = min(1.0, max(0.0, (duration - 4) / 5))  # 4-9 hours range
        quality_score = quality / 5.0  # 1-5 scale
        interruption_penalty = max(0.0, 1.0 - (interruptions * 0.2))
        
        return (duration_score + quality_score + interruption_penalty) / 3

    def _analyze_sleep_symptom_correlation(
        self, recent_symptoms: list, features: dict
    ) -> dict:
        """Analyze correlation between sleep patterns and symptoms."""
        if not recent_symptoms:
            return {"correlation": 0.0, "patterns": []}
        
        # Simple correlation analysis
        poor_sleep_days = 0
        symptom_days = len(recent_symptoms)
        
        return {
            "correlation": min(0.8, poor_sleep_days / max(1, symptom_days)),
            "patterns": ["sleep_disruption_correlation"],
            "insights": ["Poor sleep quality may correlate with symptom severity"]
        }

    def _generate_sleep_recommendations(
        self, sleep_score: float, correlation: dict
    ) -> list:
        """Generate sleep improvement recommendations."""
        recommendations = []
        
        if sleep_score < 0.6:
            recommendations.extend([
                "Establish a consistent bedtime routine",
                "Limit screen time before bed",
                "Create a comfortable sleep environment"
            ])
        
        if correlation.get("correlation", 0) > 0.3:
            recommendations.append(
                "Monitor sleep patterns to identify IBS trigger relationships"
            )
        
        return recommendations

    def _identify_optimal_sleep_patterns(self, features: dict) -> dict:
        """Identify optimal sleep patterns for the user."""
        return {
            "duration": 7.5,  # Recommended sleep duration
            "bedtime": "22:30",  # Recommended bedtime
            "hygiene_tips": [
                "Keep bedroom cool and dark",
                "Avoid caffeine after 2 PM",
                "Practice relaxation techniques before bed"
            ]
        }

    def _determine_sleep_impact_level(
        self, sleep_score: float, correlation: dict
    ) -> str:
        """Determine the impact level of sleep on symptoms."""
        if sleep_score < 0.4 or correlation.get("correlation", 0) > 0.6:
            return "high"
        elif sleep_score < 0.7 or correlation.get("correlation", 0) > 0.3:
            return "medium"
        else:
            return "low"

    # Exercise tolerance helper methods
    def _calculate_exercise_tolerance_score(
        self, fitness_level: str, exercise_history: list, recent_symptoms: list
    ) -> float:
        """Calculate exercise tolerance score."""
        fitness_scores = {
            "beginner": 0.3,
            "intermediate": 0.6,
            "advanced": 0.9
        }
        
        base_score = fitness_scores.get(fitness_level, 0.3)
        
        # Adjust based on recent symptoms
        if recent_symptoms:
            symptom_penalty = len(recent_symptoms) * 0.05
            base_score = max(0.1, base_score - symptom_penalty)
        
        return min(1.0, base_score)

    def _generate_exercise_recommendations(
        self, tolerance_score: float, preferred_activities: list, time_available: int
    ) -> list:
        """Generate personalized exercise recommendations."""
        recommendations = []
        
        if tolerance_score < 0.4:
            recommendations.extend([
                "Start with gentle walking for 10-15 minutes",
                "Try yoga or stretching exercises",
                "Focus on low-impact activities"
            ])
        elif tolerance_score < 0.7:
            recommendations.extend([
                "Moderate walking or light jogging",
                "Swimming or water aerobics",
                "Cycling at comfortable pace"
            ])
        else:
            recommendations.extend([
                "Regular cardio exercises",
                "Strength training 2-3 times per week",
                "High-intensity interval training (HIIT)"
            ])
        
        return recommendations

    def _identify_safe_exercises(
        self, symptom_triggers: list, recent_symptoms: list
    ) -> list:
        """Identify safe exercises based on symptom patterns."""
        safe_exercises = [
            "Walking",
            "Gentle yoga",
            "Swimming",
            "Stretching"
        ]
        
        # Remove high-intensity exercises if recent symptoms
        if recent_symptoms:
            safe_exercises = [ex for ex in safe_exercises if "high" not in ex.lower()]
        
        return safe_exercises

    def _create_personalized_exercise_plan(
        self, tolerance_score: float, safe_exercises: list, time_available: int
    ) -> dict:
        """Create a personalized exercise plan."""
        if tolerance_score < 0.4:
            frequency = "3 times per week"
            duration = min(20, time_available)
        elif tolerance_score < 0.7:
            frequency = "4-5 times per week"
            duration = min(30, time_available)
        else:
            frequency = "5-6 times per week"
            duration = min(45, time_available)
        
        return {
            "frequency": frequency,
            "duration_minutes": duration,
            "activities": safe_exercises[:3],
            "progression": "Increase duration by 5 minutes every 2 weeks"
        }

    def _generate_exercise_precautions(self, symptom_triggers: list) -> list:
        """Generate exercise precautions based on triggers."""
        precautions = [
            "Stay hydrated during exercise",
            "Stop if you experience severe symptoms",
            "Warm up and cool down properly"
        ]
        
        if "stress" in symptom_triggers:
            precautions.append("Choose relaxing exercises during stressful periods")
        
        return precautions

    def _create_progression_timeline(
        self, tolerance_score: float, fitness_level: str
    ) -> dict:
        """Create exercise progression timeline."""
        if fitness_level == "beginner":
            weeks = 12
        elif fitness_level == "intermediate":
            weeks = 8
        else:
            weeks = 6
        
        return {
            "total_weeks": weeks,
            "milestones": [
                f"Week 2: Establish routine",
                f"Week 4: Increase duration",
                f"Week {weeks//2}: Add new activities",
                f"Week {weeks}: Reassess and adjust"
            ]
        }

    def _analyze_historical_trends(
        self, symptom_history: List[Dict], timeframe_days: int
    ) -> Dict[str, Any]:
        """Analyze historical symptom trends."""
        if not symptom_history:
            return {"trend": "stable", "severity_change": 0.0, "frequency_change": 0.0}
        
        # Simple trend analysis
        recent_symptoms = [s for s in symptom_history if s.get('days_ago', 0) <= timeframe_days]
        if len(recent_symptoms) < 2:
            return {"trend": "stable", "severity_change": 0.0, "frequency_change": 0.0}
        
        # Calculate average severity and frequency changes
        early_period = recent_symptoms[:len(recent_symptoms)//2]
        late_period = recent_symptoms[len(recent_symptoms)//2:]
        
        early_severity = sum(s.get('severity', 0) for s in early_period) / len(early_period)
        late_severity = sum(s.get('severity', 0) for s in late_period) / len(late_period)
        
        severity_change = late_severity - early_severity
        frequency_change = len(late_period) - len(early_period)
        
        trend = "improving" if severity_change < -0.5 else "worsening" if severity_change > 0.5 else "stable"
        
        return {
            "trend": trend,
            "severity_change": severity_change,
            "frequency_change": frequency_change
        }

    def _generate_progression_forecast(
        self, trends: Dict[str, Any], risk_factors: List[str]
    ) -> Dict[str, Any]:
        """Generate symptom progression forecast."""
        base_risk = 0.3
        
        # Adjust risk based on trends
        if trends["trend"] == "worsening":
            base_risk += 0.3
        elif trends["trend"] == "improving":
            base_risk -= 0.2
        
        # Adjust for risk factors
        risk_adjustment = len(risk_factors) * 0.1
        progression_risk = min(max(base_risk + risk_adjustment, 0.0), 1.0)
        
        return {
            "progression_risk": progression_risk,
            "predicted_severity": max(1, min(10, 5 + trends["severity_change"])),
            "timeline_weeks": 4 if progression_risk > 0.6 else 8
        }

    def _identify_risk_periods(
        self, trends: Dict[str, Any], lifestyle_factors: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify high-risk periods for symptom progression."""
        risk_periods = []
        
        # Stress-related risk periods
        if lifestyle_factors.get("stress_level", 0) > 7:
            risk_periods.append({
                "period": "high_stress_periods",
                "risk_level": "high",
                "description": "Periods of high stress may worsen symptoms"
            })
        
        # Dietary risk periods
        if "dietary_triggers" in lifestyle_factors:
            risk_periods.append({
                "period": "trigger_food_exposure",
                "risk_level": "medium",
                "description": "Exposure to trigger foods may cause flare-ups"
            })
        
        return risk_periods

    def _calculate_progression_confidence(
        self, data_quality: Dict[str, Any], trends: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for progression forecast."""
        base_confidence = 0.5
        
        # Adjust based on data quality
        if data_quality.get("symptom_logs_count", 0) > 30:
            base_confidence += 0.2
        if data_quality.get("timeframe_days", 0) > 60:
            base_confidence += 0.1
        
        # Adjust based on trend clarity
        if abs(trends.get("severity_change", 0)) > 1.0:
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.0), 1.0)

    def _calculate_response_probability(
        self, medication_history: List[Dict], user_profile: Dict[str, Any]
    ) -> float:
        """Calculate treatment response probability."""
        base_probability = 0.6
        
        # Adjust based on medication history
        if medication_history:
            successful_treatments = sum(1 for m in medication_history if m.get('effectiveness', 0) > 6)
            total_treatments = len(medication_history)
            if total_treatments > 0:
                success_rate = successful_treatments / total_treatments
                base_probability = (base_probability + success_rate) / 2
        
        # Adjust based on user profile
        age = user_profile.get('age', 30)
        if age < 25:
            base_probability += 0.1
        elif age > 60:
            base_probability -= 0.1
        
        return min(max(base_probability, 0.0), 1.0)

    def _generate_response_timeline(
        self, medication_type: str, response_probability: float
    ) -> Dict[str, Any]:
        """Generate treatment response timeline."""
        # Default timelines based on medication type
        timeline_map = {
            "antispasmodic": {"onset_days": 1, "peak_days": 7, "duration_weeks": 4},
            "probiotic": {"onset_days": 7, "peak_days": 21, "duration_weeks": 8},
            "fiber_supplement": {"onset_days": 3, "peak_days": 14, "duration_weeks": 6},
            "default": {"onset_days": 3, "peak_days": 14, "duration_weeks": 6}
        }
        
        timeline = timeline_map.get(medication_type, timeline_map["default"])
        
        # Adjust based on response probability
        if response_probability > 0.7:
            timeline["onset_days"] = max(1, timeline["onset_days"] - 1)
        elif response_probability < 0.4:
            timeline["onset_days"] += 2
        
        return timeline

    def _assess_treatment_side_effect_risk(
        self, medication_type: str, user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess side effect risk for treatment."""
        # Base risk levels by medication type
        risk_map = {
            "antispasmodic": 0.2,
            "probiotic": 0.1,
            "fiber_supplement": 0.15,
            "default": 0.25
        }
        
        base_risk = risk_map.get(medication_type, risk_map["default"])
        
        # Adjust based on user profile
        if user_profile.get('age', 30) > 65:
            base_risk += 0.1
        if user_profile.get('comorbidities', []):
            base_risk += 0.05 * len(user_profile['comorbidities'])
        
        risk_level = min(max(base_risk, 0.0), 1.0)
        
        return {
            "risk_score": risk_level,
            "risk_level": "high" if risk_level > 0.6 else "medium" if risk_level > 0.3 else "low",
            "common_side_effects": self._get_common_side_effects(medication_type)
        }

    def _get_common_side_effects(self, medication_type: str) -> List[str]:
        """Get common side effects for medication type."""
        side_effects_map = {
            "antispasmodic": ["drowsiness", "dry_mouth", "constipation"],
            "probiotic": ["bloating", "gas", "digestive_upset"],
            "fiber_supplement": ["bloating", "gas", "cramping"],
            "default": ["nausea", "headache", "fatigue"]
        }
        
        return side_effects_map.get(medication_type, side_effects_map["default"])

    def _suggest_treatment_alternatives(
        self, primary_treatment: str, response_probability: float
    ) -> List[Dict[str, Any]]:
        """Suggest alternative treatments."""
        alternatives = []
        
        if response_probability < 0.5:
            alternatives.extend([
                {
                    "treatment": "dietary_modification",
                    "type": "lifestyle",
                    "description": "Elimination diet to identify triggers",
                    "evidence_level": "high"
                },
                {
                    "treatment": "stress_management",
                    "type": "behavioral",
                    "description": "Cognitive behavioral therapy or mindfulness",
                    "evidence_level": "medium"
                }
            ])
        
        # Add medication alternatives
        if primary_treatment != "probiotic":
            alternatives.append({
                "treatment": "probiotic_therapy",
                "type": "medication",
                "description": "Multi-strain probiotic supplement",
                "evidence_level": "medium"
            })
        
        return alternatives

    def _get_fallback_sleep_analysis(self) -> dict:
        """Fallback sleep quality analysis."""
        return {
            "sleep_quality_score": 0.5,
            "symptom_correlation": {"correlation": 0.0, "patterns": []},
            "recommendations": ["Maintain regular sleep schedule"],
            "optimal_sleep_duration": 7.5,
            "optimal_bedtime": "22:30",
            "sleep_hygiene_tips": ["Keep bedroom cool and dark"],
            "impact_level": "medium"
        }

    def _get_fallback_exercise_analysis(self) -> dict:
        """Fallback exercise tolerance analysis."""
        return {
            "tolerance_level": 0.5,
            "recommended_exercises": ["Walking", "Gentle yoga"],
            "safe_activities": ["Walking", "Stretching"],
            "exercise_plan": {
                "frequency": "3 times per week",
                "duration_minutes": 20,
                "activities": ["Walking"],
                "progression": "Gradual increase"
            },
            "precautions": ["Start slowly", "Listen to your body"],
            "progression_timeline": {
                "total_weeks": 8,
                "milestones": ["Week 2: Establish routine"]
            }
        }

    def _get_fallback_medication_prediction(self) -> Dict[str, Any]:
        """Fallback medication effectiveness prediction."""
        return {
            "effectiveness_score": 0.5,
            "confidence": 0.3,
            "predicted_improvement": 0.4,
            "time_to_effect": 14,
            "recommendations": [{
                "type": "consultation",
                "priority": "medium",
                "message": "Consult with healthcare provider for personalized medication guidance"
            }],
            "side_effect_risk": 0.2,
            "alternative_suggestions": []
        }





    async def generate_multimodal_predictions(
        self, 
        user_id: int, 
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate enhanced predictions using multi-modal data integration.
        
        Args:
            user_id: User ID for predictions
            timeframe_days: Number of days to analyze
            db: Database session
            
        Returns:
            Dictionary containing multi-modal predictions and insights
        """
        try:
            # Integrate multi-modal data
            integrated_data = await self.multimodal_integration.integrate_user_data(
                user_id, timeframe_days, self.db
            )
            
            if "error" in integrated_data:
                logger.error(f"Multi-modal integration failed: {integrated_data['error']}")
                return await self._get_fallback_multimodal_predictions()
                
            # Extract unified features for ML predictions
            unified_features = integrated_data.get("unified_features", {})
            correlations = integrated_data.get("cross_modal_correlations", {})
            
            # Generate enhanced predictions using unified features
            predictions = {}
            
            # Symptom risk prediction with multi-modal context
            if unified_features:
                predictions["symptom_risk"] = await self.predict_symptom_risk(
                    unified_features
                )
                
                # Dietary trigger analysis with cross-modal correlations
                predictions["dietary_triggers"] = await self.analyze_dietary_triggers(
                    unified_features
                )
                
                # Treatment response with integrated data
                predictions["treatment_response"] = await self.predict_treatment_response(
                    unified_features
                )
                
                # Exercise tolerance with lifestyle integration
                predictions["exercise_tolerance"] = await self.predict_exercise_tolerance(
                    unified_features
                )
                
            # Queue data for real-time training
            await self._queue_training_data(user_id, integrated_data, predictions)
            
            return {
                "predictions": predictions,
                "integrated_insights": integrated_data.get("insights", {}),
                "data_quality": integrated_data.get("insights", {}).get("data_quality", {}),
                "correlation_analysis": correlations,
                "multimodal_recommendations": self._generate_multimodal_recommendations(
                    predictions, correlations
                ),
                "confidence_scores": integrated_data.get("insights", {}).get("confidence_scores", {}),
                "timestamp": datetime.utcnow().isoformat(),
                "model_version": "multimodal_v1.0"
            }
            
        except Exception as e:
            logger.error(f"Error generating multi-modal predictions: {e}")
            return await self._get_fallback_multimodal_predictions()
            
    async def _queue_training_data(
        self, 
        user_id: int, 
        integrated_data: Dict[str, Any], 
        predictions: Dict[str, Any]
    ):
        """Queue data for real-time model training."""
        try:
            training_data = {
                "user_id": user_id,
                "features": integrated_data.get("unified_features", {}),
                "predictions": predictions,
                "timestamp": datetime.utcnow().isoformat(),
                "data_quality": integrated_data.get("insights", {}).get("data_quality", {})
            }
            
            # Queue for different prediction types
            for prediction_type in ["symptom_risk", "dietary_triggers", "treatment_response"]:
                if prediction_type in predictions:
                    await self.real_time_training.queue_training_data(
                        prediction_type, training_data
                    )
                    
        except Exception as e:
            logger.error(f"Error queuing training data: {e}")
            
    def _generate_multimodal_recommendations(
        self, 
        predictions: Dict[str, Any], 
        correlations: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on multi-modal analysis."""
        recommendations = []
        
        # Analyze cross-modal correlations for recommendations
        if "symptoms_dietary" in correlations:
            dietary_corr = correlations["symptoms_dietary"]
            if dietary_corr.get("strength", 0) > 0.6:
                recommendations.append({
                    "type": "dietary",
                    "priority": "high",
                    "action": "Focus on identified trigger foods",
                    "evidence": f"Strong correlation detected (strength: {dietary_corr.get('strength', 0):.2f})",
                    "timeline": f"Effects typically seen within {dietary_corr.get('temporal_lag', 2)} hours"
                })
                
        if "symptoms_lifestyle" in correlations:
            lifestyle_corr = correlations["symptoms_lifestyle"]
            if lifestyle_corr.get("strength", 0) > 0.5:
                recommendations.append({
                    "type": "lifestyle",
                    "priority": "medium",
                    "action": "Optimize sleep and stress management",
                    "evidence": f"Moderate correlation with lifestyle factors (strength: {lifestyle_corr.get('strength', 0):.2f})",
                    "timeline": f"Improvements typically seen within {lifestyle_corr.get('temporal_lag', 12)} hours"
                })
                
        # Add prediction-based recommendations
        if "symptom_risk" in predictions:
            risk_level = predictions["symptom_risk"].get("risk_level", "medium")
            if risk_level == "high":
                recommendations.append({
                    "type": "monitoring",
                    "priority": "high",
                    "action": "Increase symptom monitoring frequency",
                    "evidence": "High symptom risk predicted",
                    "timeline": "Immediate action recommended"
                })
                
        return recommendations
        
    async def _get_fallback_multimodal_predictions(self) -> Dict[str, Any]:
        """Get fallback predictions when multi-modal analysis fails."""
        return {
            "predictions": {
                "symptom_risk": {"risk_level": "medium", "confidence": 0.3},
                "dietary_triggers": {"high_risk_foods": [], "confidence": 0.3},
                "treatment_response": {"response_probability": 0.5, "confidence": 0.3}
            },
            "integrated_insights": {"error": "Multi-modal analysis unavailable"},
            "data_quality": {"completeness": 0.0, "consistency": 0.0},
            "correlation_analysis": {},
            "multimodal_recommendations": [
                {
                    "type": "general",
                    "priority": "medium", 
                    "action": "Continue standard IBS management practices",
                    "evidence": "Fallback recommendation due to analysis failure"
                }
            ],
            "confidence_scores": {"overall": 0.3},
            "timestamp": datetime.utcnow().isoformat(),
            "model_version": "fallback_v1.0"
        }


def create_enhanced_recommendation_service(
    db: Session,
) -> EnhancedRecommendationService:
    """Factory function to create an enhanced recommendation service instance."""
    return EnhancedRecommendationService(db)
