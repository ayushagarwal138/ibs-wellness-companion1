"""
IBS Recommendation Service

This service provides personalized recommendations for diet, lifestyle,
and treatment based on IBS severity assessment and user data patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.user import User
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.schemas.chat import IBSAssessment, IBSSeverity, Recommendation, RecommendationType


class RecommendationService:
    """Service for generating personalized IBS recommendations."""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Evidence-based recommendation database
        self.diet_recommendations = {
            IBSSeverity.MILD: [
                {
                    "title": "Follow a Low-FODMAP Diet",
                    "description": "Reduce intake of fermentable carbohydrates that can trigger IBS symptoms",
                    "priority": 1,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Eliminate high-FODMAP foods for 2-6 weeks",
                        "Keep a detailed food diary",
                        "Gradually reintroduce foods to identify triggers",
                        "Consider working with a registered dietitian"
                    ],
                    "expected_benefit": "60-70% of IBS patients see symptom improvement",
                    "timeframe": "2-6 weeks for initial phase"
                },
                {
                    "title": "Increase Soluble Fiber Intake",
                    "description": "Add soluble fiber gradually to help regulate bowel movements",
                    "priority": 2,
                    "evidence_level": "Moderate",
                    "actionable_steps": [
                        "Start with 5-10g soluble fiber daily",
                        "Include oats, bananas, and carrots",
                        "Increase gradually by 2-3g per week",
                        "Drink plenty of water"
                    ],
                    "expected_benefit": "Improved stool consistency and reduced bloating",
                    "timeframe": "2-4 weeks"
                }
            ],
            IBSSeverity.MODERATE: [
                {
                    "title": "Strict Low-FODMAP Diet with Professional Guidance",
                    "description": "Implement a comprehensive low-FODMAP approach with dietitian support",
                    "priority": 1,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Consult with IBS-specialized dietitian",
                        "Follow elimination phase strictly for 4-6 weeks",
                        "Use FODMAP tracking apps",
                        "Plan structured reintroduction phase"
                    ],
                    "expected_benefit": "Significant symptom reduction in 70-80% of cases",
                    "timeframe": "6-12 weeks for full protocol"
                },
                {
                    "title": "Implement Stress Management Techniques",
                    "description": "Address gut-brain connection through stress reduction",
                    "priority": 2,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Practice daily meditation (10-20 minutes)",
                        "Try progressive muscle relaxation",
                        "Consider cognitive behavioral therapy",
                        "Maintain regular sleep schedule"
                    ],
                    "expected_benefit": "Reduced symptom severity and frequency",
                    "timeframe": "4-8 weeks"
                }
            ],
            IBSSeverity.SEVERE: [
                {
                    "title": "Comprehensive Medical Management",
                    "description": "Work closely with gastroenterologist for medication optimization",
                    "priority": 1,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Schedule gastroenterologist consultation",
                        "Discuss prescription medications (antispasmodics, etc.)",
                        "Consider probiotics with clinical evidence",
                        "Evaluate for comorbid conditions"
                    ],
                    "expected_benefit": "Significant symptom control with proper medication",
                    "timeframe": "2-4 weeks to see initial improvement"
                },
                {
                    "title": "Intensive Dietary Intervention",
                    "description": "Structured elimination diet with close monitoring",
                    "priority": 2,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Work with specialized IBS dietitian",
                        "Consider elemental diet for severe cases",
                        "Implement strict food and symptom tracking",
                        "Regular follow-up appointments"
                    ],
                    "expected_benefit": "Identification of specific triggers and symptom relief",
                    "timeframe": "8-12 weeks for comprehensive approach"
                }
            ]
        }
        
        self.lifestyle_recommendations = {
            IBSSeverity.MILD: [
                {
                    "title": "Regular Exercise Routine",
                    "description": "Gentle, consistent physical activity to improve gut motility",
                    "priority": 1,
                    "evidence_level": "Moderate",
                    "actionable_steps": [
                        "Start with 20-30 minutes walking daily",
                        "Try yoga or tai chi for stress relief",
                        "Avoid high-intensity exercise during flares",
                        "Maintain consistency over intensity"
                    ],
                    "expected_benefit": "Improved bowel regularity and reduced stress",
                    "timeframe": "2-4 weeks"
                }
            ],
            IBSSeverity.MODERATE: [
                {
                    "title": "Structured Sleep Hygiene",
                    "description": "Optimize sleep quality to support gut health",
                    "priority": 1,
                    "evidence_level": "Moderate",
                    "actionable_steps": [
                        "Maintain consistent sleep schedule",
                        "Create relaxing bedtime routine",
                        "Limit screen time before bed",
                        "Keep bedroom cool and dark"
                    ],
                    "expected_benefit": "Better symptom management and reduced flares",
                    "timeframe": "2-3 weeks"
                },
                {
                    "title": "Mindfulness-Based Stress Reduction",
                    "description": "Systematic approach to managing IBS-related stress",
                    "priority": 2,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Enroll in MBSR program or app",
                        "Practice daily mindfulness meditation",
                        "Use breathing exercises during symptoms",
                        "Join IBS support groups"
                    ],
                    "expected_benefit": "Reduced symptom severity and improved quality of life",
                    "timeframe": "6-8 weeks"
                }
            ],
            IBSSeverity.SEVERE: [
                {
                    "title": "Comprehensive Stress Management Program",
                    "description": "Multi-modal approach to address severe IBS impact",
                    "priority": 1,
                    "evidence_level": "High",
                    "actionable_steps": [
                        "Consider professional counseling",
                        "Explore gut-directed hypnotherapy",
                        "Implement workplace accommodations",
                        "Build strong support network"
                    ],
                    "expected_benefit": "Significant improvement in symptom control",
                    "timeframe": "8-12 weeks"
                }
            ]
        }
    
    def generate_recommendations(self, user: User, ibs_assessment: IBSAssessment, 
                               user_context: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """
        Generate personalized recommendations based on IBS severity and user context.
        
        Args:
            user: User object
            ibs_assessment: Current IBS severity assessment
            user_context: Additional context about user preferences and history
            
        Returns:
            List of personalized recommendations
        """
        recommendations = []
        
        # Get base recommendations for severity level
        diet_recs = self.diet_recommendations.get(ibs_assessment.severity, [])
        lifestyle_recs = self.lifestyle_recommendations.get(ibs_assessment.severity, [])
        
        # Add diet recommendations
        for rec_data in diet_recs:
            recommendation = Recommendation(
                type=RecommendationType.DIET,
                **rec_data
            )
            recommendations.append(recommendation)
        
        # Add lifestyle recommendations
        for rec_data in lifestyle_recs:
            recommendation = Recommendation(
                type=RecommendationType.LIFESTYLE,
                **rec_data
            )
            recommendations.append(recommendation)
        
        # Add personalized recommendations based on user data
        personalized_recs = self._generate_personalized_recommendations(user, ibs_assessment)
        recommendations.extend(personalized_recs)
        
        # Add medication recommendations if appropriate
        medication_recs = self._generate_medication_recommendations(user, ibs_assessment)
        recommendations.extend(medication_recs)
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x.priority)
        return recommendations[:8]  # Return top 8 recommendations
    
    def _generate_personalized_recommendations(self, user: User, ibs_assessment: IBSAssessment) -> List[Recommendation]:
        """Generate recommendations based on user's specific patterns."""
        recommendations = []
        
        # Analyze food reaction patterns
        food_triggers = self._analyze_food_triggers(user.id)
        if food_triggers:
            trigger_foods = ", ".join(food_triggers[:3])
            recommendations.append(Recommendation(
                type=RecommendationType.DIET,
                title=f"Avoid Identified Trigger Foods",
                description=f"Your data shows reactions to specific foods that should be avoided",
                priority=1,
                evidence_level="Personal Data",
                actionable_steps=[
                    f"Eliminate {trigger_foods} from your diet",
                    "Read food labels carefully",
                    "Find suitable alternatives",
                    "Monitor symptoms after elimination"
                ],
                expected_benefit="Reduced food-related symptom flares",
                timeframe="1-2 weeks"
            ))
        
        # Analyze symptom timing patterns
        timing_patterns = self._analyze_symptom_timing(user.id)
        if timing_patterns:
            recommendations.append(Recommendation(
                type=RecommendationType.LIFESTYLE,
                title="Optimize Meal Timing",
                description="Adjust eating schedule based on your symptom patterns",
                priority=2,
                evidence_level="Personal Data",
                actionable_steps=timing_patterns,
                expected_benefit="Better symptom predictability and control",
                timeframe="2-3 weeks"
            ))
        
        return recommendations
    
    def _generate_medication_recommendations(self, user: User, ibs_assessment: IBSAssessment) -> List[Recommendation]:
        """Generate medication-related recommendations."""
        recommendations = []
        
        if ibs_assessment.severity in [IBSSeverity.MODERATE, IBSSeverity.SEVERE]:
            recommendations.append(Recommendation(
                type=RecommendationType.MEDICATION,
                title="Consider Probiotic Supplementation",
                description="Evidence-based probiotics may help manage IBS symptoms",
                priority=3,
                evidence_level="Moderate",
                actionable_steps=[
                    "Consult healthcare provider about probiotics",
                    "Consider multi-strain formulations",
                    "Start with lower doses and increase gradually",
                    "Monitor symptoms for 4-6 weeks"
                ],
                expected_benefit="Potential improvement in gut microbiome balance",
                timeframe="4-6 weeks"
            ))
        
        if ibs_assessment.severity == IBSSeverity.SEVERE:
            recommendations.append(Recommendation(
                type=RecommendationType.MEDICATION,
                title="Discuss Prescription Options",
                description="Prescription medications may be necessary for severe IBS",
                priority=1,
                evidence_level="High",
                actionable_steps=[
                    "Schedule appointment with gastroenterologist",
                    "Discuss antispasmodic medications",
                    "Consider IBS-specific treatments",
                    "Review current medication effectiveness"
                ],
                expected_benefit="Significant symptom relief with proper medication",
                timeframe="2-4 weeks"
            ))
        
        return recommendations
    
    def _analyze_food_triggers(self, user_id: str, days: int = 60) -> List[str]:
        """Analyze user's food reaction data to identify trigger foods."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get food reactions with moderate to severe severity
        reactions = self.db.query(FoodReaction).filter(
            and_(
                FoodReaction.user_id == user_id,
                FoodReaction.reaction_occurred_at >= start_date,
                FoodReaction.severity.in_([
                    ReactionSeverityEnum.MODERATE,
                    ReactionSeverityEnum.SEVERE,
                    ReactionSeverityEnum.VERY_SEVERE
                ])
            )
        ).all()
        
        # Count reactions per food
        food_counts = {}
        for reaction in reactions:
            food = reaction.food_name.lower().strip()
            food_counts[food] = food_counts.get(food, 0) + 1
        
        # Return foods with multiple reactions
        trigger_foods = [food for food, count in food_counts.items() if count >= 2]
        return sorted(trigger_foods, key=lambda x: food_counts[x], reverse=True)
    
    def _analyze_symptom_timing(self, user_id: str, days: int = 30) -> List[str]:
        """Analyze timing patterns in symptoms to provide scheduling recommendations."""
        # This would analyze symptom logs to find patterns
        # For now, return general timing recommendations
        return [
            "Eat smaller, more frequent meals",
            "Avoid large meals 3 hours before bedtime",
            "Consider eating your largest meal at lunch",
            "Keep consistent meal times daily"
        ]
    
    def get_recommendation_progress(self, user: User, recommendation_id: str) -> Dict[str, Any]:
        """Track progress on a specific recommendation."""
        # This would track user's progress on following recommendations
        # Implementation would depend on how recommendations are stored and tracked
        return {
            "recommendation_id": recommendation_id,
            "status": "in_progress",
            "adherence_score": 0.75,
            "days_followed": 14,
            "symptom_improvement": True,
            "notes": "User reports following diet recommendations consistently"
        }
    
    def update_recommendations_based_on_feedback(self, user: User, 
                                               recommendation_id: str, 
                                               feedback: Dict[str, Any]) -> List[Recommendation]:
        """Update recommendations based on user feedback and progress."""
        # This would adjust recommendations based on user feedback
        # For now, return updated recommendations
        return self.generate_recommendations(user, feedback.get("current_assessment"))