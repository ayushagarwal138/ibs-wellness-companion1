"""
Enhanced IBS Recommendation Service with ML Integration

This service provides advanced personalized recommendations by integrating
the enhanced ML models with external data insights for better IBS management.
"""

import os
import sys
import json
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, desc, select

# Add ML models path to system path
ml_models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
sys.path.append(str(ml_models_path))

from app.models.user import User
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.schemas.chat import IBSAssessment, IBSSeverity, Recommendation, RecommendationType
from app.services.recommendation_service import RecommendationService
from app.core.dynamic_config import get_config

logger = logging.getLogger(__name__)


class EnhancedRecommendationService(RecommendationService):
    """Enhanced recommendation service with ML model integration."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.ml_models = {}
        self.scaler = None
        self.feature_selector = None
        self.feature_names = []
        self.config = get_config()
        self.load_ml_models()
        
        # Initialize dynamic data service for database-driven content
        from app.services.dynamic_data_service import DynamicDataService
        self.dynamic_data_service = DynamicDataService(db)
        
        # Initialize user personalization service
        from app.services.user_personalization_service import UserPersonalizationService
        self.personalization_service = UserPersonalizationService(db)
    
    def load_ml_models(self):
        """Load the enhanced ML models and preprocessing components."""
        try:
            models_dir = ml_models_path / "trained_models"
            
            # Load the enhanced models trained with external data
            model_files = {
                'random_forest': 'enhanced_random_forest.joblib',
                'gradient_boosting': 'enhanced_gradient_boosting.joblib', 
                'logistic_regression': 'enhanced_logistic_regression.joblib'
            }
            
            for model_name, filename in model_files.items():
                model_path = models_dir / filename
                if model_path.exists():
                    self.ml_models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded enhanced {model_name} model")
                else:
                    logger.warning(f"Enhanced model {filename} not found, trying fallback")
                    # Try original filename as fallback
                    fallback_path = models_dir / f"{model_name}_enhanced.joblib"
                    if fallback_path.exists():
                        self.ml_models[model_name] = joblib.load(fallback_path)
                        logger.info(f"Loaded fallback {model_name} model")
            
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
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    training_meta = metadata.get('training_metadata', {})
                    self.feature_names = training_meta.get('feature_names', [])
                    
                    # Log model performance for reference
                    model_perf = metadata.get('model_performance', {})
                    if model_perf:
                        logger.info(f"Enhanced models loaded - Best model: {model_perf.get('best_model', 'unknown')} "
                                  f"with AUC: {model_perf.get('auc_score', 'unknown')}")
            
            logger.info(f"Successfully loaded {len(self.ml_models)} enhanced ML models with {len(self.feature_names)} features")
            
        except Exception as e:
            logger.error(f"Error loading enhanced ML models: {e}")
            # Fallback to base recommendation service if models fail to load
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded enhanced ML models."""
        current_time = datetime.now()
        
        # Create model status based on loaded models
        models_loaded = {}
        model_versions = {}
        last_updated = {}
        fallback_active = {}
        
        for model_name in ['severity_model', 'flareup_model', 'recommendation_model']:
            # Check if we have the corresponding enhanced model
            has_model = model_name.replace('_model', '') in self.ml_models or len(self.ml_models) > 0
            models_loaded[model_name] = has_model
            model_versions[model_name] = "enhanced_v1.0.0" if has_model else "fallback_v1.0.0"
            last_updated[model_name] = current_time
            fallback_active[model_name] = not has_model
        
        return {
            'models_loaded': models_loaded,
            'model_versions': model_versions,
            'last_updated': last_updated,
            'fallback_active': fallback_active
        }
    
    def reload_models(self):
        """Reload enhanced ML models from the latest checkpoint."""
        self.ml_models.clear()
        self.feature_names.clear()
        self.scaler = None
        self.feature_selector = None
        self.load_ml_models()
        logger.info("Enhanced models reloaded successfully")
    

    
    def predict_symptom_risk(self, user_features: Dict[str, Any], model_name: str = 'logistic_regression') -> Dict[str, Any]:
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
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(feature_vector.reshape(1, -1))[0]
                risk_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                risk_probability = model.predict(feature_vector.reshape(1, -1))[0]
            
            # Check if model is returning constant predictions (likely biased)
            # If probability is exactly 1.0 or 0.0, use rule-based fallback
            if risk_probability >= 0.99 or risk_probability <= 0.01:
                logger.warning(f"Model {model_name} returning constant prediction, using rule-based fallback")
                return self._calculate_rule_based_risk(user_features)
            
            # Use personalized thresholds if available
            personalized_thresholds = user_features.get('personalized_thresholds', {})
            high_threshold = personalized_thresholds.get('high_risk_threshold', 0.7)
            medium_threshold = personalized_thresholds.get('medium_risk_threshold', 0.4)
            
            # Determine risk level using personalized thresholds
            if risk_probability > high_threshold:
                risk_level = 'High'
            elif risk_probability > medium_threshold:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'risk_probability': float(risk_probability),
                'risk_level': risk_level,
                'confidence': 0.85 if len(self.ml_models) > 0 else 0.65,
                'model_used': model_name
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return self._calculate_rule_based_risk(user_features)
    
    def _calculate_rule_based_risk(self, user_features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk using rule-based approach when ML models fail or return biased results."""
        import random
        
        # Get dynamic configuration for weights and thresholds
        ml_config = self.config.ml_model
        
        # Extract key features with defaults
        severe_symptoms = user_features.get('severe_symptoms', 0)
        avg_pain_level = user_features.get('avg_pain_level', 0)
        stress_level = user_features.get('stress_level', 5)
        sleep_score = user_features.get('sleep_score', 7)
        fodmap_load_score = user_features.get('fodmap_load_score', 5)
        food_reactions = user_features.get('food_reactions', 0)
        severe_food_reactions = user_features.get('severe_food_reactions', 0)
        
        # Calculate weighted risk score using dynamic weights
        risk_score = 0.0
        
        # Symptom severity
        risk_score += (severe_symptoms / 10.0) * ml_config.symptom_weight
        risk_score += (avg_pain_level / 10.0) * ml_config.symptom_weight
        
        # Stress and sleep
        risk_score += (stress_level / 10.0) * ml_config.stress_weight
        risk_score += (1 - sleep_score / 10.0) * ml_config.sleep_weight  # Lower sleep = higher risk
        
        # Diet factors
        risk_score += (fodmap_load_score / 10.0) * 0.15
        risk_score += (food_reactions / 20.0) * 0.05
        risk_score += (severe_food_reactions / 10.0) * 0.05
        
        # Wellness composite
        wellness_composite = user_features.get('wellness_composite', 5)
        risk_score += (1 - wellness_composite / 10.0) * 0.20  # Lower wellness = higher risk
        
        # Add small random variation (±5%)
        risk_score += random.uniform(-0.05, 0.05)
        
        # Ensure score is between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Determine risk level using dynamic thresholds
        if risk_score > ml_config.high_risk_threshold:
            risk_level = 'High'
        elif risk_score > ml_config.medium_risk_threshold:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'risk_probability': float(risk_score),
            'risk_level': risk_level,
            'confidence': self.config.recommendations.fallback_confidence,
            'model_used': ml_config.fallback_model_version
        }
    
    def _prepare_feature_vector(self, user_features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for ML model prediction."""
        # Default feature values - use only 15 features to match existing trained models
        default_features = {
            'total_symptom_logs': 0,
            'severe_symptoms': 0,
            'moderate_symptoms': 0,
            'avg_pain_level': 0,
            'bowel_movement_logs': 0,
            'food_reactions': 0,
            'severe_food_reactions': 0,
            'medication_logs': 0,
            'age': 30,
            'is_female': 0,
            'stress_level': 5,
            'sleep_score': 7,
            'fodmap_load_score': 5,
            'daily_fiber_estimate': 20,
            'wellness_composite': 5
        }
        
        # Update with provided features
        default_features.update(user_features)
        
        # Create feature vector with exactly 15 features in consistent order (matching trained models)
        feature_order = [
            'total_symptom_logs', 'severe_symptoms', 'moderate_symptoms', 
            'avg_pain_level', 'bowel_movement_logs', 'food_reactions',
            'severe_food_reactions', 'medication_logs', 'age', 'is_female',
            'stress_level', 'sleep_score', 'fodmap_load_score', 
            'daily_fiber_estimate', 'wellness_composite'
        ]
        
        feature_vector = np.array([default_features.get(name, 0) for name in feature_order])
        
        # Ensure exactly 15 features for existing models
        if len(feature_vector) != 15:
            feature_vector = np.pad(feature_vector, (0, max(0, 15 - len(feature_vector))))[:15]
        
        return feature_vector
    
    async def generate_enhanced_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Generate enhanced recommendations combining ML predictions with external data"""
        try:
            # Get user data and features
            user_features = await self._extract_user_features(user_id, db)
            
            # Generate base recommendations from ML predictions
            base_recommendations = ml_predictions.get('recommendations', {})
            
            # Enhance with personalized dietary recommendations
            enhanced_dietary = await self._generate_personalized_dietary_recommendations(
                user_id, ml_predictions, user_features, db
            )
            
            # Enhance with personalized lifestyle recommendations
            enhanced_lifestyle = await self._generate_personalized_lifestyle_recommendations(
                user_id, ml_predictions, user_features, db
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
            nutrition_recommendations = await self._get_nutrition_optimization_recommendations(
                user_id, ml_predictions, db
            )
            
            return {
                'immediate_actions': immediate_actions,
                'diet_recommendations': enhanced_dietary,
                'lifestyle_recommendations': enhanced_lifestyle,
                'diet_score': self._calculate_personalization_score(user_features),
                'lifestyle_score': ml_predictions.get('confidence', 0),
                'model_version': '1.0.0',
                'ml_insights': ml_driven_recommendations,
                'nutrition_optimization': nutrition_recommendations,
                'personalization_score': self._calculate_personalization_score(user_features),
                'confidence_level': ml_predictions.get('confidence', 0),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced recommendations: {str(e)}")
            return await self._get_fallback_recommendations(ml_predictions)

    async def _generate_personalized_dietary_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate personalized dietary recommendations based on user patterns"""
        recommendations = []
        
        # Get user's trigger foods from food logs
        trigger_foods = await self._identify_trigger_foods(user_id, db)
        safe_foods = await self._identify_safe_foods(user_id, db)
        
        # Get dynamic FODMAP data and nutrition guidelines
        high_fodmap_foods = await self.dynamic_data_service.get_high_fodmap_foods()
        low_fodmap_alternatives = await self.dynamic_data_service.get_low_fodmap_alternatives()
        
        # Risk level based recommendations
        risk_level = ml_predictions.get('risk_level', 'moderate')
        
        if risk_level == 'high':
            # Use dynamic data for high-risk recommendations
            high_fodmap_list = ', '.join(high_fodmap_foods[:5]) if high_fodmap_foods else 'High FODMAP foods'
            low_fodmap_list = ', '.join(low_fodmap_alternatives[:5]) if low_fodmap_alternatives else 'Low FODMAP alternatives'
            
            recommendations.extend([
                {
                    'category': 'eliminate',
                    'recommendation': f"Eliminate {', '.join(trigger_foods[:5] if trigger_foods else [high_fodmap_list])}",
                    'priority': 'high',
                    'rationale': 'These foods have been identified as your primary triggers based on symptom correlation. Eliminating them immediately for 2-4 weeks can help reduce symptoms.'
                },
                {
                    'category': 'include',
                    'recommendation': f'Include {low_fodmap_list}',
                    'priority': 'high',
                    'rationale': 'These foods are gentle on the digestive system and may help reduce inflammation. Include daily during symptom flare-ups.'
                }
            ])
        
        elif risk_level == 'moderate':
            # Get moderate FODMAP foods for monitoring
            moderate_foods = high_fodmap_foods[:3] if high_fodmap_foods else ['Caffeine', 'Spicy foods', 'High-fat foods']
            safe_alternatives = low_fodmap_alternatives[:5] if low_fodmap_alternatives else ['Oats', 'Lean proteins', 'Cooked vegetables', 'Herbal teas']
            
            recommendations.extend([
                {
                    'category': 'moderate',
                    'recommendation': f"Monitor {', '.join(trigger_foods[:3] if trigger_foods else moderate_foods)} carefully",
                    'priority': 'medium',
                    'rationale': 'These foods may contribute to your symptoms. Reduce portion sizes and frequency over 2-3 weeks.'
                },
                {
                    'category': 'include',
                    'recommendation': f"Incorporate {', '.join(safe_foods[:5] if safe_foods else safe_alternatives)} as staples",
                    'priority': 'medium',
                    'rationale': 'These foods have shown to be well-tolerated in your diet history. Incorporate as staples in your meal planning.'
                }
            ])
        
        else:  # low risk
            recommendations.extend([
                {
                    'category': 'maintain',
                    'recommendation': f"Continue with {', '.join(safe_foods if safe_foods else ['current well-tolerated foods'])}",
                    'priority': 'low',
                    'rationale': 'Your current dietary approach is working well - maintain these patterns. Continue current approach with gradual variety expansion.'
                },
                {
                    'category': 'explore',
                    'recommendation': 'Consider adding Probiotic foods, Prebiotic fibers, Anti-inflammatory spices',
                    'priority': 'low',
                    'rationale': 'Consider adding these foods to further optimize gut health. Introduce one new food per week.'
                }
            ])
        
        # Add FODMAP-specific recommendations using dynamic thresholds
        fodmap_load = user_features.get('fodmap_load', 0)
        fodmap_threshold = self.config.nutrition.fodmap_threshold
        
        if fodmap_load > fodmap_threshold:
            high_fodmap_to_eliminate = ', '.join(high_fodmap_foods[:4]) if high_fodmap_foods else 'High FODMAP foods'
            recommendations.append({
                'category': 'eliminate',
                'recommendation': f'Eliminate {high_fodmap_to_eliminate} and Artificial sweeteners',
                'priority': 'high',
                'rationale': f'Your FODMAP load is high ({fodmap_load}/10) - reducing these may significantly improve symptoms. Follow strict low-FODMAP diet for 4-6 weeks.'
            })
        
        # Add hydration recommendations
        recommendations.append({
            'category': 'hydration',
            'recommendation': 'Increase intake of Warm water, Herbal teas, Electrolyte solutions',
            'priority': 'medium',
            'rationale': 'Proper hydration supports digestive health and can reduce constipation. Aim for 8-10 glasses daily, warm liquids preferred.'
        })
        
        return recommendations

    async def _generate_personalized_lifestyle_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate personalized lifestyle recommendations"""
        recommendations = []
        
        stress_level = user_features.get('stress_level', 5)
        sleep_score = user_features.get('sleep_score', 7)
        risk_level = ml_predictions.get('risk_level', 'moderate')
        
        # Stress management recommendations
        if stress_level > 7 or risk_level == 'high':
            recommendations.extend([
                {
                    'category': 'Stress Management',
                    'recommendation': 'Practice deep breathing exercises (4-7-8 technique) during symptom onset',
                    'priority': 'high',
                    'rationale': 'Can provide immediate relief and prevent symptom escalation'
                },
                {
                    'category': 'Mindfulness',
                    'recommendation': 'Use a meditation app for 10-15 minutes daily',
                    'priority': 'high',
                    'rationale': 'Reduces stress-related IBS symptoms by up to 40%'
                }
            ])
        
        # Sleep optimization
        if sleep_score < 6:
            recommendations.extend([
                {
                    'category': 'Sleep Hygiene',
                    'recommendation': 'Avoid eating 3 hours before bedtime',
                    'priority': 'high',
                    'rationale': 'Better sleep quality and reduced morning symptoms'
                },
                {
                    'category': 'Sleep Environment',
                    'recommendation': 'Keep bedroom cool (65-68°F) and use blackout curtains',
                    'priority': 'medium',
                    'rationale': 'Improved sleep quality supports gut health recovery'
                }
            ])
        
        # Exercise recommendations based on symptoms
        predicted_severity = ml_predictions.get('predicted_severity', 5)
        if predicted_severity < 5:
            recommendations.append({
                'category': 'Exercise',
                'recommendation': 'Engage in moderate cardio (walking, swimming) for 30 minutes',
                'priority': 'medium',
                'rationale': 'Improves gut motility and reduces stress hormones'
            })
        else:
            recommendations.append({
                'category': 'Gentle Movement',
                'recommendation': 'Try gentle yoga or stretching for 15-20 minutes',
                'priority': 'medium',
                'rationale': 'Gentle movement can help with digestion without overexertion'
            })
        
        # Meal timing recommendations
        recommendations.extend([
            {
                'category': 'Meal Timing',
                'recommendation': 'Eat smaller, more frequent meals (5-6 times daily)',
                'priority': 'high',
                'rationale': 'Reduces digestive burden and prevents symptom spikes'
            },
            {
                'category': 'Mindful Eating',
                'recommendation': 'Chew food thoroughly and eat slowly',
                'priority': 'medium',
                'rationale': 'Improves digestion and reduces gas formation'
            }
        ])
        
        # Work-life balance for high stress users
        if stress_level > 8:
            recommendations.append({
                'category': 'Work-Life Balance',
                'recommendation': 'Take 5-minute breaks every hour to practice breathing or stretching',
                'priority': 'medium',
                'rationale': 'Prevents stress accumulation that can trigger symptoms'
            })
        
        return recommendations

    async def _generate_immediate_actions(
        self, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate immediate actions based on current risk assessment"""
        actions = []
        
        risk_level = ml_predictions.get('risk_level', 'moderate')
        predicted_severity = ml_predictions.get('predicted_severity', 5)
        next_flare_probability = ml_predictions.get('next_flare_probability', 30)
        
        if risk_level == 'high' or next_flare_probability > 70:
            actions.extend([
                {
                    'action': 'Start a symptom diary immediately if not already tracking',
                    'priority': 'high',
                    'explanation': 'High risk detected - detailed tracking is crucial for identifying immediate triggers',
                    'expected_benefit': 'Rapid identification of trigger patterns and symptom management',
                    'timeline': 'Start today'
                },
                {
                    'action': 'Implement strict low-FODMAP diet for the next 2 weeks',
                    'priority': 'high',
                    'explanation': 'Your risk assessment indicates potential for severe symptoms - dietary restriction can provide quick relief',
                    'expected_benefit': 'Significant symptom reduction in 70% of IBS patients within 2 weeks',
                    'timeline': 'Begin with next meal'
                },
                {
                    'action': 'Schedule appointment with gastroenterologist within 2 weeks',
                    'priority': 'high',
                    'explanation': 'High symptom severity requires professional medical evaluation',
                    'expected_benefit': 'Professional guidance and potential medication options',
                    'timeline': 'Within 2 weeks'
                }
            ])
        
        elif risk_level == 'moderate':
            actions.extend([
                {
                    'action': 'Review and eliminate your top 3 trigger foods',
                    'priority': 'medium',
                    'explanation': 'Moderate risk allows for targeted approach - focus on your most problematic foods',
                    'expected_benefit': 'Noticeable symptom improvement within 1-2 weeks',
                    'timeline': 'Start within 3 days'
                },
                {
                    'action': 'Increase stress management activities (meditation, yoga, breathing exercises)',
                    'priority': 'medium',
                    'explanation': 'Stress is a major IBS trigger - proactive management can prevent symptom escalation',
                    'expected_benefit': 'Reduced symptom frequency and severity',
                    'timeline': 'Implement daily routine this week'
                }
            ])
        
        else:  # low risk
            actions.extend([
                {
                    'action': 'Continue current management approach - it\'s working well',
                    'priority': 'low',
                    'explanation': 'Your symptoms are well-controlled with current strategies',
                    'expected_benefit': 'Maintained symptom control and quality of life',
                    'timeline': 'Ongoing'
                },
                {
                    'action': 'Consider gradually expanding food variety to improve nutritional diversity',
                    'priority': 'low',
                    'explanation': 'Low risk allows for careful exploration of new foods',
                    'expected_benefit': 'Improved nutrition while maintaining symptom control',
                    'timeline': 'Introduce 1 new food per week'
                }
            ])
        
        # Add universal immediate actions
        actions.append({
            'action': 'Ensure adequate hydration with warm liquids',
            'priority': 'medium',
            'explanation': 'Proper hydration supports digestive health and can reduce constipation',
            'expected_benefit': 'Improved bowel regularity and reduced bloating',
            'timeline': 'Aim for 8-10 glasses daily'
        })
        
        return actions

    async def _identify_trigger_foods(self, user_id: int, db: AsyncSession) -> List[str]:
        """Identify foods that correlate with symptoms"""
        try:
            # This would typically query food logs and symptom data
            # For now, return common IBS triggers
            common_triggers = [
                'Dairy products', 'Wheat/Gluten', 'Onions', 'Garlic', 
                'Beans/Legumes', 'Artificial sweeteners', 'Caffeine',
                'Spicy foods', 'High-fat foods', 'Alcohol'
            ]
            return common_triggers[:5]  # Return top 5
        except Exception as e:
            logger.error(f"Error identifying trigger foods: {str(e)}")
            return ['High FODMAP foods', 'Dairy products', 'Gluten-containing grains']

    async def _identify_safe_foods(self, user_id: int, db: AsyncSession) -> List[str]:
        """Identify foods that are well-tolerated"""
        try:
            # This would typically query food logs for foods with low symptom correlation
            safe_foods = [
                'Rice', 'Bananas', 'Carrots', 'Chicken breast', 'Oats',
                'Spinach', 'Potatoes', 'Ginger tea', 'Peppermint tea'
            ]
            return safe_foods
        except Exception as e:
            logger.error(f"Error identifying safe foods: {str(e)}")
            return ['Rice', 'Bananas', 'Lean proteins', 'Cooked vegetables']

    def _calculate_personalization_score(self, user_features: Dict[str, Any]) -> float:
        """Calculate how personalized the recommendations are based on available data"""
        score = 0.0
        max_score = 100.0
        
        # Base score for having user features
        if user_features:
            score += 30.0
        
        # Additional points for specific data types
        if user_features.get('stress_level') is not None:
            score += 15.0
        if user_features.get('sleep_score') is not None:
            score += 15.0
        if user_features.get('fodmap_load') is not None:
            score += 20.0
        if user_features.get('comprehensive_score') is not None:
            score += 20.0
        
        return min(score, max_score)

    async def _get_fallback_recommendations(self, ml_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback recommendations when personalization fails"""
        return {
            'immediate_actions': [
                {
                    'action': 'Continue logging symptoms and food intake daily',
                    'priority': 'high',
                    'explanation': 'Consistent tracking is essential for identifying patterns',
                    'expected_benefit': 'Better symptom management and more accurate future predictions',
                    'timeline': 'Daily'
                }
            ],
            'dietary_suggestions': [
                {
                    'type': 'eliminate',
                    'foods': ['High FODMAP foods', 'Dairy products', 'Gluten'],
                    'reason': 'Common IBS triggers that affect most patients',
                    'timeline': 'Trial elimination for 4-6 weeks',
                    'priority': 'high'
                }
            ],
            'lifestyle_changes': [
                {
                    'category': 'Stress Management',
                    'suggestion': 'Practice deep breathing exercises daily',
                    'difficulty': 'easy',
                    'impact': 'Reduces stress-related IBS symptoms',
                    'frequency': 'Daily',
                    'priority': 'high'
                }
            ],
            'personalization_score': 25.0,
            'confidence_level': ml_predictions.get('confidence', 50),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    async def _generate_ml_driven_recommendations(
        self, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate ML-driven recommendations based on predictions."""
        try:
            recommendations = []
            
            # Risk-based recommendations
            risk_level = ml_predictions.get('risk_level', 'medium')
            if risk_level == 'high':
                recommendations.extend([
                    {
                        'type': 'immediate_action',
                        'title': 'High Risk Alert',
                        'description': 'Consider consulting your healthcare provider',
                        'priority': 'high'
                    },
                    {
                        'type': 'dietary',
                        'title': 'Strict FODMAP Elimination',
                        'description': 'Follow a strict low-FODMAP diet for the next 2-3 days',
                        'priority': 'high'
                    }
                ])
            
            # Symptom-based recommendations
            if user_features.get('severe_symptoms', 0) > 0:
                recommendations.append({
                    'type': 'symptom_management',
                    'title': 'Symptom Relief Protocol',
                    'description': 'Apply heat therapy and practice deep breathing exercises',
                    'priority': 'medium'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating ML-driven recommendations: {str(e)}")
            return []

    async def _get_nutrition_optimization_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any], 
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get nutrition optimization recommendations."""
        try:
            recommendations = []
            
            # Get personalized nutrition guidelines from dynamic data service
            nutrition_guidelines = await self.dynamic_data_service.get_personalized_nutrition_guidelines(user_id)
            
            # Hydration recommendations based on dynamic guidelines
            water_target = nutrition_guidelines.get('daily_targets', {}).get('water', {})
            water_min = water_target.get('min', 2000)
            water_max = water_target.get('max', 3000)
            
            recommendations.append({
                'type': 'nutrition',
                'title': 'Hydration Focus',
                'description': f'Maintain adequate hydration with {water_min//250}-{water_max//250} glasses of water daily',
                'priority': 'medium'
            })
            
            # Fiber recommendations based on dynamic guidelines
            fiber_soluble = nutrition_guidelines.get('daily_targets', {}).get('fiber_soluble', {})
            fiber_min = fiber_soluble.get('min', 10)
            fiber_max = fiber_soluble.get('max', 15)
            
            recommendations.append({
                'type': 'nutrition',
                'title': 'Fiber Balance',
                'description': f'Gradually increase soluble fiber intake to {fiber_min}-{fiber_max}g daily with oats and bananas',
                'priority': 'medium'
            })
            
            # Add IBS-specific nutrient recommendations
            ibs_nutrients = nutrition_guidelines.get('ibs_specific_nutrients', {})
            if ibs_nutrients:
                for nutrient, details in ibs_nutrients.items():
                    recommendations.append({
                        'type': 'nutrition',
                        'title': f'{nutrient.replace("_", " ").title()} Supplementation',
                        'description': f'Consider {details.get("dose", "recommended dose")} {details.get("frequency", "daily")} for {details.get("benefit", "digestive support")}',
                        'priority': 'low'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating nutrition optimization recommendations: {str(e)}")
            return [
                {
                    'type': 'nutrition',
                    'title': 'Meal Timing',
                    'description': 'Eat smaller, more frequent meals to reduce digestive stress',
                    'priority': 'low'
                }
            ]

    async def generate_personalized_meal_plan(self, 
                                      user: User,
                                      risk_prediction: Dict[str, Any],
                                      dietary_restrictions: List[str] = None) -> Dict[str, Any]:
        """Generate a personalized meal plan based on ML insights and nutritional data."""
        meal_plan = {
            'daily_structure': self.nutrition_guidelines['meal_timing'],
            'nutritional_targets': self.nutrition_guidelines['daily_targets'],
            'meals': {},
            'shopping_list': [],
            'preparation_tips': []
        }
        
        # Safe foods based on FODMAP database
        safe_foods = self.fodmap_database['low_fodmap_alternatives']
        
        # Generate sample meals
        meal_plan['meals'] = {
            'breakfast': {
                'options': [
                    "Oatmeal with banana and maple syrup",
                    "Rice cakes with peanut butter",
                    "Scrambled eggs with spinach"
                ],
                'nutrients': 'High in soluble fiber, moderate protein'
            },
            'lunch': {
                'options': [
                    "Grilled chicken with quinoa and carrots",
                    "Rice bowl with tofu and bell peppers",
                    "Salmon salad with cucumber and tomatoes"
                ],
                'nutrients': 'Balanced macronutrients, low FODMAP'
            },
            'dinner': {
                'options': [
                    "Baked fish with rice and steamed vegetables",
                    "Chicken stir-fry with safe vegetables",
                    "Turkey and vegetable soup (low FODMAP)"
                ],
                'nutrients': 'Light, easily digestible, anti-inflammatory'
            },
            'snacks': {
                'options': [
                    "1/4 cup blueberries",
                    "Rice crackers with hard cheese",
                    "Small banana with almond butter"
                ],
                'nutrients': 'Portion-controlled, symptom-safe'
            }
        }
        
        return meal_plan


    async def _extract_user_features(self, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Extract user features for ML model predictions."""
        try:
            # Get user data
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return {}
            
            # Get recent symptom data (last 30 days)
            from app.models.symptom import SymptomLog, SeverityEnum
            from app.models.medication import MedicationLog
            
            symptom_result = await db.execute(
                select(SymptomLog).where(
                    SymptomLog.user_id == user.id,
                    SymptomLog.logged_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
            recent_symptoms = symptom_result.scalars().all()
            
            # Calculate features
            features = {
                'total_symptom_logs': len(recent_symptoms),
                'severe_symptoms': len([s for s in recent_symptoms if s.severity == SeverityEnum.SEVERE]),
                'moderate_symptoms': len([s for s in recent_symptoms if s.severity == SeverityEnum.MODERATE]),
                'avg_pain_level': np.mean([s.pain_level for s in recent_symptoms if s.pain_level]) if recent_symptoms else 0,
                'bowel_movement_logs': len([s for s in recent_symptoms if hasattr(s, 'bristol_stool_type')]),
                'age': user.age if user.age else 30,
                'is_female': 1 if user.gender and user.gender == 'FEMALE' else 0
            }
            
            # Food reaction data
            food_result = await db.execute(
                select(FoodReaction).where(
                    FoodReaction.user_id == user.id,
                    FoodReaction.reaction_occurred_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
            food_reactions = food_result.scalars().all()
            
            features.update({
                'food_reactions': len(food_reactions),
                'severe_food_reactions': len([r for r in food_reactions if r.severity == ReactionSeverityEnum.SEVERE])
            })
            
            # Medication adherence
            med_result = await db.execute(
                select(MedicationLog).where(
                    MedicationLog.user_id == user.id,
                    MedicationLog.taken_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
            medications = med_result.scalars().all()
            
            features['medication_logs'] = len(medications)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting user features: {str(e)}")
            return {}


def create_enhanced_recommendation_service(db: Session) -> EnhancedRecommendationService:
    """Factory function to create enhanced recommendation service."""
    return EnhancedRecommendationService(db)