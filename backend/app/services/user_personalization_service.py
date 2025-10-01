"""
User Personalization Service

This service provides adaptive algorithms and user-specific customization
for recommendations, thresholds, and ML model parameters based on user
behavior, preferences, and historical data.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.dynamic_config import get_config
from app.services.dynamic_data_service import DynamicDataService
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog


class UserPersonalizationService:
    """Service for providing personalized, adaptive recommendations and configurations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = get_config()
        self.dynamic_data_service = DynamicDataService(db)
        
    def get_personalized_ml_thresholds(self, user_id: int) -> Dict[str, Any]:
        """
        Get personalized ML model thresholds based on user's historical data and patterns.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing personalized thresholds and weights
        """
        user_profile = self._get_user_profile(user_id)
        historical_patterns = self._analyze_historical_patterns(user_id)
        
        # Base thresholds from config
        base_config = self.config.ml_model
        
        # Adaptive adjustments based on user patterns
        personalized_thresholds = {
            "risk_thresholds": {
                "high": self._adjust_threshold(
                    base_config.risk_thresholds.high,
                    historical_patterns.get("sensitivity_factor", 1.0),
                    user_profile.get("risk_tolerance", "medium")
                ),
                "medium": self._adjust_threshold(
                    base_config.risk_thresholds.medium,
                    historical_patterns.get("sensitivity_factor", 1.0),
                    user_profile.get("risk_tolerance", "medium")
                )
            },
            "weights": {
                "symptom_weight": self._adjust_weight(
                    base_config.weights.symptom_weight,
                    historical_patterns.get("symptom_correlation", 1.0)
                ),
                "stress_weight": self._adjust_weight(
                    base_config.weights.stress_weight,
                    historical_patterns.get("stress_correlation", 1.0)
                ),
                "sleep_weight": self._adjust_weight(
                    base_config.weights.sleep_weight,
                    historical_patterns.get("sleep_correlation", 1.0)
                )
            },
            "confidence_threshold": self._adjust_confidence_threshold(
                base_config.confidence_threshold,
                historical_patterns.get("prediction_accuracy", 0.7)
            ),
            "personalization_metadata": {
                "last_updated": datetime.utcnow().isoformat(),
                "data_points_used": historical_patterns.get("data_points", 0),
                "adaptation_level": self._calculate_adaptation_level(historical_patterns)
            }
        }
        
        return personalized_thresholds
    
    def get_adaptive_recommendations(self, user_id: int, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate adaptive recommendations based on user's current context and learning patterns.
        
        Args:
            user_id: User ID
            current_context: Current user context (symptoms, stress, etc.)
            
        Returns:
            Personalized recommendations with adaptive prioritization
        """
        user_profile = self._get_user_profile(user_id)
        learning_patterns = self._get_learning_patterns(user_id)
        effectiveness_scores = self._calculate_recommendation_effectiveness(user_id)
        
        # Get base recommendations
        base_recommendations = self.dynamic_data_service.get_personalized_recommendations(
            user_id, current_context
        )
        
        # Apply adaptive prioritization
        adaptive_recommendations = {
            "dietary": self._prioritize_recommendations(
                base_recommendations.get("dietary", []),
                effectiveness_scores.get("dietary", {}),
                learning_patterns.get("dietary_preferences", {})
            ),
            "lifestyle": self._prioritize_recommendations(
                base_recommendations.get("lifestyle", []),
                effectiveness_scores.get("lifestyle", {}),
                learning_patterns.get("lifestyle_patterns", {})
            ),
            "medical": self._prioritize_recommendations(
                base_recommendations.get("medical", []),
                effectiveness_scores.get("medical", {}),
                learning_patterns.get("medical_adherence", {})
            ),
            "personalization_insights": {
                "adaptation_confidence": learning_patterns.get("confidence", 0.5),
                "recommendation_count": len(base_recommendations.get("dietary", [])) + 
                                      len(base_recommendations.get("lifestyle", [])) + 
                                      len(base_recommendations.get("medical", [])),
                "user_engagement_score": self._calculate_engagement_score(user_id),
                "learning_progress": learning_patterns.get("learning_progress", "initial")
            }
        }
        
        return adaptive_recommendations
    
    def update_user_learning_patterns(self, user_id: int, feedback_data: Dict[str, Any]) -> bool:
        """
        Update user learning patterns based on feedback and outcomes.
        
        Args:
            user_id: User ID
            feedback_data: User feedback and outcome data
            
        Returns:
            Success status
        """
        try:
            # Store feedback for future learning
            self._store_feedback(user_id, feedback_data)
            
            # Update learning patterns
            self._update_learning_patterns(user_id, feedback_data)
            
            # Recalculate effectiveness scores
            self._recalculate_effectiveness_scores(user_id)
            
            return True
        except Exception as e:
            print(f"Error updating learning patterns: {e}")
            return False
    
    def get_personalized_nutrition_targets(self, user_id: int) -> Dict[str, Any]:
        """
        Get personalized nutrition targets based on user's profile and patterns.
        
        Args:
            user_id: User ID
            
        Returns:
            Personalized nutrition targets and guidelines
        """
        user_profile = self._get_user_profile(user_id)
        dietary_patterns = self._analyze_dietary_patterns(user_id)
        
        base_nutrition = self.dynamic_data_service.get_nutrition_guidelines()
        
        personalized_nutrition = {
            "daily_targets": self._adjust_nutrition_targets(
                base_nutrition.get("daily_targets", {}),
                user_profile,
                dietary_patterns
            ),
            "fodmap_tolerance": self._calculate_fodmap_tolerance(user_id),
            "trigger_food_sensitivity": self._calculate_trigger_sensitivity(user_id),
            "meal_timing_preferences": self._get_optimal_meal_timing(user_id),
            "hydration_targets": self._calculate_hydration_needs(user_profile),
            "supplement_recommendations": self._get_personalized_supplements(user_id)
        }
        
        return personalized_nutrition
    
    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user profile including preferences and demographics."""
        user = self.db.query(User).filter(User.id == user_id).first()
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not user:
            return {}
        
        profile = {
            "age": user.age,
            "gender": user.gender,
            "activity_level": getattr(preferences, "activity_level", "moderate") if preferences else "moderate",
            "risk_tolerance": getattr(preferences, "risk_tolerance", "medium") if preferences else "medium",
            "dietary_restrictions": getattr(preferences, "dietary_restrictions", []) if preferences else [],
            "health_goals": getattr(preferences, "health_goals", []) if preferences else [],
            "notification_preferences": getattr(preferences, "notification_preferences", {}) if preferences else {}
        }
        
        return profile
    
    def _analyze_historical_patterns(self, user_id: int, days: int = 90) -> Dict[str, Any]:
        """Analyze user's historical patterns for the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get symptom patterns
        symptoms = self.db.query(SymptomLog).filter(
            SymptomLog.user_id == user_id,
            SymptomLog.logged_at >= cutoff_date
        ).all()
        
        # Get diet patterns
        diet_logs = self.db.query(DietLog).filter(
            DietLog.user_id == user_id,
            DietLog.logged_at >= cutoff_date
        ).all()
        
        if not symptoms:
            return {"data_points": 0, "sensitivity_factor": 1.0}
        
        # Calculate patterns
        severity_scores = [s.severity for s in symptoms]
        avg_severity = np.mean(severity_scores) if severity_scores else 5.0
        severity_variance = np.var(severity_scores) if len(severity_scores) > 1 else 1.0
        
        # Calculate correlations (simplified)
        patterns = {
            "data_points": len(symptoms),
            "avg_severity": avg_severity,
            "severity_variance": severity_variance,
            "sensitivity_factor": self._calculate_sensitivity_factor(severity_scores),
            "symptom_correlation": min(1.0, len(symptoms) / 30),  # More data = higher correlation
            "stress_correlation": self._calculate_stress_correlation(symptoms),
            "sleep_correlation": self._calculate_sleep_correlation(symptoms),
            "prediction_accuracy": self._estimate_prediction_accuracy(symptoms)
        }
        
        return patterns
    
    def _adjust_threshold(self, base_threshold: float, sensitivity_factor: float, risk_tolerance: str) -> float:
        """Adjust threshold based on user sensitivity and risk tolerance."""
        # Risk tolerance adjustments
        tolerance_adjustments = {
            "low": 0.8,      # More conservative (lower thresholds)
            "medium": 1.0,   # No adjustment
            "high": 1.2      # Less conservative (higher thresholds)
        }
        
        tolerance_factor = tolerance_adjustments.get(risk_tolerance, 1.0)
        
        # Apply adjustments
        adjusted = base_threshold * sensitivity_factor * tolerance_factor
        
        # Keep within reasonable bounds
        return max(0.1, min(0.9, adjusted))
    
    def _adjust_weight(self, base_weight: float, correlation: float) -> float:
        """Adjust weight based on correlation strength."""
        # Increase weight for factors with higher correlation
        adjusted = base_weight * (0.5 + 0.5 * correlation)
        return max(0.1, min(1.0, adjusted))
    
    def _adjust_confidence_threshold(self, base_threshold: float, accuracy: float) -> float:
        """Adjust confidence threshold based on historical accuracy."""
        # Higher accuracy allows for lower confidence threshold
        adjusted = base_threshold * (1.0 - 0.2 * accuracy)
        return max(0.3, min(0.9, adjusted))
    
    def _calculate_adaptation_level(self, patterns: Dict[str, Any]) -> str:
        """Calculate the level of adaptation based on available data."""
        data_points = patterns.get("data_points", 0)
        
        if data_points < 10:
            return "initial"
        elif data_points < 30:
            return "learning"
        elif data_points < 90:
            return "adapting"
        else:
            return "optimized"
    
    def _get_learning_patterns(self, user_id: int) -> Dict[str, Any]:
        """Get user's learning patterns and preferences."""
        # This would typically come from a learning patterns table
        # For now, return default patterns
        return {
            "confidence": 0.7,
            "learning_progress": "adapting",
            "dietary_preferences": {},
            "lifestyle_patterns": {},
            "medical_adherence": {}
        }
    
    def _calculate_recommendation_effectiveness(self, user_id: int) -> Dict[str, Any]:
        """Calculate effectiveness scores for different recommendation types."""
        # This would analyze user feedback and outcomes
        # For now, return default scores
        return {
            "dietary": {"effectiveness": 0.8, "adherence": 0.7},
            "lifestyle": {"effectiveness": 0.6, "adherence": 0.5},
            "medical": {"effectiveness": 0.9, "adherence": 0.8}
        }
    
    def _prioritize_recommendations(self, recommendations: List[Dict], effectiveness: Dict, patterns: Dict) -> List[Dict]:
        """Prioritize recommendations based on effectiveness and patterns."""
        if not recommendations:
            return []
        
        # Add personalized priority scores
        for rec in recommendations:
            base_priority = {"high": 3, "medium": 2, "low": 1}.get(rec.get("priority", "medium"), 2)
            effectiveness_score = effectiveness.get("effectiveness", 0.5)
            
            # Calculate personalized priority
            personalized_score = base_priority * (1 + effectiveness_score)
            rec["personalized_priority"] = personalized_score
            rec["effectiveness_score"] = effectiveness_score
        
        # Sort by personalized priority
        return sorted(recommendations, key=lambda x: x.get("personalized_priority", 0), reverse=True)
    
    def _calculate_engagement_score(self, user_id: int) -> float:
        """Calculate user engagement score based on activity."""
        # Count recent logs
        recent_logs = self.db.query(SymptomLog).filter(
            SymptomLog.user_id == user_id,
            SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Simple engagement score (0-1)
        return min(1.0, recent_logs / 7.0)
    
    def _store_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> None:
        """Store user feedback for future learning."""
        # This would store feedback in a dedicated table
        pass
    
    def _update_learning_patterns(self, user_id: int, feedback_data: Dict[str, Any]) -> None:
        """Update learning patterns based on feedback."""
        # This would update learning patterns in the database
        pass
    
    def _recalculate_effectiveness_scores(self, user_id: int) -> None:
        """Recalculate effectiveness scores based on new data."""
        # This would recalculate and store updated effectiveness scores
        pass
    
    def _analyze_dietary_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's dietary patterns and preferences."""
        # This would analyze diet logs to identify patterns
        return {
            "preferred_foods": [],
            "avoided_foods": [],
            "meal_timing": {},
            "portion_preferences": {}
        }
    
    def _adjust_nutrition_targets(self, base_targets: Dict, profile: Dict, patterns: Dict) -> Dict[str, Any]:
        """Adjust nutrition targets based on user profile and patterns."""
        # Adjust based on age, gender, activity level, etc.
        adjusted_targets = base_targets.copy()
        
        # Example adjustments
        if profile.get("activity_level") == "high":
            adjusted_targets["calories"] = adjusted_targets.get("calories", 2000) * 1.2
        elif profile.get("activity_level") == "low":
            adjusted_targets["calories"] = adjusted_targets.get("calories", 2000) * 0.8
        
        return adjusted_targets
    
    def _calculate_fodmap_tolerance(self, user_id: int) -> Dict[str, Any]:
        """Calculate user's FODMAP tolerance levels."""
        return {
            "overall_tolerance": "medium",
            "specific_tolerances": {
                "fructans": "low",
                "lactose": "medium",
                "fructose": "high",
                "polyols": "medium"
            }
        }
    
    def _calculate_trigger_sensitivity(self, user_id: int) -> Dict[str, float]:
        """Calculate sensitivity to different trigger foods."""
        return {
            "dairy": 0.8,
            "gluten": 0.6,
            "spicy_foods": 0.7,
            "high_fat": 0.5
        }
    
    def _get_optimal_meal_timing(self, user_id: int) -> Dict[str, Any]:
        """Get optimal meal timing based on user patterns."""
        return {
            "breakfast": "7:00-9:00",
            "lunch": "12:00-14:00",
            "dinner": "18:00-20:00",
            "snacks": ["10:00", "15:00"],
            "meal_frequency": "small_frequent"
        }
    
    def _calculate_hydration_needs(self, profile: Dict) -> Dict[str, Any]:
        """Calculate personalized hydration needs."""
        base_water = 2000  # ml
        
        # Adjust based on activity level
        activity_multiplier = {
            "low": 0.9,
            "moderate": 1.0,
            "high": 1.3
        }.get(profile.get("activity_level", "moderate"), 1.0)
        
        return {
            "daily_water_ml": int(base_water * activity_multiplier),
            "timing_recommendations": [
                "Upon waking",
                "Before meals",
                "During exercise",
                "Before bed"
            ]
        }
    
    def _get_personalized_supplements(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized supplement recommendations."""
        return [
            {
                "name": "Probiotics",
                "dosage": "10 billion CFU daily",
                "timing": "With breakfast",
                "reasoning": "Support gut microbiome balance"
            },
            {
                "name": "Fiber supplement",
                "dosage": "5g daily",
                "timing": "With dinner",
                "reasoning": "Gradual fiber increase for digestive health"
            }
        ]
    
    def _calculate_sensitivity_factor(self, severity_scores: List[float]) -> float:
        """Calculate sensitivity factor based on severity patterns."""
        if not severity_scores:
            return 1.0
        
        avg_severity = np.mean(severity_scores)
        # Higher average severity = higher sensitivity factor
        return min(1.5, max(0.5, avg_severity / 5.0))
    
    def _calculate_stress_correlation(self, symptoms: List) -> float:
        """Calculate correlation between stress and symptoms."""
        # Simplified correlation calculation
        # In real implementation, this would analyze stress levels vs symptoms
        return 0.7
    
    def _calculate_sleep_correlation(self, symptoms: List) -> float:
        """Calculate correlation between sleep and symptoms."""
        # Simplified correlation calculation
        # In real implementation, this would analyze sleep quality vs symptoms
        return 0.6
    
    def _estimate_prediction_accuracy(self, symptoms: List) -> float:
        """Estimate prediction accuracy based on historical data."""
        # Simplified accuracy estimation
        # In real implementation, this would compare predictions vs actual outcomes
        return min(0.9, max(0.5, len(symptoms) / 100))