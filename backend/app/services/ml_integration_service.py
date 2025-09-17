"""
ML Integration Service

This service integrates machine learning models for personalized IBS recommendations,
symptom prediction, and intelligent chatbot responses.
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

from app.models.user import User
from app.models.symptom import SymptomLog, SeverityEnum
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.models.medication import MedicationLog
from app.schemas.chat import IBSAssessment, IBSSeverity, Recommendation
from app.core.logging import StructuredLogger

logger = logging.getLogger(__name__)


class MLIntegrationService:
    """Service for integrating ML models with the IBS chatbot system."""
    
    def __init__(self, db: Session):
        self.db = db
        self.models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
        self.models = {}
        self.scalers = {}
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained ML models and scalers."""
        try:
            # Load flare-up prediction model
            flareup_model_path = self.models_path / "checkpoints" / "flareup_predictor.pkl"
            if flareup_model_path.exists():
                self.models['flareup_predictor'] = joblib.load(flareup_model_path)
                logger.info("Loaded flare-up prediction model")
            
            # Load severity assessment model
            severity_model_path = self.models_path / "checkpoints" / "severity_classifier.pkl"
            if severity_model_path.exists():
                self.models['severity_classifier'] = joblib.load(severity_model_path)
                logger.info("Loaded severity classification model")
            
            # Load recommendation model
            recommendation_model_path = self.models_path / "checkpoints" / "recommendation_engine.pkl"
            if recommendation_model_path.exists():
                self.models['recommendation_engine'] = joblib.load(recommendation_model_path)
                logger.info("Loaded recommendation engine model")
            
            # Load scalers
            scaler_path = self.models_path / "checkpoints" / "feature_scaler.pkl"
            if scaler_path.exists():
                self.scalers['feature_scaler'] = joblib.load(scaler_path)
                logger.info("Loaded feature scaler")
                
        except Exception as e:
            logger.warning(f"Could not load some ML models: {e}")
            # Initialize fallback models if pre-trained ones aren't available
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize simple fallback models for development."""
        logger.info("Initializing fallback ML models")
        
        # Simple Random Forest for flare-up prediction
        self.models['flareup_predictor'] = RandomForestClassifier(
            n_estimators=100, random_state=42
        )
        
        # Simple classifier for severity assessment
        self.models['severity_classifier'] = RandomForestClassifier(
            n_estimators=50, random_state=42
        )
        
        # Standard scaler
        self.scalers['feature_scaler'] = StandardScaler()
    
    def predict_flareup_risk(self, user: User, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict the risk of IBS flare-up in the next N days.
        
        Args:
            user: User object
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary with risk score, confidence, and factors
        """
        try:
            # Extract features from user data
            features = self._extract_user_features(user)
            
            if not features or len(features) < 5:
                return {
                    "risk_score": 0.3,  # Default moderate risk
                    "risk_level": "moderate",
                    "confidence": 0.5,
                    "factors": ["Insufficient data for accurate prediction"],
                    "days_ahead": days_ahead,
                    "model_used": "fallback"
                }
            
            # Prepare feature array
            feature_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler is available
            if 'feature_scaler' in self.scalers:
                try:
                    feature_array = self.scalers['feature_scaler'].transform(feature_array)
                except:
                    # If scaler fails, use raw features
                    pass
            
            # Make prediction
            if 'flareup_predictor' in self.models:
                try:
                    risk_proba = self.models['flareup_predictor'].predict_proba(feature_array)[0]
                    risk_score = risk_proba[1] if len(risk_proba) > 1 else 0.3
                    confidence = max(risk_proba)
                except:
                    # Fallback calculation
                    risk_score = self._calculate_fallback_risk(features)
                    confidence = 0.6
            else:
                risk_score = self._calculate_fallback_risk(features)
                confidence = 0.6
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.7:
                risk_level = "moderate"
            else:
                risk_level = "high"
            
            # Identify key risk factors
            risk_factors = self._identify_risk_factors(user, features)
            
            # Log prediction
            structured_logger = StructuredLogger(__name__)
            structured_logger.log_ml_prediction(
                model_name="flareup_predictor",
                prediction_time=0.1,  # Placeholder timing
                user_id=user.id,
                input_data={"features": features[:5]},  # Log first 5 features only
                prediction=risk_score,
                confidence_score=confidence,
                metadata={"days_ahead": days_ahead, "risk_level": risk_level}
            )
            
            return {
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "confidence": round(confidence, 3),
                "factors": risk_factors,
                "days_ahead": days_ahead,
                "model_used": "ml_model" if 'flareup_predictor' in self.models else "fallback"
            }
            
        except Exception as e:
            logger.error(f"Error in flare-up prediction: {e}")
            return {
                "risk_score": 0.3,
                "risk_level": "moderate",
                "confidence": 0.5,
                "factors": ["Error in prediction model"],
                "days_ahead": days_ahead,
                "model_used": "error_fallback"
            }
    
    def enhance_severity_assessment(self, assessment: IBSAssessment, user: User) -> IBSAssessment:
        """
        Enhance IBS severity assessment using ML models.
        
        Args:
            assessment: Basic IBS assessment
            user: User object
            
        Returns:
            Enhanced assessment with ML insights
        """
        try:
            # Extract ML features
            features = self._extract_user_features(user)
            
            if features and len(features) >= 5:
                # Get ML-based severity prediction
                ml_severity = self._predict_ml_severity(features)
                
                # Combine rule-based and ML assessments
                combined_severity = self._combine_severity_assessments(
                    assessment.severity, ml_severity
                )
                
                # Update assessment
                assessment.severity = combined_severity
                assessment.confidence_score = min(assessment.confidence_score + 0.1, 1.0)
                assessment.factors.append("Enhanced with ML analysis")
                
                # Log ML enhancement
                structured_logger = StructuredLogger()
                structured_logger.log_ml_prediction(
                    user_id=user.id,
                    model_name="severity_enhancement",
                    input_data={"original_severity": assessment.severity.value},
                    prediction=combined_severity.value,
                    confidence_score=assessment.confidence_score,
                    metadata={"enhancement": "ml_combined"},
                    prediction_time=datetime.now()
                )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in severity enhancement: {e}")
            return assessment
    
    def generate_personalized_recommendations(self, user: User, assessment: IBSAssessment) -> List[Recommendation]:
        """
        Generate ML-enhanced personalized recommendations.
        
        Args:
            user: User object
            assessment: IBS assessment
            
        Returns:
            List of personalized recommendations
        """
        try:
            # Extract user features for personalization
            features = self._extract_user_features(user)
            user_profile = self._build_user_profile(user, features)
            
            # Get base recommendations from rule-based system
            base_recommendations = self._get_base_recommendations(assessment.severity)
            
            # Enhance with ML personalization
            if 'recommendation_engine' in self.models and features:
                personalized_recs = self._apply_ml_personalization(
                    base_recommendations, features, user_profile
                )
            else:
                personalized_recs = self._apply_heuristic_personalization(
                    base_recommendations, user_profile
                )
            
            return personalized_recs
            
        except Exception as e:
            logger.error(f"Error in recommendation generation: {e}")
            return self._get_base_recommendations(assessment.severity)
    
    def generate_onboarding_predictions(self, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ML-powered predictions based on onboarding questionnaire data.
        
        Args:
            onboarding_data: Complete onboarding questionnaire responses
            
        Returns:
            Dictionary with predictions and insights
        """
        try:
            # Extract features from onboarding data
            features = self._extract_onboarding_features(onboarding_data)
            
            # Generate predictions
            predictions = {
                "risk_assessment": self._predict_risk_level(features, onboarding_data),
                "trigger_analysis": self._analyze_triggers(onboarding_data),
                "lifestyle_insights": self._generate_lifestyle_insights(onboarding_data),
                "dietary_recommendations": self._generate_dietary_recommendations(onboarding_data),
                "management_strategy": self._suggest_management_strategy(onboarding_data),
                "predicted_severity": self._predict_severity_from_onboarding(features),
                "personalized_tips": self._generate_personalized_tips(onboarding_data)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating onboarding predictions: {e}")
            return self._get_fallback_predictions()
    
    def _extract_onboarding_features(self, data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from onboarding data for ML models."""
        features = []
        
        # Age feature
        features.append(float(data.get('age', 30)))
        
        # Gender encoding (0: female, 1: male, 0.5: other/unknown)
        gender_map = {'female': 0.0, 'male': 1.0, 'other': 0.5, 'prefer_not_to_say': 0.5}
        features.append(gender_map.get(data.get('gender', 'unknown'), 0.5))
        
        # IBS type encoding
        ibs_type_map = {'ibs-d': 1.0, 'ibs-c': 2.0, 'ibs-m': 3.0, 'ibs-u': 1.5}
        features.append(ibs_type_map.get(data.get('ibsType', 'ibs-u'), 1.5))
        
        # Severity level (1-10 scale)
        severity_map = {'mild': 3.0, 'moderate': 6.0, 'severe': 9.0}
        severity_value = data.get('severityLevel', 'mild')
        if isinstance(severity_value, str):
            features.append(severity_map.get(severity_value, 5.0))
        else:
            features.append(float(severity_value))
        
        # Years since diagnosis
        current_year = datetime.now().year
        diagnosis_year = data.get('diagnosisYear', current_year)
        try:
            # Handle case where diagnosisYear might be a string or invalid value
            if isinstance(diagnosis_year, str):
                # Try to convert to int, if it fails use current year
                try:
                    diagnosis_year = int(diagnosis_year)
                except ValueError:
                    diagnosis_year = current_year
            years_since_diagnosis = max(0, current_year - int(diagnosis_year))
        except (ValueError, TypeError):
            # Fallback to 1 year if conversion fails
            years_since_diagnosis = 1
        features.append(float(years_since_diagnosis))
        
        # Number of known triggers
        triggers = data.get('knownTriggers', [])
        features.append(float(len(triggers)))
        
        # Number of common symptoms
        symptoms = data.get('commonSymptoms', [])
        features.append(float(len(symptoms)))
        
        # Stress level (1-10 scale)
        features.append(float(data.get('stressLevel', 5)))
        
        # Sleep quality (1-10 scale)
        features.append(float(data.get('sleepQuality', 5)))
        
        # Exercise frequency encoding
        exercise_map = {'none': 0, 'light': 1, 'moderate': 2, 'intense': 3}
        exercise_value = data.get('exerciseFrequency', 'moderate')
        features.append(float(exercise_map.get(exercise_value, 2)))
        
        # Number of dietary restrictions
        dietary_restrictions = data.get('dietaryRestrictions', [])
        features.append(float(len(dietary_restrictions)))
        
        # Number of medications
        medications = data.get('medications', [])
        features.append(float(len(medications)))
        
        return features
    
    def _predict_risk_level(self, features: List[float], data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict overall IBS management risk level."""
        # Calculate risk score based on multiple factors
        # Ensure all values are converted to integers/floats to avoid string concatenation errors
        
        # Handle severity level conversion
        severity_value = data.get('severityLevel', 5)
        if isinstance(severity_value, str):
            severity_map = {'mild': 3, 'moderate': 6, 'severe': 9}
            severity = severity_map.get(severity_value.lower(), 5)
        else:
            severity = int(severity_value) if severity_value is not None else 5
            
        # Handle stress level conversion
        stress_value = data.get('stressLevel', 5)
        if isinstance(stress_value, str):
            stress_map = {'low': 2, 'mild': 3, 'moderate': 6, 'high': 8, 'severe': 9}
            stress = stress_map.get(stress_value.lower(), 5)
        else:
            stress = int(stress_value) if stress_value is not None else 5
            
        # Handle sleep quality conversion
        sleep_value = data.get('sleepQuality', 5)
        if isinstance(sleep_value, str):
            sleep_map = {'poor': 2, 'fair': 4, 'good': 6, 'excellent': 8}
            sleep_quality = sleep_map.get(sleep_value.lower(), 5)
        else:
            sleep_quality = int(sleep_value) if sleep_value is not None else 5
            
        num_triggers = len(data.get('knownTriggers', []))
        num_symptoms = len(data.get('commonSymptoms', []))
        
        # Risk calculation (0-100 scale)
        risk_score = (
            (severity * 10) +
            (stress * 8) +
            ((10 - sleep_quality) * 6) +
            (num_triggers * 5) +
            (num_symptoms * 3)
        ) / 3.2  # Normalize to 0-100
        
        risk_score = min(100, max(0, risk_score))
        
        if risk_score < 30:
            risk_level = "Low"
            description = "Your symptoms appear manageable with lifestyle modifications."
        elif risk_score < 60:
            risk_level = "Moderate"
            description = "You may benefit from structured management strategies."
        else:
            risk_level = "High"
            description = "Consider working closely with healthcare providers for optimal management."
        
        return {
            "level": risk_level,
            "score": round(risk_score, 1),
            "description": description,
            "confidence": 0.85
        }
    
    def _analyze_triggers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze reported triggers and provide insights."""
        triggers = data.get('knownTriggers', [])
        
        # Categorize triggers
        food_triggers = [t for t in triggers if t in ['dairy', 'gluten', 'spicy_foods', 'high_fat_foods', 'caffeine', 'alcohol']]
        stress_triggers = [t for t in triggers if t in ['work_stress', 'emotional_stress', 'lack_of_sleep']]
        lifestyle_triggers = [t for t in triggers if t in ['irregular_meals', 'travel', 'hormonal_changes']]
        
        analysis = {
            "primary_category": "food" if len(food_triggers) >= len(stress_triggers) else "stress",
            "food_triggers": food_triggers,
            "stress_triggers": stress_triggers,
            "lifestyle_triggers": lifestyle_triggers,
            "total_count": len(triggers),
            "insights": []
        }
        
        if len(food_triggers) > 2:
            analysis["insights"].append("Consider an elimination diet to identify specific food sensitivities.")
        
        if len(stress_triggers) > 1:
            analysis["insights"].append("Stress management techniques could significantly improve your symptoms.")
        
        if len(triggers) > 5:
            analysis["insights"].append("Multiple triggers suggest a comprehensive management approach is needed.")
        
        return analysis
    
    def _generate_lifestyle_insights(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized lifestyle insights."""
        insights = []
        
        # Sleep quality insight
        sleep_quality = data.get('sleepQuality', 5)
        if sleep_quality < 6:
            insights.append({
                "category": "Sleep",
                "insight": "Poor sleep quality can worsen IBS symptoms",
                "recommendation": "Aim for 7-9 hours of quality sleep nightly",
                "priority": "High"
            })
        
        # Exercise insight
        exercise_freq = data.get('exerciseFrequency', 'sometimes')
        if exercise_freq in ['never', 'rarely']:
            insights.append({
                "category": "Exercise",
                "insight": "Regular exercise can help regulate digestion",
                "recommendation": "Start with 20-30 minutes of moderate exercise 3x per week",
                "priority": "Medium"
            })
        
        # Stress insight
        stress_level = data.get('stressLevel', 5)
        if stress_level > 6:
            insights.append({
                "category": "Stress",
                "insight": "High stress levels can trigger IBS flare-ups",
                "recommendation": "Consider stress reduction techniques like meditation or yoga",
                "priority": "High"
            })
        
        return insights
    
    def _generate_dietary_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized dietary recommendations."""
        recommendations = []
        
        triggers = data.get('knownTriggers', [])
        dietary_restrictions = data.get('dietaryRestrictions', [])
        ibs_type = data.get('ibsType', 'ibs-u')
        
        # FODMAP recommendation
        if any(trigger in triggers for trigger in ['dairy', 'gluten', 'high_fat_foods']):
            recommendations.append({
                "type": "Diet Plan",
                "title": "Low-FODMAP Diet",
                "description": "Consider trying a low-FODMAP diet to identify trigger foods",
                "duration": "4-6 weeks",
                "priority": "High"
            })
        
        # Fiber recommendations based on IBS type
        if ibs_type == 'ibs-c':
            recommendations.append({
                "type": "Nutrition",
                "title": "Increase Soluble Fiber",
                "description": "Gradually increase soluble fiber intake to help with constipation",
                "examples": "Oats, bananas, carrots, psyllium husk",
                "priority": "Medium"
            })
        elif ibs_type == 'ibs-d':
            recommendations.append({
                "type": "Nutrition",
                "title": "Limit Insoluble Fiber",
                "description": "Reduce insoluble fiber during flare-ups to minimize diarrhea",
                "examples": "Limit raw vegetables, whole grains during symptoms",
                "priority": "Medium"
            })
        
        # Hydration
        recommendations.append({
            "type": "Hydration",
            "title": "Maintain Proper Hydration",
            "description": "Drink 8-10 glasses of water daily, avoid carbonated drinks",
            "priority": "Medium"
        })
        
        return recommendations
    
    def _suggest_management_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest overall management strategy based on profile."""
        severity = data.get('severityLevel', 5)
        primary_goals = data.get('primaryGoals', [])
        
        if severity <= 3:
            strategy = "Lifestyle-Focused"
            approach = "Focus on dietary modifications and stress management"
        elif severity <= 6:
            strategy = "Integrated Approach"
            approach = "Combine lifestyle changes with targeted interventions"
        else:
            strategy = "Comprehensive Management"
            approach = "Multi-modal approach including medical consultation"
        
        return {
            "strategy": strategy,
            "approach": approach,
            "primary_focus": primary_goals[0] if primary_goals else "symptom_relief",
            "timeline": "4-8 weeks for initial improvements"
        }
    
    def _predict_severity_from_onboarding(self, features: List[float]) -> str:
        """Predict likely severity category from onboarding features."""
        if not features or len(features) < 4:
            return "Moderate"
        
        # Simple heuristic based on key features
        severity_score = features[3]  # Direct severity rating
        stress_score = features[7] if len(features) > 7 else 5
        trigger_count = features[5] if len(features) > 5 else 0
        
        combined_score = (severity_score + stress_score + trigger_count) / 3
        
        if combined_score <= 3:
            return "Mild"
        elif combined_score <= 6:
            return "Moderate"
        else:
            return "Severe"
    
    def _generate_personalized_tips(self, data: Dict[str, Any]) -> List[str]:
        """Generate personalized tips based on user profile."""
        tips = []
        
        # Age-specific tips
        age = data.get('age', 30)
        if age > 50:
            tips.append("Consider discussing hormone-related IBS changes with your healthcare provider")
        elif age < 30:
            tips.append("Establish consistent routines early to better manage symptoms long-term")
        
        # Gender-specific tips
        gender = data.get('gender')
        if gender == 'female':
            tips.append("Track symptoms in relation to your menstrual cycle for pattern recognition")
        
        # IBS type-specific tips
        ibs_type = data.get('ibsType')
        if ibs_type == 'ibs-d':
            tips.append("Keep anti-diarrheal medication handy when traveling or during stressful periods")
        elif ibs_type == 'ibs-c':
            tips.append("Establish a regular bathroom routine, ideally at the same time each day")
        
        # Stress-related tips
        if data.get('stressLevel', 5) > 6:
            tips.append("Consider keeping a stress-symptom diary to identify your personal stress triggers")
        
        return tips[:5]  # Limit to top 5 tips
    
    def _get_fallback_predictions(self) -> Dict[str, Any]:
        """Provide fallback predictions when ML processing fails."""
        return {
            "risk_assessment": {
                "level": "Moderate",
                "score": 50.0,
                "description": "Based on general IBS patterns, moderate management approach recommended.",
                "confidence": 0.6
            },
            "trigger_analysis": {
                "primary_category": "mixed",
                "insights": ["Consider keeping a symptom diary to identify personal triggers"]
            },
            "lifestyle_insights": [
                {
                    "category": "General",
                    "insight": "Regular routines can help manage IBS symptoms",
                    "recommendation": "Maintain consistent meal and sleep schedules",
                    "priority": "Medium"
                }
            ],
            "dietary_recommendations": [
                {
                    "type": "General",
                    "title": "Balanced Approach",
                    "description": "Focus on a balanced diet with regular meal timing",
                    "priority": "Medium"
                }
            ],
            "management_strategy": {
                "strategy": "Balanced Approach",
                "approach": "Combine dietary awareness with lifestyle modifications",
                "timeline": "4-6 weeks for initial assessment"
            },
            "predicted_severity": "Moderate",
            "personalized_tips": [
                "Keep a food and symptom diary",
                "Stay hydrated throughout the day",
                "Practice stress management techniques"
            ]
        }
    
    def _extract_user_features(self, user: User) -> List[float]:
        """Extract numerical features from user data for ML models."""
        features = []
        
        try:
            # Get recent symptom data (last 30 days)
            recent_symptoms = self.db.query(SymptomLog).filter(
                SymptomLog.user_id == user.id,
                SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            # Symptom frequency features
            features.append(len(recent_symptoms))  # Total symptom logs
            features.append(len([s for s in recent_symptoms if s.severity == SeverityEnum.SEVERE]))
            features.append(len([s for s in recent_symptoms if s.severity == SeverityEnum.MODERATE]))
            
            # Pain and discomfort averages
            pain_scores = [s.pain_level for s in recent_symptoms if s.pain_level]
            features.append(np.mean(pain_scores) if pain_scores else 0)
            
            # Bowel movement patterns
            bm_logs = [s for s in recent_symptoms if hasattr(s, 'bristol_stool_type')]
            features.append(len(bm_logs))
            
            # Food reaction data
            food_reactions = self.db.query(FoodReaction).filter(
                FoodReaction.user_id == user.id,
                FoodReaction.reaction_date >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            features.append(len(food_reactions))  # Number of food reactions
            severe_reactions = len([r for r in food_reactions if r.severity == ReactionSeverityEnum.SEVERE])
            features.append(severe_reactions)
            
            # Medication adherence
            medications = self.db.query(MedicationLog).filter(
                MedicationLog.user_id == user.id,
                MedicationLog.taken_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            features.append(len(medications))  # Medication logs
            
            # User profile features
            features.append(user.age if user.age else 30)  # Default age
            features.append(1 if user.gender and user.gender.value == 'female' else 0)
            
            # Pad or truncate to fixed size (e.g., 15 features)
            target_size = 15
            if len(features) < target_size:
                features.extend([0] * (target_size - len(features)))
            else:
                features = features[:target_size]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting user features: {e}")
            return [0] * 15  # Return default features
    
    def _calculate_fallback_risk(self, features: List[float]) -> float:
        """Calculate risk score using heuristic rules when ML model is unavailable."""
        if not features or len(features) < 5:
            return 0.3
        
        # Simple heuristic based on symptom frequency and severity
        symptom_count = features[0] if len(features) > 0 else 0
        severe_symptoms = features[1] if len(features) > 1 else 0
        pain_level = features[3] if len(features) > 3 else 0
        food_reactions = features[5] if len(features) > 5 else 0
        
        # Normalize and combine factors
        risk_score = (
            min(symptom_count / 20, 1.0) * 0.3 +  # Symptom frequency
            min(severe_symptoms / 10, 1.0) * 0.4 +  # Severe symptoms
            min(pain_level / 10, 1.0) * 0.2 +  # Pain level
            min(food_reactions / 15, 1.0) * 0.1  # Food reactions
        )
        
        return min(max(risk_score, 0.0), 1.0)
    
    def _identify_risk_factors(self, user: User, features: List[float]) -> List[str]:
        """Identify key risk factors based on user data and features."""
        factors = []
        
        if len(features) >= 10:
            if features[0] > 15:  # High symptom frequency
                factors.append("High symptom frequency detected")
            if features[1] > 5:  # Many severe symptoms
                factors.append("Frequent severe symptoms")
            if features[3] > 7:  # High pain levels
                factors.append("Elevated pain levels")
            if features[5] > 10:  # Many food reactions
                factors.append("Multiple food sensitivities")
            if features[7] < 5:  # Low medication adherence
                factors.append("Inconsistent medication use")
        
        return factors[:5]  # Return top 5 factors
    
    def _predict_ml_severity(self, features: List[float]) -> IBSSeverity:
        """Predict severity using ML model."""
        try:
            if 'severity_classifier' in self.models:
                feature_array = np.array(features).reshape(1, -1)
                prediction = self.models['severity_classifier'].predict(feature_array)[0]
                
                # Map prediction to severity enum
                if prediction == 0:
                    return IBSSeverity.MILD
                elif prediction == 1:
                    return IBSSeverity.MODERATE
                else:
                    return IBSSeverity.SEVERE
            else:
                # Fallback heuristic
                risk_score = self._calculate_fallback_risk(features)
                if risk_score < 0.3:
                    return IBSSeverity.MILD
                elif risk_score < 0.7:
                    return IBSSeverity.MODERATE
                else:
                    return IBSSeverity.SEVERE
                    
        except Exception as e:
            logger.error(f"Error in ML severity prediction: {e}")
            return IBSSeverity.MODERATE
    
    def _combine_severity_assessments(self, rule_based: IBSSeverity, ml_based: IBSSeverity) -> IBSSeverity:
        """Combine rule-based and ML-based severity assessments."""
        # Simple voting mechanism
        severity_values = {
            IBSSeverity.MILD: 1,
            IBSSeverity.MODERATE: 2,
            IBSSeverity.SEVERE: 3
        }
        
        rule_value = severity_values[rule_based]
        ml_value = severity_values[ml_based]
        
        # Weighted average (rule-based gets 60% weight, ML gets 40%)
        combined_value = int(round(rule_value * 0.6 + ml_value * 0.4))
        
        # Map back to enum
        for severity, value in severity_values.items():
            if value == combined_value:
                return severity
        
        return rule_based  # Fallback to rule-based
    
    def _build_user_profile(self, user: User, features: List[float]) -> Dict[str, Any]:
        """Build user profile for personalization."""
        return {
            "age": user.age or 30,
            "gender": user.gender.value if user.gender else "unknown",
            "ibs_type": user.ibs_type.value if user.ibs_type else "unknown",
            "symptom_frequency": features[0] if features else 0,
            "severity_pattern": "high" if features and features[1] > 5 else "moderate",
            "food_sensitivity": "high" if features and len(features) > 5 and features[5] > 10 else "moderate"
        }
    
    def _get_base_recommendations(self, severity: IBSSeverity) -> List[Recommendation]:
        """Get base recommendations for given severity level."""
        # This would typically come from the RecommendationService
        # Simplified version for ML integration
        base_recs = []
        
        if severity == IBSSeverity.MILD:
            base_recs = [
                {"title": "Dietary Modifications", "priority": 1, "type": "diet"},
                {"title": "Stress Management", "priority": 2, "type": "lifestyle"}
            ]
        elif severity == IBSSeverity.MODERATE:
            base_recs = [
                {"title": "Low-FODMAP Diet", "priority": 1, "type": "diet"},
                {"title": "Regular Exercise", "priority": 2, "type": "lifestyle"},
                {"title": "Probiotics", "priority": 3, "type": "treatment"}
            ]
        else:  # SEVERE
            base_recs = [
                {"title": "Medical Consultation", "priority": 1, "type": "treatment"},
                {"title": "Elimination Diet", "priority": 2, "type": "diet"},
                {"title": "Stress Therapy", "priority": 3, "type": "lifestyle"}
            ]
        
        return base_recs
    
    def _apply_ml_personalization(self, base_recs: List[Dict], features: List[float], profile: Dict) -> List[Recommendation]:
        """Apply ML-based personalization to recommendations."""
        # This would use the recommendation_engine model
        # Simplified version for now
        return self._apply_heuristic_personalization(base_recs, profile)
    
    def _apply_heuristic_personalization(self, base_recs: List[Dict], profile: Dict) -> List[Recommendation]:
        """Apply heuristic-based personalization to recommendations."""
        personalized = []
        
        for rec in base_recs:
            # Customize based on user profile
            if profile["food_sensitivity"] == "high" and rec["type"] == "diet":
                rec["priority"] = max(1, rec["priority"] - 1)  # Increase priority
            
            if profile["age"] > 50 and rec["type"] == "lifestyle":
                # Add age-specific modifications
                rec["title"] += " (Age-Adapted)"
            
            personalized.append(Recommendation(
                title=rec["title"],
                description=f"Personalized recommendation based on your profile",
                type=rec["type"],
                priority=rec["priority"],
                evidence_level="Moderate",
                actionable_steps=[f"Follow {rec['title'].lower()} guidelines"],
                expected_benefit="Improved symptom management",
                timeframe="2-4 weeks"
            ))
        
        return personalized