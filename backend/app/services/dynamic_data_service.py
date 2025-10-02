"""
Dynamic Data Service for managing FODMAP data, nutrition guidelines,
and recommendations. This service replaces hardcoded values with
database-driven dynamic content.
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import logging

from app.models.diet import Food, FODMAPLevelEnum, DietLog
from app.models.user import User
from app.models.symptom import SymptomLog
from app.core.dynamic_config import get_config, RiskLevel, RecommendationPriority

logger = logging.getLogger(__name__)


class DynamicDataService:
    """Service for managing dynamic data instead of hardcoded values."""

    def __init__(self, db: Session):
        self.db = db
        self.config = get_config()

    def get_fodmap_foods(
        self, fodmap_level: FODMAPLevelEnum = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get FODMAP foods from database instead of hardcoded lists."""
        try:
            query = self.db.query(Food)

            if fodmap_level:
                query = query.filter(Food.fodmap_level == fodmap_level)

            foods = query.all()

            # Group foods by FODMAP level and category
            fodmap_data = {
                "high_fodmap": [],
                "medium_fodmap": [],
                "low_fodmap": [],
                "alternatives": {},
            }

            for food in foods:
                food_data = {
                    "id": food.id,
                    "name": food.name,
                    "category": food.category.value if food.category else "other",
                    "fodmap_level": food.fodmap_level.value,
                    "serving_size": food.serving_size,
                    "calories_per_serving": food.calories_per_serving,
                    "fiber_per_serving": food.fiber_per_serving,
                    "notes": food.notes,
                }

                if food.fodmap_level == FODMAPLevelEnum.HIGH:
                    fodmap_data["high_fodmap"].append(food_data)
                elif food.fodmap_level == FODMAPLevelEnum.MODERATE:
                    fodmap_data["medium_fodmap"].append(food_data)
                elif food.fodmap_level == FODMAPLevelEnum.LOW:
                    fodmap_data["low_fodmap"].append(food_data)

            # Get alternatives mapping
            fodmap_data["alternatives"] = self._get_food_alternatives()

            return fodmap_data

        except Exception as e:
            logger.error(f"Error fetching FODMAP foods: {e}")
            return self._get_fallback_fodmap_data()

    def _get_food_alternatives(self) -> Dict[str, List[str]]:
        """Get food alternatives mapping from database."""
        try:
            # Query for low FODMAP alternatives to high FODMAP foods
            high_fodmap_foods = (
                self.db.query(Food)
                .filter(Food.fodmap_level == FODMAPLevelEnum.HIGH)
                .all()
            )

            alternatives = {}

            for high_food in high_fodmap_foods:
                # Find low FODMAP foods in the same category
                low_alternatives = (
                    self.db.query(Food)
                    .filter(
                        and_(
                            Food.category == high_food.category,
                            Food.fodmap_level == FODMAPLevelEnum.LOW,
                        )
                    )
                    .limit(3)
                    .all()
                )

                if low_alternatives:
                    alternatives[high_food.name] = [
                        alt.name for alt in low_alternatives
                    ]

            return alternatives

        except Exception as e:
            logger.error(f"Error fetching food alternatives: {e}")
            return {}

    def get_personalized_nutrition_guidelines(self, user_id: int) -> Dict[str, Any]:
        """Get personalized nutrition guidelines based on user data and history."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._get_default_nutrition_guidelines()

            # Get user's symptom and diet history for personalization
            recent_symptoms = self._get_recent_symptoms(user_id, days=30)
            diet_patterns = self._get_diet_patterns(user_id, days=30)

            # Base nutrition targets from config
            base_targets = self.config.get_nutrition_targets(user.weight)

            # Personalize based on user data
            personalized_targets = self._personalize_nutrition_targets(
                base_targets, user, recent_symptoms, diet_patterns
            )

            return {
                "daily_targets": personalized_targets,
                "meal_timing": self._get_meal_timing_recommendations(
                    user, recent_symptoms
                ),
                "hydration": self._get_hydration_recommendations(user),
                "supplements": self._get_supplement_recommendations(
                    user, recent_symptoms
                ),
                "personalization_score": self._calculate_personalization_score(user_id),
            }

        except Exception as e:
            logger.error(f"Error getting personalized nutrition guidelines: {e}")
            return self._get_default_nutrition_guidelines()

    def _get_recent_symptoms(self, user_id: int, days: int = 30) -> List[SymptomLog]:
        """Get recent symptom logs for a user."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(SymptomLog)
            .filter(
                and_(SymptomLog.user_id == user_id, SymptomLog.logged_at >= cutoff_date)
            )
            .all()
        )

    def _get_diet_patterns(self, user_id: int, days: int = 30) -> List[DietLog]:
        """Get recent diet patterns for a user."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(DietLog)
            .filter(and_(DietLog.user_id == user_id, DietLog.logged_at >= cutoff_date))
            .all()
        )

    def _personalize_nutrition_targets(
        self,
        base_targets: Dict[str, Any],
        user: User,
        symptoms: List[SymptomLog],
        diet_patterns: List[DietLog],
    ) -> Dict[str, Any]:
        """Personalize nutrition targets based on user data."""
        personalized = base_targets.copy()

        # Adjust fiber recommendations based on symptom patterns
        if symptoms:
            avg_severity = sum(s.severity.value for s in symptoms) / len(symptoms)

            if avg_severity > 3:  # High symptom severity
                # Reduce fiber recommendations for sensitive users
                personalized["fiber_soluble"]["max"] *= 0.8
                personalized["fiber_insoluble"]["max"] *= 0.7
            elif avg_severity < 2:  # Low symptom severity
                # Can handle more fiber
                personalized["fiber_soluble"]["max"] *= 1.2
                personalized["fiber_insoluble"]["max"] *= 1.1

        # Adjust based on IBS type
        if user.ibs_type:
            if "constipation" in user.ibs_type.value.lower():
                personalized["fiber_insoluble"]["min"] *= 1.3
                personalized["water"]["min"] *= 1.2
            elif "diarrhea" in user.ibs_type.value.lower():
                personalized["fiber_soluble"]["max"] *= 1.2
                personalized["fiber_insoluble"]["max"] *= 0.8

        return personalized

    def _get_meal_timing_recommendations(
        self, user: User, symptoms: List[SymptomLog]
    ) -> Dict[str, Any]:
        """Get personalized meal timing recommendations."""
        base_timing = {
            "meals_per_day": self.config.nutrition.meal_frequency_min,
            "spacing_hours": self.config.nutrition.meal_spacing_hours,
            "last_meal_before_bed": self.config.nutrition.last_meal_hours_before_bed,
        }

        # Adjust based on symptom patterns
        if symptoms:
            evening_symptoms = [s for s in symptoms if s.logged_at.hour >= 18]
            if len(evening_symptoms) > len(symptoms) * 0.3:  # Many evening symptoms
                base_timing["last_meal_before_bed"] += 1.0  # Eat earlier
                base_timing["meals_per_day"] = min(
                    base_timing["meals_per_day"] + 1,
                    self.config.nutrition.meal_frequency_max,
                )

        return base_timing

    def _get_hydration_recommendations(self, user: User) -> Dict[str, Any]:
        """Get personalized hydration recommendations."""
        base_water = self.config.nutrition.water_min_ml

        # Adjust based on user weight and activity
        if user.weight:
            # 35ml per kg body weight as base
            weight_based = user.weight * 35
            base_water = max(base_water, weight_based)

        return {
            "daily_target_ml": base_water,
            "timing": [
                {"time": "upon_waking", "amount_ml": 250},
                {"time": "before_meals", "amount_ml": 200},
                {"time": "between_meals", "amount_ml": 150},
                {"time": "before_bed", "amount_ml": 100},
            ],
        }

    def _get_supplement_recommendations(
        self, user: User, symptoms: List[SymptomLog]
    ) -> List[Dict[str, Any]]:
        """Get personalized supplement recommendations."""
        supplements = []

        # Base IBS-friendly supplements
        base_supplements = [
            {
                "name": "Probiotics",
                "dosage": "10-50 billion CFU",
                "timing": "with_meals",
                "evidence_level": "high",
                "notes": "Multi-strain probiotic for gut health",
            },
            {
                "name": "Peppermint Oil",
                "dosage": "0.2-0.4ml",
                "timing": "before_meals",
                "evidence_level": "high",
                "notes": "Enteric-coated capsules for IBS symptoms",
            },
        ]

        supplements.extend(base_supplements)

        # Add personalized supplements based on symptoms
        if symptoms:
            symptom_types = [s.symptom.name for s in symptoms]

            if "bloating" in symptom_types or "gas" in symptom_types:
                supplements.append(
                    {
                        "name": "Digestive Enzymes",
                        "dosage": "1-2 capsules",
                        "timing": "with_meals",
                        "evidence_level": "medium",
                        "notes": "May help with bloating and gas",
                    }
                )

            if "constipation" in symptom_types:
                supplements.append(
                    {
                        "name": "Magnesium",
                        "dosage": "200-400mg",
                        "timing": "evening",
                        "evidence_level": "medium",
                        "notes": "Magnesium glycinate for gentle laxative effect",
                    }
                )

        return supplements

    def _calculate_personalization_score(self, user_id: int) -> float:
        """Calculate how personalized the recommendations can be based on available data."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return 0.0

            score = 0.0
            max_score = 100.0

            # User profile completeness (30 points)
            profile_score = 0
            if user.age:
                profile_score += 5
            if user.weight:
                profile_score += 5
            if user.height:
                profile_score += 5
            if user.gender:
                profile_score += 5
            if user.ibs_type:
                profile_score += 10
            score += profile_score

            # Symptom tracking history (25 points)
            symptom_count = (
                self.db.query(SymptomLog).filter(SymptomLog.user_id == user_id).count()
            )
            symptom_score = min(25, symptom_count * 2.5)
            score += symptom_score

            # Diet tracking history (20 points)
            diet_count = (
                self.db.query(DietLog).filter(DietLog.user_id == user_id).count()
            )
            diet_score = min(20, diet_count * 2)
            score += diet_score

            # Recent activity (15 points)
            recent_logs = (
                self.db.query(SymptomLog)
                .filter(
                    and_(
                        SymptomLog.user_id == user_id,
                        SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=7),
                    )
                )
                .count()
            )
            recent_score = min(15, recent_logs * 3)
            score += recent_score

            # Data consistency (10 points)
            consistency_score = self._calculate_data_consistency(user_id)
            score += consistency_score

            return min(score, max_score)

        except Exception as e:
            logger.error(f"Error calculating personalization score: {e}")
            return 0.0

    def _calculate_data_consistency(self, user_id: int) -> float:
        """Calculate data consistency score."""
        try:
            # Check if user has been logging consistently
            recent_days = 14
            cutoff_date = datetime.utcnow() - timedelta(days=recent_days)

            days_with_logs = (
                self.db.query(func.date(SymptomLog.logged_at))
                .filter(
                    and_(
                        SymptomLog.user_id == user_id,
                        SymptomLog.logged_at >= cutoff_date,
                    )
                )
                .distinct()
                .count()
            )

            consistency_ratio = days_with_logs / recent_days
            return consistency_ratio * 10  # Max 10 points

        except Exception as e:
            logger.error(f"Error calculating data consistency: {e}")
            return 0.0

    def _get_default_nutrition_guidelines(self) -> Dict[str, Any]:
        """Get default nutrition guidelines when personalization is not available."""
        return {
            "daily_targets": self.config.get_nutrition_targets(),
            "meal_timing": {
                "meals_per_day": self.config.nutrition.meal_frequency_min,
                "spacing_hours": self.config.nutrition.meal_spacing_hours,
                "last_meal_before_bed": self.config.nutrition.last_meal_hours_before_bed,
            },
            "hydration": {
                "daily_target_ml": self.config.nutrition.water_min_ml,
                "timing": [
                    {"time": "upon_waking", "amount_ml": 250},
                    {"time": "before_meals", "amount_ml": 200},
                    {"time": "between_meals", "amount_ml": 150},
                ],
            },
            "supplements": [],
            "personalization_score": 0.0,
        }

    def _get_fallback_fodmap_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback FODMAP data when database is unavailable."""
        return {
            "high_fodmap": [
                {"name": "Wheat", "category": "grains", "fodmap_level": "high"},
                {"name": "Onions", "category": "vegetables", "fodmap_level": "high"},
                {"name": "Garlic", "category": "vegetables", "fodmap_level": "high"},
            ],
            "low_fodmap": [
                {"name": "Rice", "category": "grains", "fodmap_level": "low"},
                {"name": "Carrots", "category": "vegetables", "fodmap_level": "low"},
                {"name": "Spinach", "category": "vegetables", "fodmap_level": "low"},
            ],
            "alternatives": {
                "Wheat": ["Rice", "Quinoa", "Oats"],
                "Onions": ["Green onion tops", "Chives"],
                "Garlic": ["Garlic oil", "Asafoetida"],
            },
        }

    def get_dynamic_recommendations(
        self, user_id: int, risk_level: RiskLevel
    ) -> List[Dict[str, Any]]:
        """Generate dynamic recommendations based on user data and risk level."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._get_fallback_recommendations(risk_level)

            recent_symptoms = self._get_recent_symptoms(user_id, days=7)
            diet_patterns = self._get_diet_patterns(user_id, days=14)

            recommendations = []

            # Generate personalized recommendations based on data
            if risk_level == RiskLevel.HIGH:
                recommendations.extend(
                    self._get_high_risk_recommendations(user, recent_symptoms)
                )
            elif risk_level == RiskLevel.MEDIUM:
                recommendations.extend(
                    self._get_medium_risk_recommendations(user, recent_symptoms)
                )
            else:
                recommendations.extend(
                    self._get_low_risk_recommendations(user, recent_symptoms)
                )

            # Add diet-specific recommendations
            recommendations.extend(self._get_diet_recommendations(user, diet_patterns))

            # Limit recommendations based on config
            max_recommendations = (
                self.config.recommendations.max_immediate_actions
                + self.config.recommendations.max_dietary_suggestions
                + self.config.recommendations.max_lifestyle_changes
            )

            return recommendations[:max_recommendations]

        except Exception as e:
            logger.error(f"Error generating dynamic recommendations: {e}")
            return self._get_fallback_recommendations(risk_level)

    def _get_high_risk_recommendations(
        self, user: User, symptoms: List[SymptomLog]
    ) -> List[Dict[str, Any]]:
        """Get high-risk specific recommendations."""
        recommendations = [
            {
                "type": "immediate_action",
                "priority": RecommendationPriority.URGENT.value,
                "title": "Immediate Symptom Management",
                "description": "Focus on symptom relief and trigger avoidance",
                "actions": [
                    "Return to safe foods you know work well",
                    "Increase hydration with electrolytes",
                    "Consider stress management techniques",
                ],
                "confidence": 0.9,
            }
        ]

        # Add symptom-specific recommendations
        if symptoms:
            symptom_types = [s.symptom.name for s in symptoms]
            if "pain" in symptom_types:
                recommendations.append(
                    {
                        "type": "pain_management",
                        "priority": RecommendationPriority.HIGH.value,
                        "title": "Pain Relief Protocol",
                        "description": "Gentle approaches to manage abdominal pain",
                        "actions": [
                            "Apply heat therapy to abdomen",
                            "Try gentle yoga or stretching",
                            "Consider peppermint tea",
                        ],
                        "confidence": 0.8,
                    }
                )

        return recommendations

    def _get_medium_risk_recommendations(
        self, user: User, symptoms: List[SymptomLog]
    ) -> List[Dict[str, Any]]:
        """Get medium-risk specific recommendations."""
        return [
            {
                "type": "dietary_adjustment",
                "priority": RecommendationPriority.MEDIUM.value,
                "title": "Dietary Modifications",
                "description": "Gradual adjustments to reduce symptoms",
                "actions": [
                    "Review recent food choices for triggers",
                    "Increase low FODMAP foods",
                    "Monitor portion sizes",
                ],
                "confidence": 0.7,
            }
        ]

    def _get_low_risk_recommendations(
        self, user: User, symptoms: List[SymptomLog]
    ) -> List[Dict[str, Any]]:
        """Get low-risk specific recommendations."""
        return [
            {
                "type": "maintenance",
                "priority": RecommendationPriority.LOW.value,
                "title": "Wellness Maintenance",
                "description": "Continue current positive patterns",
                "actions": [
                    "Maintain current dietary approach",
                    "Continue regular meal timing",
                    "Keep tracking symptoms and diet",
                ],
                "confidence": 0.8,
            }
        ]

    def _get_diet_recommendations(
        self, user: User, diet_patterns: List[DietLog]
    ) -> List[Dict[str, Any]]:
        """Get diet-specific recommendations based on patterns."""
        recommendations = []

        if diet_patterns:
            # Analyze diet patterns for recommendations
            food_frequency = {}
            for log in diet_patterns:
                if log.food_id:
                    food_frequency[log.food_id] = food_frequency.get(log.food_id, 0) + 1

            # Get most frequent foods
            if food_frequency:
                frequent_foods = sorted(
                    food_frequency.items(), key=lambda x: x[1], reverse=True
                )[:5]
                food_ids = [food_id for food_id, _ in frequent_foods]

                foods = self.db.query(Food).filter(Food.id.in_(food_ids)).all()
                high_fodmap_foods = [
                    f for f in foods if f.fodmap_level == FODMAPLevelEnum.HIGH
                ]

                if high_fodmap_foods:
                    recommendations.append(
                        {
                            "type": "dietary_suggestion",
                            "priority": RecommendationPriority.MEDIUM.value,
                            "title": "High FODMAP Food Review",
                            "description": f"Consider reducing: {', '.join([f.name for f in high_fodmap_foods[:3]])}",
                            "actions": [
                                f"Try alternatives to {food.name}"
                                for food in high_fodmap_foods[:3]
                            ],
                            "confidence": 0.6,
                        }
                    )

        return recommendations

    def _get_fallback_recommendations(
        self, risk_level: RiskLevel
    ) -> List[Dict[str, Any]]:
        """Fallback recommendations when personalization is not available."""
        base_recommendations = [
            {
                "type": "general",
                "priority": RecommendationPriority.MEDIUM.value,
                "title": "General IBS Management",
                "description": "Basic recommendations for IBS wellness",
                "actions": [
                    "Follow a low FODMAP diet",
                    "Eat regular, smaller meals",
                    "Stay hydrated",
                    "Manage stress levels",
                ],
                "confidence": self.config.recommendations.fallback_confidence,
            }
        ]

        return base_recommendations
