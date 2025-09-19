"""
IBS Severity Detection Service

This service analyzes user symptoms, food reactions, and medication data
to determine IBS severity and provide personalized insights.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, desc, select

from app.models.user import User
from app.models.symptom import SymptomLog, SeverityEnum, BristolStoolTypeEnum
from app.models.diet import FoodReaction, ReactionSeverityEnum
from app.models.medication import MedicationLog, AdherenceEnum
from app.schemas.chat import IBSAssessment, IBSSeverity
from app.core.logging import StructuredLogger


class IBSDetectionService:
    """Service for detecting IBS severity based on user data patterns."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def assess_ibs_severity(self, user: User, days: int = 30) -> IBSAssessment:
        """
        Assess IBS severity based on recent user data.
        
        Args:
            user: User object
            days: Number of days to analyze (default: 30)
            
        Returns:
            IBSAssessment with severity level and supporting data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Gather data for analysis
        symptoms_data = await self._get_symptoms_data(user.id, start_date, end_date)
        food_reactions_data = await self._get_food_reactions_data(user.id, start_date, end_date)
        medication_data = await self._get_medication_data(user.id, start_date, end_date)
        
        # Calculate individual scores
        symptoms_score = self._calculate_symptoms_score(symptoms_data)
        frequency_score = self._calculate_frequency_score(symptoms_data, food_reactions_data)
        impact_score = self._calculate_impact_score(symptoms_data, medication_data)
        
        # Determine overall severity
        severity, confidence = self._determine_severity(
            symptoms_score, frequency_score, impact_score
        )
        
        # Identify key factors
        factors = self._identify_key_factors(
            symptoms_data, food_reactions_data, medication_data
        )
        
        assessment = IBSAssessment(
            severity=severity,
            confidence=confidence,
            factors=factors,
            symptoms_score=symptoms_score,
            frequency_score=frequency_score,
            impact_score=impact_score,
            last_assessment=datetime.utcnow()
        )
        
        # Log the prediction for ML tracking
        structured_logger = StructuredLogger(__name__)
        structured_logger.log_ml_prediction(
            model_name="ibs_severity_detection",
            prediction_time=0.1,  # Placeholder timing
            user_id=user.id,
            input_data={
                "symptoms_score": symptoms_score,
                "frequency_score": frequency_score,
                "impact_score": impact_score,
                "days_analyzed": days
            },
            prediction=severity.value,
            confidence_score=confidence,
            metadata={"factors": factors}
        )
        
        return assessment
    
    async def _get_symptoms_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get symptom logs for the specified period."""
        stmt = select(SymptomLog).filter(
            and_(
                SymptomLog.user_id == user_id,
                SymptomLog.logged_at >= start_date,
                SymptomLog.logged_at <= end_date
            )
        ).order_by(desc(SymptomLog.logged_at))
        
        result = await self.db.execute(stmt)
        symptoms = result.scalars().all()
        
        return [
            {
                "severity": symptom.severity,
                "bristol_scale": symptom.bristol_scale,
                "pain_level": symptom.pain_level,
                "bloating_level": symptom.bloating_level,
                "logged_at": symptom.logged_at,
                "notes": symptom.notes
            }
            for symptom in symptoms
        ]
    
    async def _get_food_reactions_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get food reaction data for the specified period."""
        stmt = select(FoodReaction).filter(
            and_(
                FoodReaction.user_id == user_id,
                FoodReaction.consumed_at >= start_date,
                FoodReaction.consumed_at <= end_date
            )
        ).order_by(desc(FoodReaction.consumed_at))
        
        result = await self.db.execute(stmt)
        reactions = result.scalars().all()
        
        return [
            {
                "food_name": reaction.food_name,
                "severity": reaction.severity,
                "symptoms": reaction.symptoms,
                "consumed_at": reaction.consumed_at,
                "reaction_time": reaction.reaction_time_hours
            }
            for reaction in reactions
        ]
    
    async def _get_medication_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get medication adherence data for the specified period."""
        stmt = select(MedicationLog).filter(
            and_(
                MedicationLog.user_id == user_id,
                MedicationLog.taken_at >= start_date,
                MedicationLog.taken_at <= end_date
            )
        ).order_by(desc(MedicationLog.taken_at))
        
        result = await self.db.execute(stmt)
        medications = result.scalars().all()
        
        return [
            {
                "medication_name": med.medication_name,
                "adherence": med.adherence,
                "effectiveness": med.effectiveness_rating,
                "taken_at": med.taken_at
            }
            for med in medications
        ]
    
    def _calculate_symptoms_score(self, symptoms_data: List[Dict]) -> float:
        """Calculate symptom severity score (0-10)."""
        if not symptoms_data:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for symptom in symptoms_data:
            # Convert severity enum to numeric value
            severity_map = {
                SeverityEnum.NONE: 0,
                SeverityEnum.MILD: 2,
                SeverityEnum.MODERATE: 5,
                SeverityEnum.SEVERE: 8,
                SeverityEnum.VERY_SEVERE: 10
            }
            
            severity_score = severity_map.get(symptom["severity"], 0)
            pain_score = symptom.get("pain_level", 0)
            bloating_score = symptom.get("bloating_level", 0)
            
            # Bristol scale contribution (abnormal = higher score)
            bristol_score = 0
            if symptom.get("bristol_scale"):
                bristol = symptom["bristol_scale"]
                if bristol in [BristolStoolTypeEnum.TYPE_1, BristolStoolTypeEnum.TYPE_2]:
                    bristol_score = 3  # Constipation
                elif bristol in [BristolStoolTypeEnum.TYPE_6, BristolStoolTypeEnum.TYPE_7]:
                    bristol_score = 3  # Diarrhea
                else:
                    bristol_score = 1  # Normal range
            
            symptom_total = (severity_score + pain_score + bloating_score + bristol_score) / 4
            total_score += symptom_total
            count += 1
        
        return min(total_score / count, 10.0) if count > 0 else 0.0
    
    def _calculate_frequency_score(self, symptoms_data: List[Dict], food_reactions_data: List[Dict]) -> float:
        """Calculate frequency score based on symptom and reaction frequency (0-10)."""
        days_with_symptoms = len(set(
            symptom["logged_at"].date() for symptom in symptoms_data
        ))
        
        days_with_reactions = len(set(
            reaction["consumed_at"].date() for reaction in food_reactions_data
        ))
        
        # Assume 30-day analysis period
        analysis_days = 30
        symptom_frequency = (days_with_symptoms / analysis_days) * 10
        reaction_frequency = (days_with_reactions / analysis_days) * 10
        
        # Weight symptoms more heavily than reactions
        frequency_score = (symptom_frequency * 0.7) + (reaction_frequency * 0.3)
        
        return min(frequency_score, 10.0)
    
    def _calculate_impact_score(self, symptoms_data: List[Dict], medication_data: List[Dict]) -> float:
        """Calculate impact score based on medication usage and symptom notes (0-10)."""
        impact_score = 0.0
        
        # Medication usage indicates higher impact
        if medication_data:
            # More medications = higher impact
            unique_medications = len(set(med["medication_name"] for med in medication_data))
            medication_score = min(unique_medications * 2, 6)
            
            # Poor adherence might indicate severity or ineffectiveness
            adherence_scores = []
            for med in medication_data:
                if med["adherence"] == AdherenceEnum.MISSED:
                    adherence_scores.append(2)
                elif med["adherence"] == AdherenceEnum.PARTIAL:
                    adherence_scores.append(1)
                else:
                    adherence_scores.append(0)
            
            avg_adherence_impact = sum(adherence_scores) / len(adherence_scores) if adherence_scores else 0
            impact_score += medication_score + avg_adherence_impact
        
        # Analyze symptom notes for impact keywords
        impact_keywords = [
            "work", "sleep", "social", "activity", "daily", "routine",
            "unable", "difficult", "interfere", "affect", "impact"
        ]
        
        note_impact = 0
        for symptom in symptoms_data:
            if symptom.get("notes"):
                notes_lower = symptom["notes"].lower()
                keyword_count = sum(1 for keyword in impact_keywords if keyword in notes_lower)
                note_impact += min(keyword_count * 0.5, 2)
        
        impact_score += note_impact / len(symptoms_data) if symptoms_data else 0
        
        return min(impact_score, 10.0)
    
    def _determine_severity(self, symptoms_score: float, frequency_score: float, impact_score: float) -> Tuple[IBSSeverity, float]:
        """Determine overall IBS severity and confidence level."""
        # Weighted average of scores
        overall_score = (symptoms_score * 0.4) + (frequency_score * 0.3) + (impact_score * 0.3)
        
        # Determine severity thresholds
        if overall_score >= 7.5:
            severity = IBSSeverity.SEVERE
            confidence = min(0.9, 0.6 + (overall_score - 7.5) * 0.1)
        elif overall_score >= 4.5:
            severity = IBSSeverity.MODERATE
            confidence = min(0.85, 0.6 + (overall_score - 4.5) * 0.08)
        elif overall_score >= 2.0:
            severity = IBSSeverity.MILD
            confidence = min(0.8, 0.5 + (overall_score - 2.0) * 0.1)
        else:
            severity = IBSSeverity.UNKNOWN
            confidence = 0.5
        
        return severity, confidence
    
    def _identify_key_factors(self, symptoms_data: List[Dict], food_reactions_data: List[Dict], medication_data: List[Dict]) -> List[str]:
        """Identify key factors contributing to IBS severity."""
        factors = []
        
        # Analyze symptom patterns
        if symptoms_data:
            avg_pain = sum(s.get("pain_level", 0) for s in symptoms_data) / len(symptoms_data)
            avg_bloating = sum(s.get("bloating_level", 0) for s in symptoms_data) / len(symptoms_data)
            
            if avg_pain >= 6:
                factors.append("High pain levels")
            if avg_bloating >= 6:
                factors.append("Significant bloating")
        
        # Analyze food reactions
        if food_reactions_data:
            severe_reactions = [r for r in food_reactions_data if r["severity"] in [ReactionSeverityEnum.SEVERE, ReactionSeverityEnum.VERY_SEVERE]]
            if len(severe_reactions) >= 3:
                factors.append("Frequent severe food reactions")
            
            # Common trigger foods
            food_counts = {}
            for reaction in food_reactions_data:
                food = reaction["food_name"].lower()
                food_counts[food] = food_counts.get(food, 0) + 1
            
            frequent_triggers = [food for food, count in food_counts.items() if count >= 2]
            if frequent_triggers:
                factors.append(f"Trigger foods identified: {', '.join(frequent_triggers[:3])}")
        
        # Analyze medication patterns
        if medication_data:
            factors.append("Currently using IBS medications")
            
            poor_adherence = [m for m in medication_data if m["adherence"] == AdherenceEnum.MISSED]
            if len(poor_adherence) > len(medication_data) * 0.3:
                factors.append("Medication adherence challenges")
        
        # Frequency factors
        if len(symptoms_data) >= 15:  # More than 15 symptom logs in 30 days
            factors.append("High symptom frequency")
        
        return factors[:5]  # Return top 5 factors
    
    def get_severity_trend(self, user: User, periods: int = 3) -> List[Dict[str, Any]]:
        """Get IBS severity trend over multiple time periods."""
        trends = []
        
        for i in range(periods):
            end_date = datetime.utcnow() - timedelta(days=i * 30)
            start_date = end_date - timedelta(days=30)
            
            # Create a temporary assessment for this period
            symptoms_data = self._get_symptoms_data(user.id, start_date, end_date)
            food_reactions_data = self._get_food_reactions_data(user.id, start_date, end_date)
            medication_data = self._get_medication_data(user.id, start_date, end_date)
            
            if symptoms_data or food_reactions_data:  # Only include periods with data
                symptoms_score = self._calculate_symptoms_score(symptoms_data)
                frequency_score = self._calculate_frequency_score(symptoms_data, food_reactions_data)
                impact_score = self._calculate_impact_score(symptoms_data, medication_data)
                
                severity, confidence = self._determine_severity(symptoms_score, frequency_score, impact_score)
                
                trends.append({
                    "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    "severity": severity.value,
                    "confidence": confidence,
                    "symptoms_score": symptoms_score,
                    "frequency_score": frequency_score,
                    "impact_score": impact_score
                })
        
        return trends