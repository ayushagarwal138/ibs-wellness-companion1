"""
IBS Assessment API Endpoints

Comprehensive API endpoints for IBS risk assessment, personalized recommendations,
and health management features.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field, validator

from app.core.database import get_db
from app.models.user import User
from app.services.ibs_assessment_service import (
    IBSAssessmentService,
    IBSAssessmentResult,
)
from app.core.dependencies import get_current_user
from app.schemas.response import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ibs-assessment", tags=["IBS Assessment"])

# Initialize assessment service
assessment_service = IBSAssessmentService()


# Pydantic models for request/response
class AssessmentRequest(BaseModel):
    """Request model for IBS assessment."""

    include_recent_data: bool = Field(
        default=True, description="Include recent symptom/diet data"
    )
    assessment_type: str = Field(
        default="comprehensive", description="Type of assessment"
    )
    custom_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional assessment data"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "include_recent_data": True,
                "assessment_type": "comprehensive",
                "custom_data": {
                    "current_symptoms": {
                        "abdominal_pain": 7,
                        "bloating": 6,
                        "stress_level": 8,
                    }
                },
            }
        }
    }


class QuickAssessmentRequest(BaseModel):
    """Request model for quick IBS assessment."""

    abdominal_pain: int = Field(ge=0, le=10, description="Abdominal pain level (0-10)")
    bloating: int = Field(ge=0, le=10, description="Bloating severity (0-10)")
    bowel_movement_frequency: float = Field(
        gt=0, description="Daily bowel movement frequency"
    )
    stool_consistency: int = Field(ge=1, le=7, description="Bristol stool scale (1-7)")
    stress_level: int = Field(ge=0, le=10, description="Current stress level (0-10)")
    sleep_quality: int = Field(ge=0, le=10, description="Sleep quality (0-10)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "abdominal_pain": 6,
                "bloating": 7,
                "bowel_movement_frequency": 2.5,
                "stool_consistency": 4,
                "stress_level": 8,
                "sleep_quality": 4,
            }
        }
    }


class RecommendationFilter(BaseModel):
    """Filter parameters for recommendations."""

    recommendation_types: Optional[List[str]] = Field(
        default=None, description="Filter by recommendation types"
    )
    priority_levels: Optional[List[str]] = Field(
        default=None, description="Filter by priority levels"
    )
    implementation_timeframe: Optional[str] = Field(
        default=None, description="Filter by implementation timeframe"
    )

    @validator("recommendation_types")
    def validate_recommendation_types(cls, v):
        if v is not None:
            valid_types = [
                "dietary",
                "lifestyle",
                "medical",
                "behavioral",
                "supplement",
            ]
            for rec_type in v:
                if rec_type not in valid_types:
                    raise ValueError(f"Invalid recommendation type: {rec_type}")
        return v

    @validator("priority_levels")
    def validate_priority_levels(cls, v):
        if v is not None:
            valid_priorities = ["critical", "high", "medium", "low"]
            for priority in v:
                if priority not in valid_priorities:
                    raise ValueError(f"Invalid priority level: {priority}")
        return v


class AssessmentResponse(BaseModel):
    """Response model for IBS assessment."""

    assessment_id: str
    user_id: str
    assessment_date: datetime
    risk_assessment: Dict[str, Any]
    severity_classification: str
    confidence_score: float
    next_assessment_date: datetime
    clinical_flags: List[str]
    summary: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "example": {
                "assessment_id": "assess_123456",
                "user_id": "user_789",
                "assessment_date": "2024-01-15T10:30:00Z",
                "risk_assessment": {
                    "risk_level": "moderate",
                    "risk_score": 2.3,
                    "flare_probability": 0.35,
                },
                "severity_classification": "moderate",
                "confidence_score": 0.85,
                "next_assessment_date": "2024-02-15T10:30:00Z",
                "clinical_flags": ["stress_management_needed"],
                "summary": {
                    "primary_concerns": ["abdominal_pain", "stress"],
                    "key_recommendations": 3,
                    "immediate_actions": 1,
                },
            }
        }
    }


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""

    recommendations: Dict[str, List[Dict[str, Any]]]
    total_recommendations: int
    priority_breakdown: Dict[str, int]
    implementation_timeline: Dict[str, List[str]]

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": {
                    "dietary_plan": [
                        {
                            "id": "low_fodmap_diet",
                            "title": "Implement Low FODMAP Diet",
                            "priority": "high",
                            "expected_timeline": "2-4 weeks",
                        }
                    ]
                },
                "total_recommendations": 8,
                "priority_breakdown": {"high": 3, "medium": 4, "low": 1},
                "implementation_timeline": {
                    "immediate": ["stress_management"],
                    "short_term": ["dietary_changes"],
                    "long_term": ["lifestyle_modifications"],
                },
            }
        }
    }


@router.post("/conduct", response_model=StandardResponse[AssessmentResponse])
async def conduct_comprehensive_assessment(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Conduct comprehensive IBS assessment for the current user.

    This endpoint performs a complete IBS risk assessment including:
    - Machine learning-based risk prediction
    - Clinical rule-based assessment
    - Personalized recommendation generation
    - Severity classification
    - Clinical flag identification
    """
    try:
        logger.info(f"Starting comprehensive IBS assessment for user {current_user.id}")

        # Conduct assessment
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db, assessment_data=request.custom_data
        )

        # Create response
        response_data = AssessmentResponse(
            assessment_id=f"assess_{current_user.id}_{int(datetime.now().timestamp())}",
            user_id=assessment_result.user_id,
            assessment_date=assessment_result.assessment_date,
            risk_assessment=assessment_result.risk_assessment,
            severity_classification=assessment_result.severity_classification,
            confidence_score=assessment_result.confidence_score,
            next_assessment_date=assessment_result.next_assessment_date,
            clinical_flags=assessment_result.clinical_flags,
            summary=_create_assessment_summary(assessment_result),
        )

        # Schedule follow-up tasks in background
        background_tasks.add_task(_schedule_follow_up_tasks, assessment_result, db)

        logger.info(f"Assessment completed for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="IBS assessment completed successfully",
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Error conducting assessment for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to conduct IBS assessment: {str(e)}"
        )


@router.post("/quick-assessment", response_model=StandardResponse[AssessmentResponse])
async def conduct_quick_assessment(
    request: QuickAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Conduct quick IBS assessment based on current symptoms.

    This endpoint provides a rapid assessment based on current symptom data
    without requiring extensive historical data analysis.
    """
    try:
        logger.info(f"Starting quick IBS assessment for user {current_user.id}")

        # Convert request to assessment data format
        quick_assessment_data = {
            "current_symptoms": {
                "abdominal_pain": request.abdominal_pain,
                "bloating": request.bloating,
                "bowel_movement_frequency": request.bowel_movement_frequency,
                "stool_consistency": request.stool_consistency,
                "stress_level": request.stress_level,
                "sleep_quality": request.sleep_quality,
                "mood_score": 10 - request.stress_level,  # Inverse relationship
            }
        }

        # Conduct assessment
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db, assessment_data=quick_assessment_data
        )

        # Create response
        response_data = AssessmentResponse(
            assessment_id=f"quick_{current_user.id}_{int(datetime.now().timestamp())}",
            user_id=assessment_result.user_id,
            assessment_date=assessment_result.assessment_date,
            risk_assessment=assessment_result.risk_assessment,
            severity_classification=assessment_result.severity_classification,
            confidence_score=assessment_result.confidence_score,
            next_assessment_date=assessment_result.next_assessment_date,
            clinical_flags=assessment_result.clinical_flags,
            summary=_create_assessment_summary(assessment_result),
        )

        logger.info(f"Quick assessment completed for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="Quick IBS assessment completed successfully",
            data=response_data,
        )

    except Exception as e:
        logger.error(
            f"Error conducting quick assessment for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to conduct quick IBS assessment: {str(e)}"
        )


@router.get("/recommendations", response_model=StandardResponse[RecommendationResponse])
async def get_personalized_recommendations(
    filter_params: RecommendationFilter = Depends(),
    include_evidence: bool = Query(
        default=True, description="Include scientific evidence"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get personalized IBS management recommendations for the current user.

    Returns filtered and prioritized recommendations based on the user's
    latest assessment and current health profile.
    """
    try:
        logger.info(f"Fetching recommendations for user {current_user.id}")

        # Get latest assessment (this would typically be stored in database)
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db
        )

        # Apply filters to recommendations
        filtered_recommendations = _apply_recommendation_filters(
            assessment_result.recommendations, filter_params
        )

        # Remove evidence if not requested
        if not include_evidence:
            filtered_recommendations = _remove_evidence_from_recommendations(
                filtered_recommendations
            )

        # Create summary statistics
        total_recommendations = sum(
            len(recs) for recs in filtered_recommendations.values()
        )
        priority_breakdown = _calculate_priority_breakdown(filtered_recommendations)
        implementation_timeline = _create_implementation_timeline(
            filtered_recommendations
        )

        response_data = RecommendationResponse(
            recommendations=filtered_recommendations,
            total_recommendations=total_recommendations,
            priority_breakdown=priority_breakdown,
            implementation_timeline=implementation_timeline,
        )

        logger.info(f"Recommendations retrieved for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="Personalized recommendations retrieved successfully",
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Error fetching recommendations for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve recommendations: {str(e)}"
        )


@router.get("/risk-factors", response_model=StandardResponse[Dict[str, Any]])
async def get_risk_factors_analysis(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get detailed analysis of IBS risk factors for the current user.

    Provides insights into personal risk factors, triggers, and patterns
    that contribute to IBS symptoms.
    """
    try:
        logger.info(f"Analyzing risk factors for user {current_user.id}")

        # Conduct assessment to get risk factors
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db
        )

        # Extract and analyze risk factors
        risk_factors = assessment_result.risk_assessment.get("risk_factors", [])

        # Create detailed risk factor analysis
        risk_analysis = {
            "identified_risk_factors": risk_factors,
            "risk_level": assessment_result.risk_assessment.get(
                "risk_level", "moderate"
            ),
            "flare_probability": assessment_result.risk_assessment.get(
                "flare_probability", 0.3
            ),
            "primary_triggers": _identify_primary_triggers(assessment_result),
            "modifiable_factors": _identify_modifiable_factors(risk_factors),
            "protective_factors": _identify_protective_factors(assessment_result),
            "risk_trend": _calculate_risk_trend(current_user.id, db),
            "personalized_insights": _generate_risk_insights(assessment_result),
        }

        logger.info(f"Risk factors analysis completed for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="Risk factors analysis completed successfully",
            data=risk_analysis,
        )

    except Exception as e:
        logger.error(f"Error analyzing risk factors for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze risk factors: {str(e)}"
        )


@router.get("/severity-assessment", response_model=StandardResponse[Dict[str, Any]])
async def get_severity_assessment(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get detailed IBS severity assessment with clinical indicators.

    Provides comprehensive severity classification with supporting metrics
    and clinical indicators.
    """
    try:
        logger.info(f"Conducting severity assessment for user {current_user.id}")

        # Conduct assessment
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db
        )

        # Create detailed severity assessment
        severity_assessment = {
            "overall_severity": assessment_result.severity_classification,
            "severity_score": assessment_result.risk_assessment.get("risk_score", 0),
            "clinical_severity_score": assessment_result.risk_assessment.get(
                "clinical_severity_score", 0
            ),
            "functional_impact": assessment_result.risk_assessment.get(
                "functional_impact", "moderate"
            ),
            "psychological_impact": assessment_result.risk_assessment.get(
                "psychological_impact", "moderate"
            ),
            "quality_of_life_impact": _calculate_qol_impact(assessment_result),
            "severity_indicators": {
                "pain_severity": _extract_pain_severity(assessment_result),
                "bowel_dysfunction": _extract_bowel_dysfunction(assessment_result),
                "psychological_distress": _extract_psychological_distress(
                    assessment_result
                ),
                "functional_disability": _extract_functional_disability(
                    assessment_result
                ),
            },
            "severity_trend": _calculate_severity_trend(current_user.id, db),
            "clinical_flags": assessment_result.clinical_flags,
            "recommendations_by_severity": _categorize_recommendations_by_severity(
                assessment_result.recommendations,
                assessment_result.severity_classification,
            ),
        }

        logger.info(f"Severity assessment completed for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="Severity assessment completed successfully",
            data=severity_assessment,
        )

    except Exception as e:
        logger.error(
            f"Error conducting severity assessment for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to conduct severity assessment: {str(e)}"
        )


@router.get(
    "/assessment-history", response_model=StandardResponse[List[Dict[str, Any]]]
)
async def get_assessment_history(
    limit: int = Query(
        default=10, ge=1, le=50, description="Number of assessments to retrieve"
    ),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get historical IBS assessments for the current user.

    Provides paginated access to previous assessments for tracking
    progress and trends over time.
    """
    try:
        logger.info(f"Fetching assessment history for user {current_user.id}")

        # This would typically query stored assessments from database
        # For now, we'll return a placeholder structure
        assessment_history = [
            {
                "assessment_id": f"assess_{current_user.id}_{i}",
                "assessment_date": (
                    datetime.now() - timedelta(days=i * 30)
                ).isoformat(),
                "risk_level": ["mild", "moderate", "high"][i % 3],
                "severity_classification": ["mild", "moderate", "high"][i % 3],
                "confidence_score": 0.7 + (i * 0.05),
                "key_changes": f"Assessment {i+1} changes",
                "recommendations_count": 5 + i,
            }
            for i in range(offset, min(offset + limit, 10))
        ]

        logger.info(f"Assessment history retrieved for user {current_user.id}")

        return StandardResponse(
            success=True,
            message="Assessment history retrieved successfully",
            data=assessment_history,
        )

    except Exception as e:
        logger.error(
            f"Error fetching assessment history for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve assessment history: {str(e)}"
        )


@router.post("/update-assessment", response_model=StandardResponse[Dict[str, Any]])
async def update_assessment_data(
    assessment_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update assessment with new data and recalculate recommendations.

    Allows users to provide additional information that can improve
    the accuracy of their assessment and recommendations.
    """
    try:
        logger.info(f"Updating assessment data for user {current_user.id}")

        # Validate assessment data
        _validate_assessment_data(assessment_data)

        # Conduct updated assessment
        assessment_result = assessment_service.conduct_comprehensive_assessment(
            user_id=current_user.id, db=db, assessment_data=assessment_data
        )

        # Calculate changes from previous assessment
        changes = _calculate_assessment_changes(current_user.id, assessment_result, db)

        update_result = {
            "updated_assessment": {
                "risk_level": assessment_result.risk_assessment.get("risk_level"),
                "severity_classification": assessment_result.severity_classification,
                "confidence_score": assessment_result.confidence_score,
            },
            "changes_detected": changes,
            "new_recommendations": len(
                [
                    rec
                    for recs in assessment_result.recommendations.values()
                    for rec in recs
                ]
            ),
            "clinical_flags": assessment_result.clinical_flags,
            "next_assessment_date": assessment_result.next_assessment_date.isoformat(),
        }

        logger.info(f"Assessment data updated for user {current_user.id}")

        return StandardResponse(
            success=True, message="Assessment updated successfully", data=update_result
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating assessment for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update assessment: {str(e)}"
        )


# Helper functions
def _create_assessment_summary(
    assessment_result: IBSAssessmentResult,
) -> Dict[str, Any]:
    """Create assessment summary for response."""
    risk_assessment = assessment_result.risk_assessment
    recommendations = assessment_result.recommendations

    # Count recommendations by category
    rec_counts = {category: len(recs) for category, recs in recommendations.items()}

    # Identify primary concerns
    primary_concerns = []
    if risk_assessment.get("risk_level") in ["high", "severe"]:
        primary_concerns.append("high_risk")
    if "severe_pain_alert" in assessment_result.clinical_flags:
        primary_concerns.append("severe_pain")
    if "psychological_distress" in assessment_result.clinical_flags:
        primary_concerns.append("psychological_distress")

    return {
        "primary_concerns": primary_concerns,
        "key_recommendations": sum(rec_counts.values()),
        "immediate_actions": rec_counts.get("immediate_actions", 0),
        "risk_level": risk_assessment.get("risk_level", "moderate"),
        "flare_probability": risk_assessment.get("flare_probability", 0.3),
        "confidence_level": "high"
        if assessment_result.confidence_score > 0.8
        else "moderate",
    }


def _apply_recommendation_filters(
    recommendations: Dict[str, List[Dict[str, Any]]], filters: RecommendationFilter
) -> Dict[str, List[Dict[str, Any]]]:
    """Apply filters to recommendations."""
    filtered = {}

    for category, recs in recommendations.items():
        filtered_recs = recs.copy()

        # Filter by recommendation types
        if filters.recommendation_types:
            filtered_recs = [
                rec
                for rec in filtered_recs
                if rec.get("type") in filters.recommendation_types
            ]

        # Filter by priority levels
        if filters.priority_levels:
            filtered_recs = [
                rec
                for rec in filtered_recs
                if rec.get("priority") in filters.priority_levels
            ]

        # Filter by implementation timeframe
        if filters.implementation_timeframe:
            filtered_recs = [
                rec
                for rec in filtered_recs
                if _matches_timeframe(
                    rec.get("expected_timeline", ""), filters.implementation_timeframe
                )
            ]

        if filtered_recs:
            filtered[category] = filtered_recs

    return filtered


def _remove_evidence_from_recommendations(
    recommendations: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Remove scientific evidence from recommendations to reduce response size."""
    cleaned = {}

    for category, recs in recommendations.items():
        cleaned_recs = []
        for rec in recs:
            cleaned_rec = rec.copy()
            cleaned_rec.pop("scientific_references", None)
            cleaned_rec.pop("evidence_level", None)
            cleaned_recs.append(cleaned_rec)
        cleaned[category] = cleaned_recs

    return cleaned


def _calculate_priority_breakdown(
    recommendations: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, int]:
    """Calculate breakdown of recommendations by priority."""
    priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for recs in recommendations.values():
        for rec in recs:
            priority = rec.get("priority", "medium")
            if priority in priority_counts:
                priority_counts[priority] += 1

    return priority_counts


def _create_implementation_timeline(
    recommendations: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, List[str]]:
    """Create implementation timeline for recommendations."""
    timeline = {"immediate": [], "short_term": [], "long_term": []}

    for recs in recommendations.values():
        for rec in recs:
            timeline_str = rec.get("expected_timeline", "")
            rec_id = rec.get("id", rec.get("title", "Unknown"))

            if "immediate" in timeline_str.lower() or "within" in timeline_str.lower():
                timeline["immediate"].append(rec_id)
            elif "week" in timeline_str.lower() or "1-4" in timeline_str:
                timeline["short_term"].append(rec_id)
            else:
                timeline["long_term"].append(rec_id)

    return timeline


def _matches_timeframe(timeline_str: str, target_timeframe: str) -> bool:
    """Check if recommendation timeline matches target timeframe."""
    timeline_lower = timeline_str.lower()
    target_lower = target_timeframe.lower()

    if target_lower == "immediate":
        return "immediate" in timeline_lower or "within" in timeline_lower
    elif target_lower == "short_term":
        return "week" in timeline_lower or "month" in timeline_lower
    elif target_lower == "long_term":
        return "month" in timeline_lower or "long" in timeline_lower

    return True


def _identify_primary_triggers(assessment_result: IBSAssessmentResult) -> List[str]:
    """Identify primary IBS triggers from assessment."""
    triggers = []
    risk_factors = assessment_result.risk_assessment.get("risk_factors", [])

    for factor in risk_factors:
        if "stress" in factor.lower():
            triggers.append("stress")
        elif "diet" in factor.lower() or "food" in factor.lower():
            triggers.append("dietary_triggers")
        elif "sleep" in factor.lower():
            triggers.append("sleep_disruption")
        elif "exercise" in factor.lower():
            triggers.append("physical_activity")

    return list(set(triggers))


def _identify_modifiable_factors(risk_factors: List[str]) -> List[str]:
    """Identify modifiable risk factors."""
    modifiable = []
    modifiable_keywords = ["stress", "diet", "exercise", "sleep", "lifestyle"]

    for factor in risk_factors:
        for keyword in modifiable_keywords:
            if keyword in factor.lower():
                modifiable.append(factor)
                break

    return modifiable


def _identify_protective_factors(assessment_result: IBSAssessmentResult) -> List[str]:
    """Identify protective factors from assessment."""
    protective = []

    # This would analyze user data for protective factors
    # Placeholder implementation
    protective = ["regular_exercise", "stress_management", "dietary_awareness"]

    return protective


def _calculate_risk_trend(user_id: str, db: Session) -> str:
    """Calculate risk trend over time."""
    # Placeholder - would analyze historical assessments
    return "stable"


def _generate_risk_insights(assessment_result: IBSAssessmentResult) -> List[str]:
    """Generate personalized risk insights."""
    insights = []

    risk_level = assessment_result.risk_assessment.get("risk_level", "moderate")
    clinical_flags = assessment_result.clinical_flags

    if risk_level == "high":
        insights.append(
            "Your current risk level is elevated and requires immediate attention."
        )

    if "stress_management_needed" in clinical_flags:
        insights.append(
            "Stress appears to be a significant factor in your IBS symptoms."
        )

    if "dietary_triggers" in assessment_result.risk_assessment.get("risk_factors", []):
        insights.append("Certain foods may be triggering your symptoms.")

    return insights


def _calculate_qol_impact(assessment_result: IBSAssessmentResult) -> str:
    """Calculate quality of life impact."""
    functional_impact = assessment_result.risk_assessment.get(
        "functional_impact", "moderate"
    )
    psychological_impact = assessment_result.risk_assessment.get(
        "psychological_impact", "moderate"
    )

    if functional_impact == "severe" or psychological_impact == "severe":
        return "severe"
    elif functional_impact == "high" or psychological_impact == "high":
        return "high"
    elif functional_impact == "moderate" or psychological_impact == "moderate":
        return "moderate"
    else:
        return "mild"


def _extract_pain_severity(assessment_result: IBSAssessmentResult) -> Dict[str, Any]:
    """Extract pain severity indicators."""
    return {
        "level": "moderate",  # Placeholder
        "frequency": "daily",
        "impact_on_activities": "moderate",
    }


def _extract_bowel_dysfunction(
    assessment_result: IBSAssessmentResult,
) -> Dict[str, Any]:
    """Extract bowel dysfunction indicators."""
    return {
        "frequency_abnormality": "moderate",
        "consistency_issues": "present",
        "urgency_level": "moderate",
    }


def _extract_psychological_distress(
    assessment_result: IBSAssessmentResult,
) -> Dict[str, Any]:
    """Extract psychological distress indicators."""
    return {
        "stress_level": "elevated",
        "mood_impact": "moderate",
        "anxiety_level": "moderate",
    }


def _extract_functional_disability(
    assessment_result: IBSAssessmentResult,
) -> Dict[str, Any]:
    """Extract functional disability indicators."""
    return {
        "work_impact": "moderate",
        "social_impact": "mild",
        "daily_activities_impact": "moderate",
    }


def _calculate_severity_trend(user_id: str, db: Session) -> str:
    """Calculate severity trend over time."""
    # Placeholder - would analyze historical data
    return "stable"


def _categorize_recommendations_by_severity(
    recommendations: Dict[str, List[Dict[str, Any]]], severity: str
) -> Dict[str, List[str]]:
    """Categorize recommendations by severity level."""
    categorized = {"essential": [], "important": [], "beneficial": []}

    for recs in recommendations.values():
        for rec in recs:
            priority = rec.get("priority", "medium")
            rec_id = rec.get("id", rec.get("title", "Unknown"))

            if priority == "critical" or (severity == "severe" and priority == "high"):
                categorized["essential"].append(rec_id)
            elif priority == "high":
                categorized["important"].append(rec_id)
            else:
                categorized["beneficial"].append(rec_id)

    return categorized


def _validate_assessment_data(data: Dict[str, Any]) -> None:
    """Validate assessment data."""
    if not isinstance(data, dict):
        raise ValueError("Assessment data must be a dictionary")

    # Add specific validation rules as needed
    if "current_symptoms" in data:
        symptoms = data["current_symptoms"]
        if not isinstance(symptoms, dict):
            raise ValueError("Current symptoms must be a dictionary")


def _calculate_assessment_changes(
    user_id: str, new_assessment: IBSAssessmentResult, db: Session
) -> Dict[str, Any]:
    """Calculate changes from previous assessment."""
    # Placeholder - would compare with stored previous assessment
    return {
        "risk_level_change": "no_change",
        "severity_change": "no_change",
        "new_clinical_flags": [],
        "resolved_flags": [],
    }


async def _schedule_follow_up_tasks(
    assessment_result: IBSAssessmentResult, db: Session
):
    """Schedule follow-up tasks based on assessment results."""
    # Background task to schedule follow-ups, notifications, etc.
    logger.info(f"Scheduling follow-up tasks for user {assessment_result.user_id}")

    # Implementation would include:
    # - Scheduling next assessment reminder
    # - Setting up monitoring alerts
    # - Creating care plan updates
    pass
