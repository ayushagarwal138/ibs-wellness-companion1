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
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

# Add ML models path to system path
ml_models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
sys.path.append(str(ml_models_path))

from app.models.user import User
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.schemas.chat import IBSAssessment, IBSSeverity, Recommendation, RecommendationType
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class EnhancedRecommendationService(RecommendationService):
    """Enhanced recommendation service with ML model integration."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.ml_models = {}
        self.scaler = None
        self.feature_selector = None
        self.feature_names = []
        self.load_ml_models()
        
        # Enhanced FODMAP database with external data insights
        self.fodmap_database = self._load_enhanced_fodmap_data()
        
        # Nutritional guidelines based on external datasets
        self.nutrition_guidelines = self._load_nutrition_guidelines()
    
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
    
    def _load_enhanced_fodmap_data(self) -> Dict[str, Any]:
        """Load enhanced FODMAP data with external dataset insights."""
        return {
            'high_fodmap_foods': {
                'fruits': ['apple', 'pear', 'mango', 'watermelon', 'cherries'],
                'vegetables': ['onion', 'garlic', 'cauliflower', 'mushrooms', 'asparagus'],
                'grains': ['wheat', 'rye', 'barley'],
                'dairy': ['milk', 'yogurt', 'ice_cream'],
                'legumes': ['beans', 'lentils', 'chickpeas'],
                'sweeteners': ['honey', 'agave', 'sorbitol', 'mannitol']
            },
            'low_fodmap_alternatives': {
                'fruits': ['banana', 'blueberries', 'strawberries', 'orange', 'kiwi'],
                'vegetables': ['carrot', 'spinach', 'bell_pepper', 'cucumber', 'tomato'],
                'grains': ['rice', 'quinoa', 'oats', 'corn'],
                'dairy': ['lactose_free_milk', 'hard_cheese', 'butter'],
                'proteins': ['chicken', 'fish', 'eggs', 'tofu'],
                'sweeteners': ['maple_syrup', 'stevia', 'sugar']
            },
            'portion_guidelines': {
                'banana': '1 medium (100g)',
                'blueberries': '1/4 cup (40g)',
                'spinach': '1 cup (30g)',
                'rice': '1/2 cup cooked (75g)',
                'chicken': '3-4 oz (85-115g)'
            }
        }
    
    def _load_nutrition_guidelines(self) -> Dict[str, Any]:
        """Load nutrition guidelines based on external dataset analysis."""
        return {
            'daily_targets': {
                'fiber_soluble': {'min': 10, 'max': 15, 'unit': 'g'},
                'fiber_insoluble': {'min': 5, 'max': 10, 'unit': 'g'},
                'protein': {'min': 0.8, 'max': 1.2, 'unit': 'g/kg_body_weight'},
                'fat': {'min': 20, 'max': 35, 'unit': '% of calories'},
                'carbs': {'min': 45, 'max': 65, 'unit': '% of calories'},
                'water': {'min': 2000, 'max': 3000, 'unit': 'ml'}
            },
            'ibs_specific_nutrients': {
                'peppermint_oil': {'dose': '0.2-0.4ml', 'frequency': '3x daily', 'benefit': 'antispasmodic'},
                'probiotics': {'cfu': '10^9-10^11', 'strains': ['Bifidobacterium', 'Lactobacillus']},
                'omega3': {'dose': '1-2g', 'frequency': 'daily', 'benefit': 'anti-inflammatory'},
                'vitamin_d': {'dose': '1000-2000IU', 'frequency': 'daily', 'benefit': 'immune_support'}
            },
            'meal_timing': {
                'frequency': '4-6 small meals',
                'spacing': '2-3 hours apart',
                'last_meal': '3 hours before bed',
                'hydration': 'between meals, not during'
            }
        }
    
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
            return {'risk_probability': 0.5, 'risk_level': 'Medium', 'confidence': 'Low'}
        
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
            
            # Determine risk level
            if risk_probability > 0.7:
                risk_level = 'High'
            elif risk_probability > 0.4:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'risk_probability': float(risk_probability),
                'risk_level': risk_level,
                'confidence': 'High' if len(self.ml_models) > 0 else 'Medium',
                'model_used': model_name
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return {'risk_probability': 0.5, 'risk_level': 'Medium', 'confidence': 'Low'}
    
    def _prepare_feature_vector(self, user_features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for ML model prediction."""
        # Default feature values
        default_features = {
            'stress_level': 5,
            'sleep_score': 7,
            'fodmap_load_score': 5,
            'daily_fiber_estimate': 20,
            'daily_calories_estimate': 2000,
            'is_weekend': 0,
            'wellness_composite': 5,
            'flare_risk_score': 5,
            'severity_trend_3day': 5,
            'fiber_per_1000_cal': 10,
            'high_stress_poor_sleep': 0,
            'high_fodmap_day': 0,
            'adequate_fiber': 1,
            'severe_symptoms': 0
        }
        
        # Update with provided features
        default_features.update(user_features)
        
        # Create feature vector in the expected order
        if self.feature_names:
            feature_vector = np.array([default_features.get(name, 0) for name in self.feature_names])
        else:
            # Fallback to common features
            common_features = ['stress_level', 'sleep_score', 'fodmap_load_score', 'daily_fiber_estimate']
            feature_vector = np.array([default_features.get(name, 0) for name in common_features])
        
        return feature_vector
    
    async def generate_enhanced_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        db: Session
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
                'dietary_suggestions': enhanced_dietary,
                'lifestyle_changes': enhanced_lifestyle,
                'ml_insights': ml_driven_recommendations,
                'nutrition_optimization': nutrition_recommendations,
                'personalization_score': self._calculate_personalization_score(user_features),
                'confidence_level': ml_predictions.get('confidence', 0),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced recommendations: {str(e)}")
            return await self._get_fallback_recommendations(ml_predictions)

    async def _generate_personalized_dietary_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate personalized dietary recommendations based on user patterns"""
        recommendations = []
        
        # Get user's trigger foods from food logs
        trigger_foods = await self._identify_trigger_foods(user_id, db)
        safe_foods = await self._identify_safe_foods(user_id, db)
        
        # Risk level based recommendations
        risk_level = ml_predictions.get('risk_level', 'moderate')
        
        if risk_level == 'high':
            recommendations.extend([
                {
                    'type': 'eliminate',
                    'foods': trigger_foods[:5] if trigger_foods else ['High FODMAP foods', 'Dairy products', 'Gluten-containing grains'],
                    'reason': 'These foods have been identified as your primary triggers based on symptom correlation',
                    'timeline': 'Eliminate immediately for 2-4 weeks',
                    'priority': 'high'
                },
                {
                    'type': 'include',
                    'foods': ['Bone broth', 'Ginger tea', 'Peppermint tea', 'Rice', 'Bananas'],
                    'reason': 'These foods are gentle on the digestive system and may help reduce inflammation',
                    'timeline': 'Include daily during symptom flare-ups',
                    'priority': 'high'
                }
            ])
        
        elif risk_level == 'moderate':
            recommendations.extend([
                {
                    'type': 'moderate',
                    'foods': trigger_foods[:3] if trigger_foods else ['Caffeine', 'Spicy foods', 'High-fat foods'],
                    'reason': 'Monitor these foods carefully as they may contribute to your symptoms',
                    'timeline': 'Reduce portion sizes and frequency over 2-3 weeks',
                    'priority': 'medium'
                },
                {
                    'type': 'include',
                    'foods': safe_foods[:5] if safe_foods else ['Oats', 'Lean proteins', 'Cooked vegetables', 'Herbal teas'],
                    'reason': 'These foods have shown to be well-tolerated in your diet history',
                    'timeline': 'Incorporate as staples in your meal planning',
                    'priority': 'medium'
                }
            ])
        
        else:  # low risk
            recommendations.extend([
                {
                    'type': 'maintain',
                    'foods': safe_foods if safe_foods else ['Current well-tolerated foods'],
                    'reason': 'Your current dietary approach is working well - maintain these patterns',
                    'timeline': 'Continue current approach with gradual variety expansion',
                    'priority': 'low'
                },
                {
                    'type': 'explore',
                    'foods': ['Probiotic foods', 'Prebiotic fibers', 'Anti-inflammatory spices'],
                    'reason': 'Consider adding these foods to further optimize gut health',
                    'timeline': 'Introduce one new food per week',
                    'priority': 'low'
                }
            ])
        
        # Add FODMAP-specific recommendations
        fodmap_load = user_features.get('fodmap_load', 0)
        if fodmap_load > 7:
            recommendations.append({
                'type': 'eliminate',
                'foods': ['High FODMAP foods (onions, garlic, wheat, beans)', 'Artificial sweeteners'],
                'reason': f'Your FODMAP load is high ({fodmap_load}/10) - reducing these may significantly improve symptoms',
                'timeline': 'Follow strict low-FODMAP diet for 4-6 weeks',
                'priority': 'high'
            })
        
        # Add hydration recommendations
        recommendations.append({
            'type': 'hydration',
            'foods': ['Warm water', 'Herbal teas', 'Electrolyte solutions'],
            'reason': 'Proper hydration supports digestive health and can reduce constipation',
            'timeline': 'Aim for 8-10 glasses daily, warm liquids preferred',
            'priority': 'medium'
        })
        
        return recommendations

    async def _generate_personalized_lifestyle_recommendations(
        self, 
        user_id: int, 
        ml_predictions: Dict[str, Any],
        user_features: Dict[str, Any],
        db: Session
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
                    'suggestion': 'Practice deep breathing exercises (4-7-8 technique) during symptom onset',
                    'difficulty': 'easy',
                    'impact': 'Can provide immediate relief and prevent symptom escalation',
                    'frequency': '3-5 times daily, especially before meals',
                    'priority': 'high'
                },
                {
                    'category': 'Mindfulness',
                    'suggestion': 'Use a meditation app for 10-15 minutes daily',
                    'difficulty': 'easy',
                    'impact': 'Reduces stress-related IBS symptoms by up to 40%',
                    'frequency': 'Daily, preferably same time each day',
                    'priority': 'high'
                }
            ])
        
        # Sleep optimization
        if sleep_score < 6:
            recommendations.extend([
                {
                    'category': 'Sleep Hygiene',
                    'suggestion': 'Avoid eating 3 hours before bedtime',
                    'difficulty': 'moderate',
                    'impact': 'Better sleep quality and reduced morning symptoms',
                    'frequency': 'Every night',
                    'priority': 'high'
                },
                {
                    'category': 'Sleep Environment',
                    'suggestion': 'Keep bedroom cool (65-68°F) and use blackout curtains',
                    'difficulty': 'easy',
                    'impact': 'Improved sleep quality supports gut health recovery',
                    'frequency': 'Nightly',
                    'priority': 'medium'
                }
            ])
        
        # Exercise recommendations based on symptoms
        predicted_severity = ml_predictions.get('predicted_severity', 5)
        if predicted_severity < 5:
            recommendations.append({
                'category': 'Exercise',
                'suggestion': 'Engage in moderate cardio (walking, swimming) for 30 minutes',
                'difficulty': 'moderate',
                'impact': 'Improves gut motility and reduces stress hormones',
                'frequency': '4-5 times per week',
                'priority': 'medium'
            })
        else:
            recommendations.append({
                'category': 'Gentle Movement',
                'suggestion': 'Try gentle yoga or stretching for 10-15 minutes after meals',
                'difficulty': 'easy',
                'impact': 'Promotes healthy digestion and reduces gas buildup',
                'frequency': 'After each main meal',
                'priority': 'high'
            })
        
        # Meal timing recommendations
        recommendations.extend([
            {
                'category': 'Meal Timing',
                'suggestion': 'Eat smaller, more frequent meals (5-6 times daily)',
                'difficulty': 'moderate',
                'impact': 'Reduces digestive burden and prevents symptom spikes',
                'frequency': 'Daily meal planning',
                'priority': 'high'
            },
            {
                'category': 'Mindful Eating',
                'suggestion': 'Chew each bite 20-30 times and eat without distractions',
                'difficulty': 'moderate',
                'impact': 'Improves digestion and reduces bloating by 25-30%',
                'frequency': 'Every meal',
                'priority': 'medium'
            }
        ])
        
        # Work-life balance for high stress users
        if stress_level > 8:
            recommendations.append({
                'category': 'Work-Life Balance',
                'suggestion': 'Take 5-minute breaks every hour to practice breathing or stretching',
                'difficulty': 'easy',
                'impact': 'Prevents stress accumulation that can trigger symptoms',
                'frequency': 'During work hours',
                'priority': 'high'
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

    async def _identify_trigger_foods(self, user_id: int, db: Session) -> List[str]:
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

    async def _identify_safe_foods(self, user_id: int, db: Session) -> List[str]:
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
            'last_updated': datetime.utcnow().isoformat()
        }

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
            return {'risk_probability': 0.5, 'risk_level': 'Medium', 'confidence': 'Low'}
        
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
            
            # Determine risk level
            if risk_probability > 0.7:
                risk_level = 'High'
            elif risk_probability > 0.4:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'risk_probability': float(risk_probability),
                'risk_level': risk_level,
                'confidence': 'High' if len(self.ml_models) > 0 else 'Medium',
                'model_used': model_name
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return {'risk_probability': 0.5, 'risk_level': 'Medium', 'confidence': 'Low'}
    
    def _prepare_feature_vector(self, user_features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for ML model prediction."""
        # Default feature values
        default_features = {
            'stress_level': 5,
            'sleep_score': 7,
            'fodmap_load_score': 5,
            'daily_fiber_estimate': 20,
            'daily_calories_estimate': 2000,
            'is_weekend': 0,
            'wellness_composite': 5,
            'flare_risk_score': 5,
            'severity_trend_3day': 5,
            'fiber_per_1000_cal': 10,
            'high_stress_poor_sleep': 0,
            'high_fodmap_day': 0,
            'adequate_fiber': 1,
            'severe_symptoms': 0
        }
        
        # Update with provided features
        default_features.update(user_features)
        
        # Create feature vector in the expected order
        if self.feature_names:
            feature_vector = np.array([default_features.get(name, 0) for name in self.feature_names])
        else:
            # Fallback to common features
            common_features = ['stress_level', 'sleep_score', 'fodmap_load_score', 'daily_fiber_estimate']
            feature_vector = np.array([default_features.get(name, 0) for name in common_features])
        
        return feature_vector
    
    def generate_personalized_meal_plan(self, 
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


def create_enhanced_recommendation_service(db: Session) -> EnhancedRecommendationService:
    """Factory function to create enhanced recommendation service."""
    return EnhancedRecommendationService(db)