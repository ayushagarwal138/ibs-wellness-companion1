"""
Personalized Threshold Service for ML-driven severity classification.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import FoodReaction

logger = logging.getLogger(__name__)


class PersonalizedThresholdService:
    """Service for generating personalized severity thresholds."""
    
    # Default thresholds as fallback
    DEFAULT_THRESHOLDS = {
        "mild": 0.25,
        "moderate": 0.5,
        "severe": 0.75
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_personalized_thresholds(self, user: User) -> Dict[str, float]:
        """Generate personalized severity thresholds for a user."""
        try:
            # Build user profile from historical data
            profile = self._build_user_profile(user)
            
            # Calculate personalized thresholds
            base_mild = self.DEFAULT_THRESHOLDS["mild"]
            base_moderate = self.DEFAULT_THRESHOLDS["moderate"]
            base_severe = self.DEFAULT_THRESHOLDS["severe"]
            
            # Adjust based on user's historical severity patterns
            severity_adjustment = self._calculate_severity_adjustment(profile)
            
            thresholds = {
                "mild": max(0.1, base_mild + severity_adjustment),
                "moderate": max(0.3, base_moderate + severity_adjustment),
                "severe": max(0.5, base_severe + severity_adjustment)
            }
            
            # Ensure thresholds are properly ordered
            thresholds["moderate"] = max(
                thresholds["mild"] + 0.1, thresholds["moderate"]
            )
            thresholds["severe"] = max(
                thresholds["moderate"] + 0.1, thresholds["severe"]
            )
            
            logger.info(f"Generated thresholds for user {user.id}: {thresholds}")
            return thresholds
            
        except Exception as e:
            logger.error(f"Error generating thresholds for user {user.id}: {e}")
            return self.DEFAULT_THRESHOLDS
    
    def classify_severity_with_personalized_thresholds(
        self, user: User, severity_score: float
    ) -> str:
        """Classify severity using personalized thresholds."""
        try:
            thresholds = self.generate_personalized_thresholds(user)
            
            if severity_score >= thresholds["severe"]:
                return "severe"
            elif severity_score >= thresholds["moderate"]:
                return "moderate"
            elif severity_score >= thresholds["mild"]:
                return "mild"
            else:
                return "none"
                
        except Exception as e:
            logger.error(f"Error classifying severity for user {user.id}: {e}")
            # Fallback to default classification
            return self._classify_with_default_thresholds(severity_score)
    
    def _classify_with_default_thresholds(self, severity_score: float) -> str:
        """Classify severity using default thresholds."""
        if severity_score >= self.DEFAULT_THRESHOLDS["severe"]:
            return "severe"
        elif severity_score >= self.DEFAULT_THRESHOLDS["moderate"]:
            return "moderate"
        elif severity_score >= self.DEFAULT_THRESHOLDS["mild"]:
            return "mild"
        else:
            return "none"
    
    def _build_user_profile(self, user: User) -> Dict[str, Any]:
        """Build comprehensive user profile from historical data."""
        # Get last 90 days of data
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Get symptom logs
        symptoms = self.db.query(SymptomLog).filter(
            SymptomLog.user_id == user.id,
            SymptomLog.logged_at >= cutoff_date
        ).all()
        
        # Get food reactions
        reactions = self.db.query(FoodReaction).filter(
            FoodReaction.user_id == user.id,
            FoodReaction.reaction_occurred_at >= cutoff_date
        ).all()
        
        profile = {
            "user_id": user.id,
            "age": (
                self._calculate_age(user.date_of_birth) 
                if user.date_of_birth else 30
            ),
            "symptom_frequency": len(symptoms) / 90,  # symptoms per day
            "avg_severity": self._calculate_avg_severity(symptoms),
            "reaction_frequency": len(reactions) / 90,  # reactions per day
            "symptom_variability": self._calculate_variability(symptoms),
            "total_symptoms": len(symptoms),
            "total_reactions": len(reactions)
        }
        
        return profile
    
    def _calculate_severity_adjustment(self, profile: Dict[str, Any]) -> float:
        """Calculate adjustment factor based on user profile."""
        adjustment = 0.0
        
        # Adjust based on symptom frequency
        if profile["symptom_frequency"] > 2.0:  # More than 2 symptoms per day
            adjustment += 0.1
        elif profile["symptom_frequency"] < 0.5:  # Less than 0.5 per day
            adjustment -= 0.05
        
        # Adjust based on average severity
        if profile["avg_severity"] > 7.0:
            adjustment += 0.15
        elif profile["avg_severity"] < 3.0:
            adjustment -= 0.1
        
        # Adjust based on reaction frequency
        if profile["reaction_frequency"] > 1.0:
            adjustment += 0.05
        
        # Adjust based on age (older users may have different thresholds)
        if profile["age"] > 60:
            adjustment += 0.05
        elif profile["age"] < 25:
            adjustment -= 0.05
        
        # Cap adjustment to reasonable range
        return max(-0.2, min(0.2, adjustment))
    
    def _calculate_avg_severity(self, symptoms: List[SymptomLog]) -> float:
        """Calculate average severity from symptom logs."""
        if not symptoms:
            return 5.0  # Default moderate severity
        
        total_severity = sum(
            getattr(symptom, 'severity_level', 5) for symptom in symptoms
        )
        return total_severity / len(symptoms)
    
    def _calculate_variability(self, symptoms: List[SymptomLog]) -> float:
        """Calculate severity variability."""
        if len(symptoms) < 2:
            return 0.0
        
        severities = [
            getattr(symptom, 'severity_level', 5) for symptom in symptoms
        ]
        avg = sum(severities) / len(severities)
        variance = sum((s - avg) ** 2 for s in severities) / len(severities)
        return variance ** 0.5  # Standard deviation
    
    def _calculate_age(self, date_of_birth: datetime) -> int:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return 30  # Default age
        
        today = datetime.utcnow().date()
        birth_date = date_of_birth.date()
        age = today.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today < birth_date.replace(year=today.year):
            age -= 1
        
        return age
    
    def get_threshold_explanation(self, user: User) -> Dict[str, Any]:
        """Get explanation of how thresholds were calculated."""
        try:
            profile = self._build_user_profile(user)
            thresholds = self.generate_personalized_thresholds(user)
            adjustment = self._calculate_severity_adjustment(profile)
            
            return {
                "thresholds": thresholds,
                "adjustment_factor": adjustment,
                "profile_summary": {
                    "symptom_frequency": profile["symptom_frequency"],
                    "avg_severity": profile["avg_severity"],
                    "reaction_frequency": profile["reaction_frequency"],
                    "age": profile["age"]
                },
                "explanation": self._generate_explanation(profile, adjustment)
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation for user {user.id}: {e}")
            return {
                "thresholds": self.DEFAULT_THRESHOLDS,
                "adjustment_factor": 0.0,
                "explanation": "Using default thresholds due to insufficient data."
            }
    
    def _generate_explanation(
        self, profile: Dict[str, Any], adjustment: float
    ) -> str:
        """Generate human-readable explanation of threshold calculation."""
        explanations = []
        
        if profile["symptom_frequency"] > 2.0:
            explanations.append("high symptom frequency")
        elif profile["symptom_frequency"] < 0.5:
            explanations.append("low symptom frequency")
        
        if profile["avg_severity"] > 7.0:
            explanations.append("typically severe symptoms")
        elif profile["avg_severity"] < 3.0:
            explanations.append("typically mild symptoms")
        
        if profile["reaction_frequency"] > 1.0:
            explanations.append("frequent food reactions")
        
        if adjustment > 0:
            direction = "raised"
        elif adjustment < 0:
            direction = "lowered"
        else:
            direction = "kept standard"
        
        if explanations:
            factors = ", ".join(explanations)
            return (
                f"Thresholds {direction} based on your {factors}. "
                f"Adjustment factor: {adjustment:.2f}"
            )
        else:
            return "Using standard thresholds based on your profile."