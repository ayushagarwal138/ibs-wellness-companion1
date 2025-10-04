"""
IBS Assessment Service

Provides comprehensive IBS risk assessment, severity evaluation, and
personalized recommendation generation based on user data and symptoms.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dataclasses import dataclass
import logging
import uuid

from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog, FoodReaction

logger = logging.getLogger(__name__)


@dataclass
class IBSAssessmentResult:
    """
    Data class representing the results of an IBS assessment.
    """

    assessment_id: str
    user_id: str
    assessment_date: datetime
    risk_level: str  # low, moderate, high, severe
    risk_score: float  # 0.0 to 4.0
    confidence_score: float  # 0.0 to 1.0
    severity_classification: str
    flare_probability: float  # 0.0 to 1.0
    primary_symptoms: List[str]
    trigger_foods: List[str]
    stress_factors: Dict[str, Any]
    recommendations: Dict[str, List[Dict[str, Any]]]
    clinical_flags: List[str]
    next_assessment_date: datetime
    metadata: Dict[str, Any]


class IBSAssessmentService:
    """
    Service for conducting comprehensive IBS assessments and generating
    personalized recommendations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Risk assessment thresholds
        self.risk_thresholds = {"low": 1.0, "moderate": 2.0, "high": 3.0, "severe": 4.0}

        # Severity classification criteria
        self.severity_criteria = {
            "mild": {"pain_threshold": 3, "frequency_threshold": 2},
            "moderate": {"pain_threshold": 6, "frequency_threshold": 4},
            "severe": {"pain_threshold": 8, "frequency_threshold": 6},
        }

    async def conduct_comprehensive_assessment(
        self,
        user: User,
        db: AsyncSession,
        include_recent_data: bool = True,
        assessment_type: str = "comprehensive",
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> IBSAssessmentResult:
        """
        Conduct a comprehensive IBS assessment for a user.

        Args:
            user: User object
            db: Database session
            include_recent_data: Whether to include recent symptom/diet data
            assessment_type: Type of assessment to conduct
            custom_data: Additional assessment data

        Returns:
            IBSAssessmentResult object with assessment results
        """
        try:
            assessment_id = str(uuid.uuid4())
            assessment_date = datetime.utcnow()

            # Gather user data
            user_data = await self._gather_user_data(user, db, include_recent_data)

            # Calculate risk assessment
            risk_assessment = await self._calculate_risk_assessment(
                user_data, custom_data
            )

            # Determine severity classification
            severity = await self._classify_severity(user_data)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                user, user_data, risk_assessment, severity
            )

            # Identify clinical flags
            clinical_flags = await self._identify_clinical_flags(
                user_data, risk_assessment
            )

            # Calculate next assessment date
            next_assessment = self._calculate_next_assessment_date(
                risk_assessment["risk_level"]
            )

            return IBSAssessmentResult(
                assessment_id=assessment_id,
                user_id=str(user.id),
                assessment_date=assessment_date,
                risk_level=risk_assessment["risk_level"],
                risk_score=risk_assessment["risk_score"],
                confidence_score=risk_assessment["confidence_score"],
                severity_classification=severity,
                flare_probability=risk_assessment["flare_probability"],
                primary_symptoms=user_data.get("primary_symptoms", []),
                trigger_foods=user_data.get("trigger_foods", []),
                stress_factors=user_data.get("stress_factors", {}),
                recommendations=recommendations,
                clinical_flags=clinical_flags,
                next_assessment_date=next_assessment,
                metadata={
                    "assessment_type": assessment_type,
                    "data_sources": user_data.get("data_sources", []),
                    "custom_data_included": custom_data is not None,
                },
            )

        except Exception as e:
            self.logger.error(f"Error conducting assessment for user {user.id}: {e}")
            raise

    async def conduct_quick_assessment(
        self, user: User, db: AsyncSession, quick_data: Dict[str, Any]
    ) -> IBSAssessmentResult:
        """
        Conduct a quick IBS assessment based on current symptoms.

        Args:
            user: User object
            db: Database session
            quick_data: Quick assessment data (pain, bloating, etc.)

        Returns:
            IBSAssessmentResult object with assessment results
        """
        try:
            assessment_id = str(uuid.uuid4())
            assessment_date = datetime.utcnow()

            # Calculate quick risk assessment
            risk_assessment = await self._calculate_quick_risk_assessment(quick_data)

            # Generate quick recommendations
            recommendations = await self._generate_quick_recommendations(
                quick_data, risk_assessment
            )

            return IBSAssessmentResult(
                assessment_id=assessment_id,
                user_id=str(user.id),
                assessment_date=assessment_date,
                risk_level=risk_assessment["risk_level"],
                risk_score=risk_assessment["risk_score"],
                confidence_score=0.7,  # Lower confidence for quick assessment
                severity_classification=risk_assessment["severity"],
                flare_probability=risk_assessment["flare_probability"],
                primary_symptoms=quick_data.get("primary_symptoms", []),
                trigger_foods=[],
                stress_factors={"stress_level": quick_data.get("stress_level", 0)},
                recommendations=recommendations,
                clinical_flags=[],
                next_assessment_date=datetime.utcnow() + timedelta(days=7),
                metadata={
                    "assessment_type": "quick",
                    "data_sources": ["user_input"],
                    "quick_assessment": True,
                },
            )

        except Exception as e:
            self.logger.error(f"Error conducting quick assessment: {e}")
            raise

    async def _gather_user_data(
        self, user: User, db: AsyncSession, include_recent_data: bool
    ) -> Dict[str, Any]:
        """Gather comprehensive user data for assessment."""
        data = {
            "user_profile": {
                "age": user.age,
                "gender": user.gender,
                "ibs_type": user.ibs_type,
                "diagnosis_date": user.diagnosis_date,
            },
            "data_sources": ["user_profile"],
        }

        if include_recent_data:
            # Get recent symptom logs (last 30 days)
            result = await db.execute(
                select(SymptomLog).filter(
                    SymptomLog.user_id == user.id,
                    SymptomLog.logged_at >= datetime.utcnow() - timedelta(days=30),
                )
            )
            recent_symptoms = result.scalars().all()

            # Get recent diet logs
            result = await db.execute(
                select(DietLog).filter(
                    DietLog.user_id == user.id,
                    DietLog.consumed_at >= datetime.utcnow() - timedelta(days=30),
                )
            )
            recent_diet = result.scalars().all()

            # Get recent food reactions
            result = await db.execute(
                select(FoodReaction).filter(
                    FoodReaction.user_id == user.id,
                    FoodReaction.reaction_occurred_at
                    >= datetime.utcnow() - timedelta(days=30),
                )
            )
            recent_reactions = result.scalars().all()

            data.update(
                {
                    "recent_symptoms": [
                        self._serialize_symptom(s) for s in recent_symptoms
                    ],
                    "recent_diet": [self._serialize_diet_log(d) for d in recent_diet],
                    "recent_reactions": [
                        self._serialize_reaction(r) for r in recent_reactions
                    ],
                }
            )
            data["data_sources"].extend(["symptoms", "diet", "reactions"])

        return data

    async def _calculate_risk_assessment(
        self, user_data: Dict[str, Any], custom_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk assessment."""
        risk_score = 0.0
        factors = []

        # Analyze symptom severity and frequency
        if "recent_symptoms" in user_data:
            symptom_score = self._analyze_symptom_severity(user_data["recent_symptoms"])
            risk_score += symptom_score
            factors.append("symptom_analysis")

        # Analyze food reactions
        if "recent_reactions" in user_data:
            reaction_score = self._analyze_food_reactions(user_data["recent_reactions"])
            risk_score += reaction_score
            factors.append("food_reactions")

        # Include custom data if provided
        if custom_data and "current_symptoms" in custom_data:
            custom_score = self._analyze_custom_symptoms(
                custom_data["current_symptoms"]
            )
            risk_score += custom_score * 0.5  # Weight custom data less
            factors.append("custom_input")

        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)

        # Calculate flare probability
        flare_probability = min(risk_score / 4.0, 1.0)

        # Calculate confidence based on data availability
        confidence_score = self._calculate_confidence(factors, user_data)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flare_probability": flare_probability,
            "confidence_score": confidence_score,
            "contributing_factors": factors,
        }

    async def _calculate_quick_risk_assessment(
        self, quick_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate risk assessment from quick assessment data."""
        # Simple scoring based on quick assessment inputs
        pain_score = quick_data.get("abdominal_pain", 0) / 10.0
        bloating_score = quick_data.get("bloating", 0) / 10.0
        stress_score = quick_data.get("stress_level", 0) / 10.0

        # Calculate overall risk score
        risk_score = (pain_score + bloating_score + stress_score * 0.5) * 2.0

        # Determine risk level and severity
        risk_level = self._determine_risk_level(risk_score)
        severity = self._determine_quick_severity(quick_data)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "severity": severity,
            "flare_probability": min(risk_score / 4.0, 1.0),
        }

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score."""
        if risk_score < self.risk_thresholds["low"]:
            return "low"
        elif risk_score < self.risk_thresholds["moderate"]:
            return "moderate"
        elif risk_score < self.risk_thresholds["high"]:
            return "high"
        else:
            return "severe"

    def _analyze_symptom_severity(self, symptoms: List[Dict[str, Any]]) -> float:
        """Analyze symptom severity and return risk score contribution."""
        if not symptoms:
            return 0.0

        total_severity = sum(s.get("severity_level", 0) for s in symptoms)
        avg_severity = total_severity / len(symptoms)

        # Convert to risk score (0-2.0 range)
        return min(avg_severity / 5.0 * 2.0, 2.0)

    def _analyze_food_reactions(self, reactions: List[Dict[str, Any]]) -> float:
        """Analyze food reactions and return risk score contribution."""
        if not reactions:
            return 0.0

        severe_reactions = sum(
            1 for r in reactions if r.get("severity") in ["moderate", "severe"]
        )

        # Higher score for more severe reactions
        return min(severe_reactions / 10.0 * 1.5, 1.5)

    def _analyze_custom_symptoms(self, custom_symptoms: Dict[str, Any]) -> float:
        """Analyze custom symptom data."""
        pain = custom_symptoms.get("abdominal_pain", 0)
        bloating = custom_symptoms.get("bloating", 0)
        stress = custom_symptoms.get("stress_level", 0)

        return (pain + bloating + stress * 0.5) / 25.0 * 2.0

    def _calculate_confidence(
        self, factors: List[str], user_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on available data."""
        base_confidence = 0.5

        # Increase confidence based on data sources
        if "symptom_analysis" in factors:
            base_confidence += 0.2
        if "food_reactions" in factors:
            base_confidence += 0.15
        if "custom_input" in factors:
            base_confidence += 0.1

        # Adjust based on data recency and volume
        if "recent_symptoms" in user_data:
            symptom_count = len(user_data["recent_symptoms"])
            if symptom_count > 10:
                base_confidence += 0.05

        return min(base_confidence, 1.0)

    async def _classify_severity(self, user_data: Dict[str, Any]) -> str:
        """Classify IBS severity based on user data."""
        if "recent_symptoms" not in user_data:
            return "mild"

        symptoms = user_data["recent_symptoms"]
        if not symptoms:
            return "mild"

        avg_pain = sum(
            s.get("severity_level", 0)
            for s in symptoms
            if s.get("symptom_name") == "abdominal_pain"
        ) / max(1, len(symptoms))

        symptom_frequency = len(symptoms) / 30  # Daily frequency

        if (
            avg_pain >= self.severity_criteria["severe"]["pain_threshold"]
            and symptom_frequency
            >= self.severity_criteria["severe"]["frequency_threshold"]
        ):
            return "severe"
        elif (
            avg_pain >= self.severity_criteria["moderate"]["pain_threshold"]
            and symptom_frequency
            >= self.severity_criteria["moderate"]["frequency_threshold"]
        ):
            return "moderate"
        else:
            return "mild"

    def _determine_quick_severity(self, quick_data: Dict[str, Any]) -> str:
        """Determine severity from quick assessment data."""
        pain = quick_data.get("abdominal_pain", 0)
        bloating = quick_data.get("bloating", 0)

        avg_severity = (pain + bloating) / 2

        if avg_severity >= 7:
            return "severe"
        elif avg_severity >= 4:
            return "moderate"
        else:
            return "mild"

    async def _generate_recommendations(
        self,
        user: User,
        user_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        severity: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate personalized recommendations."""
        recommendations = {
            "dietary_plan": [],
            "lifestyle_modifications": [],
            "stress_management": [],
            "medical_consultation": [],
        }

        # Generate dietary recommendations
        if risk_assessment["risk_level"] in ["moderate", "high", "severe"]:
            recommendations["dietary_plan"].append(
                {
                    "id": "low_fodmap_diet",
                    "title": "Implement Low FODMAP Diet",
                    "description": "Follow a structured low FODMAP elimination diet",
                    "priority": "high",
                    "expected_timeline": "2-4 weeks",
                    "evidence_level": "strong",
                }
            )

        # Generate lifestyle recommendations
        recommendations["lifestyle_modifications"].append(
            {
                "id": "regular_exercise",
                "title": "Regular Physical Activity",
                "description": "Engage in moderate exercise 3-4 times per week",
                "priority": "medium",
                "expected_timeline": "ongoing",
                "evidence_level": "moderate",
            }
        )

        # Generate stress management recommendations
        if "stress_factors" in user_data:
            recommendations["stress_management"].append(
                {
                    "id": "mindfulness_meditation",
                    "title": "Mindfulness and Meditation",
                    "description": "Practice daily mindfulness or meditation",
                    "priority": "high",
                    "expected_timeline": "2-3 weeks",
                    "evidence_level": "strong",
                }
            )

        # Medical consultation recommendations
        if severity == "severe" or risk_assessment["risk_level"] == "severe":
            recommendations["medical_consultation"].append(
                {
                    "id": "gastroenterologist_referral",
                    "title": "Gastroenterologist Consultation",
                    "description": "Schedule appointment with GI specialist",
                    "priority": "high",
                    "expected_timeline": "immediate",
                    "evidence_level": "clinical_guideline",
                }
            )

        return recommendations

    async def _generate_quick_recommendations(
        self, quick_data: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate quick recommendations based on immediate symptoms."""
        recommendations = {"immediate_relief": [], "short_term_management": []}

        # Immediate relief recommendations
        if quick_data.get("abdominal_pain", 0) > 6:
            recommendations["immediate_relief"].append(
                {
                    "id": "heat_therapy",
                    "title": "Apply Heat Therapy",
                    "description": "Use heating pad on abdomen for 15-20 minutes",
                    "priority": "high",
                    "expected_timeline": "immediate",
                }
            )

        # Short-term management
        if quick_data.get("stress_level", 0) > 7:
            recommendations["short_term_management"].append(
                {
                    "id": "breathing_exercises",
                    "title": "Deep Breathing Exercises",
                    "description": "Practice 4-7-8 breathing technique",
                    "priority": "high",
                    "expected_timeline": "5-10 minutes",
                }
            )

        return recommendations

    async def _identify_clinical_flags(
        self, user_data: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Identify clinical flags that require attention."""
        flags = []

        if risk_assessment["risk_level"] == "severe":
            flags.append("severe_symptoms_require_medical_attention")

        if risk_assessment["flare_probability"] > 0.7:
            flags.append("high_flare_risk")

        # Check for stress management needs
        if "stress_factors" in user_data:
            stress_level = user_data["stress_factors"].get("stress_level", 0)
            if stress_level > 7:
                flags.append("stress_management_needed")

        return flags

    def _calculate_next_assessment_date(self, risk_level: str) -> datetime:
        """Calculate when the next assessment should be conducted."""
        days_mapping = {"low": 30, "moderate": 14, "high": 7, "severe": 3}

        days = days_mapping.get(risk_level, 14)
        return datetime.utcnow() + timedelta(days=days)

    def _serialize_symptom(self, symptom: SymptomLog) -> Dict[str, Any]:
        """Serialize symptom log for assessment."""
        return {
            "symptom_name": symptom.symptom.name if symptom.symptom else "unknown",
            "severity_level": symptom.severity_level,
            "logged_at": symptom.logged_at.isoformat(),
            "notes": symptom.notes,
        }

    def _serialize_diet_log(self, diet_log: DietLog) -> Dict[str, Any]:
        """Serialize diet log for assessment."""
        return {
            "food_name": diet_log.food.name if diet_log.food else "unknown",
            "meal_type": diet_log.meal_type,
            "portion_size": diet_log.portion_size_g,
            "logged_at": diet_log.logged_at.isoformat(),
        }

    def _serialize_reaction(self, reaction: FoodReaction) -> Dict[str, Any]:
        """Serialize food reaction for assessment."""
        return {
            "food_name": reaction.food.name if reaction.food else "unknown",
            "severity": reaction.severity,
            "symptoms": reaction.symptoms,
            "reaction_date": reaction.reaction_date.isoformat(),
            "confidence_level": reaction.confidence_level,
        }
