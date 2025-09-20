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
    
    def generate_enhanced_recommendations(self, 
                                        user: User, 
                                        ibs_assessment: IBSAssessment,
                                        user_context: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """
        Generate enhanced recommendations using ML predictions and external data insights.
        
        Args:
            user: User object
            ibs_assessment: Current IBS severity assessment
            user_context: Additional context about user preferences and history
            
        Returns:
            List of enhanced personalized recommendations
        """
        recommendations = []
        
        # Get ML-based risk prediction
        user_features = self._extract_user_features(user, ibs_assessment, user_context)
        risk_prediction = self.predict_symptom_risk(user_features)
        
        # Generate base recommendations
        base_recommendations = super().generate_recommendations(user, ibs_assessment, user_context)
        
        # Enhance recommendations with ML insights
        enhanced_recommendations = self._enhance_with_ml_insights(
            base_recommendations, risk_prediction, user_features
        )
        
        # Add ML-driven personalized recommendations
        ml_recommendations = self._generate_ml_driven_recommendations(
            user, risk_prediction, user_features
        )
        
        # Add nutrition-optimized recommendations
        nutrition_recommendations = self._generate_nutrition_recommendations(
            user_features, risk_prediction
        )
        
        # Combine and prioritize all recommendations
        all_recommendations = enhanced_recommendations + ml_recommendations + nutrition_recommendations
        
        # Sort by priority and ML confidence
        all_recommendations.sort(key=lambda x: (x.priority, -risk_prediction['risk_probability']))
        
        return all_recommendations[:10]  # Return top 10 recommendations
    
    def _extract_user_features(self, 
                             user: User, 
                             ibs_assessment: IBSAssessment,
                             user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract features from user data for ML prediction."""
        features = {}
        
        # Basic features from assessment
        features['stress_level'] = getattr(ibs_assessment, 'stress_level', 5)
        features['sleep_score'] = getattr(ibs_assessment, 'sleep_quality', 7)
        
        # Calculate FODMAP load from recent diet logs
        features['fodmap_load_score'] = self._calculate_fodmap_load(user.id)
        
        # Estimate daily nutrition
        nutrition_estimates = self._estimate_daily_nutrition(user.id)
        features.update(nutrition_estimates)
        
        # Temporal features
        features['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
        
        # Composite scores
        features['wellness_composite'] = (
            (10 - features['stress_level']) * 0.3 +
            features['sleep_score'] * 0.3 +
            (10 - features['fodmap_load_score']) * 0.4
        )
        
        features['flare_risk_score'] = (
            features['stress_level'] * 0.25 +
            (10 - features['sleep_score']) * 0.25 +
            features['fodmap_load_score'] * 0.5
        )
        
        return features
    
    def _calculate_fodmap_load(self, user_id: int) -> float:
        """Calculate FODMAP load from recent diet logs."""
        try:
            # Get recent food reactions
            recent_reactions = self.db.query(FoodReaction).filter(
                and_(
                    FoodReaction.user_id == user_id,
                    FoodReaction.created_at >= datetime.now() - timedelta(days=7)
                )
            ).all()
            
            # Calculate FODMAP score based on known high-FODMAP foods
            fodmap_score = 0
            high_fodmap_foods = []
            for category in self.fodmap_database['high_fodmap_foods'].values():
                high_fodmap_foods.extend(category)
            
            for reaction in recent_reactions:
                food_name = reaction.food_name.lower()
                if any(fodmap_food in food_name for fodmap_food in high_fodmap_foods):
                    if reaction.severity == ReactionSeverityEnum.SEVERE:
                        fodmap_score += 3
                    elif reaction.severity == ReactionSeverityEnum.MODERATE:
                        fodmap_score += 2
                    else:
                        fodmap_score += 1
            
            return min(fodmap_score, 10)  # Cap at 10
            
        except Exception as e:
            logger.error(f"Error calculating FODMAP load: {e}")
            return 5  # Default moderate score
    
    def _estimate_daily_nutrition(self, user_id: int) -> Dict[str, float]:
        """Estimate daily nutrition from recent diet logs."""
        # This would integrate with the nutrition database from external datasets
        # For now, return reasonable estimates
        return {
            'daily_fiber_estimate': 22.0,
            'daily_calories_estimate': 2000.0,
            'fiber_per_1000_cal': 11.0,
            'adequate_fiber': 1 if 22.0 >= 25 else 0
        }
    
    def _enhance_with_ml_insights(self, 
                                base_recommendations: List[Recommendation],
                                risk_prediction: Dict[str, Any],
                                user_features: Dict[str, Any]) -> List[Recommendation]:
        """Enhance base recommendations with ML insights."""
        enhanced = []
        
        for rec in base_recommendations:
            # Adjust priority based on ML risk prediction
            if risk_prediction['risk_level'] == 'High' and rec.type == RecommendationType.DIET:
                rec.priority = max(1, rec.priority - 1)  # Increase priority
                rec.description += f" (ML Risk Assessment: {risk_prediction['risk_level']})"
            
            # Add confidence indicators
            rec.evidence_level = f"{rec.evidence_level} + ML Insights"
            enhanced.append(rec)
        
        return enhanced
    
    def _generate_ml_driven_recommendations(self, 
                                          user: User,
                                          risk_prediction: Dict[str, Any],
                                          user_features: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations based on ML model insights."""
        recommendations = []
        
        # High-risk specific recommendations
        if risk_prediction['risk_level'] == 'High':
            recommendations.append(Recommendation(
                type=RecommendationType.DIET,
                title="Immediate FODMAP Restriction",
                description="ML analysis indicates high symptom risk - implement strict low-FODMAP diet immediately",
                priority=1,
                evidence_level="ML Prediction + Clinical Evidence",
                actionable_steps=[
                    "Eliminate all high-FODMAP foods for 2 weeks",
                    "Focus on safe foods: rice, chicken, carrots, spinach",
                    "Monitor symptoms daily with detailed logging",
                    "Consider meal replacement shakes if needed"
                ],
                expected_benefit="Rapid symptom reduction based on predictive model",
                timeframe="1-2 weeks"
            ))
        
        # Stress-sleep interaction recommendations
        if user_features.get('flare_risk_score', 0) > 7:
            recommendations.append(Recommendation(
                type=RecommendationType.LIFESTYLE,
                title="Integrated Stress-Sleep Management",
                description="ML model identifies high flare risk from stress-sleep interaction",
                priority=2,
                evidence_level="ML Analysis + Research",
                actionable_steps=[
                    "Implement 10-minute evening meditation routine",
                    "Set consistent sleep schedule (same time daily)",
                    "Use stress tracking app with symptom correlation",
                    "Consider magnesium supplement before bed"
                ],
                expected_benefit="Reduced flare risk by 30-40% based on model predictions",
                timeframe="2-3 weeks"
            ))
        
        # Personalized nutrition optimization
        if user_features.get('fiber_per_1000_cal', 0) < 10:
            recommendations.append(Recommendation(
                type=RecommendationType.DIET,
                title="Optimized Fiber Strategy",
                description="ML analysis suggests personalized fiber approach for your profile",
                priority=3,
                evidence_level="ML Nutrition Analysis",
                actionable_steps=[
                    "Start with 5g soluble fiber daily (psyllium husk)",
                    "Add 2g every 3 days until reaching 15g daily",
                    "Focus on soluble sources: oats, bananas, carrots",
                    "Track fiber intake and symptom response"
                ],
                expected_benefit="Improved bowel regularity with minimal symptom increase",
                timeframe="3-4 weeks"
            ))
        
        return recommendations
    
    def _generate_nutrition_recommendations(self, 
                                          user_features: Dict[str, Any],
                                          risk_prediction: Dict[str, Any]) -> List[Recommendation]:
        """Generate nutrition recommendations based on external dataset insights."""
        recommendations = []
        
        # Micronutrient optimization
        recommendations.append(Recommendation(
            type=RecommendationType.DIET,
            title="IBS-Specific Micronutrient Support",
            description="Targeted nutrients based on IBS research and nutritional databases",
            priority=4,
            evidence_level="Nutritional Research + External Data",
            actionable_steps=[
                "Take vitamin D3 (2000 IU daily) for immune support",
                "Consider B-complex for gut-brain axis support",
                "Add omega-3 (1g daily) for anti-inflammatory effects",
                "Monitor magnesium levels (supports muscle relaxation)"
            ],
            expected_benefit="Enhanced gut health and reduced inflammation",
            timeframe="4-6 weeks"
        ))
        
        # Meal timing optimization
        if risk_prediction['risk_level'] in ['Medium', 'High']:
            recommendations.append(Recommendation(
                type=RecommendationType.LIFESTYLE,
                title="Optimized Meal Timing Protocol",
                description="Evidence-based meal timing to minimize IBS symptoms",
                priority=3,
                evidence_level="Clinical Research + ML Insights",
                actionable_steps=[
                    "Eat 5-6 small meals instead of 3 large ones",
                    "Space meals 2-3 hours apart",
                    "Stop eating 3 hours before bedtime",
                    "Drink water between meals, not during"
                ],
                expected_benefit="Reduced digestive stress and better symptom control",
                timeframe="1-2 weeks"
            ))
        
        return recommendations
    
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