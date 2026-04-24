"""
Symptom Logging API Endpoints

Provides endpoints for tracking and managing IBS symptoms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.models.symptom import SymptomLog, Symptom, SeverityEnum, BristolStoolTypeEnum
from app.core.dependencies import get_current_user
from app.schemas.response import StandardResponse
from app.schemas.symptom import SymptomStats

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Symptom Logs"])


# Pydantic models for request/response
class SymptomLogCreate(BaseModel):
    """Request model for creating a symptom log."""

    symptom_id: int = Field(..., description="ID of the symptom")
    severity: SeverityEnum = Field(..., description="Severity of the symptom")
    logged_at: datetime = Field(
        default_factory=datetime.now, description="When the symptom occurred"
    )
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Additional notes")
    bristol_stool_type: Optional[BristolStoolTypeEnum] = Field(
        None, description="Bristol stool type"
    )
    bowel_movement_frequency: Optional[int] = Field(
        None, description="Bowel movement frequency"
    )
    pain_location: Optional[str] = Field(None, description="Pain location")
    pain_type: Optional[str] = Field(None, description="Type of pain")
    stress_level: Optional[int] = Field(
        None, ge=1, le=10, description="Stress level (1-10)"
    )
    sleep_quality: Optional[int] = Field(
        None, ge=1, le=10, description="Sleep quality (1-10)"
    )
    exercise_minutes: Optional[int] = Field(None, description="Exercise minutes")
    potential_triggers: Optional[str] = Field(None, description="Potential triggers")

    model_config = {
        "json_schema_extra": {
            "example": {
                "symptom_id": 1,
                "severity": "moderate",
                "logged_at": "2024-05-28T14:30:00",
                "duration_minutes": 60,
                "notes": "Occurred after lunch",
                "stress_level": 6,
                "sleep_quality": 7,
            }
        }
    }


class SymptomLogResponse(BaseModel):
    """Response model for symptom log."""

    id: int
    symptom_id: int
    symptom_name: str
    severity: str
    logged_at: datetime
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    bristol_stool_type: Optional[str] = None
    bowel_movement_frequency: Optional[int] = None
    pain_location: Optional[str] = None
    pain_type: Optional[str] = None
    stress_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    exercise_minutes: Optional[int] = None
    potential_triggers: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SymptomResponse(BaseModel):
    """Response model for symptom."""

    id: int
    name: str
    description: Optional[str] = None
    category: str

    model_config = {"from_attributes": True}


@router.post("", response_model=StandardResponse[SymptomLogResponse])
async def create_symptom_log(
    log_data: SymptomLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new symptom log entry.

    This endpoint allows users to log their IBS symptoms with detailed information.
    """
    try:
        logger.info(f"Creating symptom log for user {current_user.id}")

        # Verify symptom exists
        result = await db.execute(
            select(Symptom).where(Symptom.id == log_data.symptom_id)
        )
        symptom = result.scalar_one_or_none()
        if not symptom:
            raise HTTPException(status_code=404, detail="Symptom not found")

        # Create new symptom log
        new_log = SymptomLog(
            user_id=current_user.id,
            symptom_id=log_data.symptom_id,
            severity=log_data.severity,
            logged_at=log_data.logged_at,
            duration_minutes=log_data.duration_minutes,
            notes=log_data.notes,
            bristol_stool_type=log_data.bristol_stool_type,
            bowel_movement_frequency=log_data.bowel_movement_frequency,
            pain_location=log_data.pain_location,
            pain_type=log_data.pain_type,
            stress_level=log_data.stress_level,
            sleep_quality=log_data.sleep_quality,
            exercise_minutes=log_data.exercise_minutes,
            potential_triggers=log_data.potential_triggers,
        )

        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)

        # Create response
        response_data = SymptomLogResponse(
            id=new_log.id,
            symptom_id=new_log.symptom_id,
            symptom_name=symptom.name,
            severity=new_log.severity.value,
            logged_at=new_log.logged_at,
            duration_minutes=new_log.duration_minutes,
            notes=new_log.notes,
            bristol_stool_type=new_log.bristol_stool_type.value
            if new_log.bristol_stool_type
            else None,
            bowel_movement_frequency=new_log.bowel_movement_frequency,
            pain_location=new_log.pain_location,
            pain_type=new_log.pain_type,
            stress_level=new_log.stress_level,
            sleep_quality=new_log.sleep_quality,
            exercise_minutes=new_log.exercise_minutes,
            potential_triggers=new_log.potential_triggers,
            created_at=new_log.created_at,
        )

        logger.info(f"Symptom log created for user {current_user.id}")

        return StandardResponse(
            success=True, message="Symptom log created successfully", data=response_data
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating symptom log for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create symptom log: {str(e)}"
        )


@router.get("", response_model=StandardResponse[List[SymptomLogResponse]])
async def get_symptom_logs(
    days: int = Query(30, description="Number of days to retrieve logs for"),
    limit: Optional[int] = Query(None, description="Maximum number of logs to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's symptom logs for the specified time period.

    This endpoint retrieves the user's symptom logs for the last N days.
    """
    try:
        logger.info(f"Retrieving symptom logs for user {current_user.id}")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query logs
        query = (
            select(SymptomLog, Symptom)
            .join(Symptom)
            .where(
                SymptomLog.user_id == current_user.id,
                SymptomLog.logged_at >= start_date,
                SymptomLog.logged_at <= end_date,
            )
            .order_by(desc(SymptomLog.logged_at))
        )
        
        # Apply limit if specified
        if limit is not None:
            query = query.limit(limit)
            
        result = await db.execute(query)
        logs = result.all()

        # Create response
        response_data = []
        for log, symptom in logs:
            response_data.append(
                SymptomLogResponse(
                    id=log.id,
                    symptom_id=log.symptom_id,
                    symptom_name=symptom.name,
                    severity=log.severity.value,
                    logged_at=log.logged_at,
                    duration_minutes=log.duration_minutes,
                    notes=log.notes,
                    bristol_stool_type=log.bristol_stool_type.value
                    if log.bristol_stool_type
                    else None,
                    bowel_movement_frequency=log.bowel_movement_frequency,
                    pain_location=log.pain_location,
                    pain_type=log.pain_type,
                    stress_level=log.stress_level,
                    sleep_quality=log.sleep_quality,
                    exercise_minutes=log.exercise_minutes,
                    potential_triggers=log.potential_triggers,
                    created_at=log.created_at,
                )
            )

        logger.info(
            f"Retrieved {len(response_data)} symptom logs for user {current_user.id}"
        )

        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} symptom logs",
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Error retrieving symptom logs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve symptom logs: {str(e)}"
        )


@router.get("/symptoms", response_model=StandardResponse[List[SymptomResponse]])
async def get_symptoms(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get list of available symptoms.

    This endpoint retrieves all available symptoms that can be logged.
    """
    try:
        logger.info(f"Retrieving available symptoms for user {current_user.id}")

        # Query symptoms
        logger.info("Executing symptom query...")
        result = await db.execute(select(Symptom).where(Symptom.is_active == True))
        symptoms = result.scalars().all()
        logger.info(f"Query executed, found {len(symptoms)} symptoms")

        # Create response
        response_data = []
        for symptom in symptoms:
            logger.info(f"Processing symptom: {symptom.id} - {symptom.name}")
            response_data.append(
                SymptomResponse(
                    id=symptom.id,
                    name=symptom.name,
                    description=symptom.description,
                    category=symptom.category,
                )
            )

        logger.info(f"Retrieved {len(response_data)} symptoms")

        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} symptoms",
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Error retrieving symptoms: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve symptoms: {str(e)}"
        )


@router.get("/initial", response_model=StandardResponse[List[SymptomLogResponse]])
async def get_initial_symptom_logs(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get user's initial symptom logs.

    This endpoint retrieves the user's first 5 symptom logs for display.
    """
    try:
        logger.info(f"Retrieving initial symptom logs for user {current_user.id}")

        # Query logs
        result = await db.execute(
            select(SymptomLog, Symptom)
            .join(Symptom)
            .where(SymptomLog.user_id == current_user.id)
            .order_by(desc(SymptomLog.logged_at))
            .limit(5)
        )
        logs = result.all()

        # Create response
        response_data = []
        for log, symptom in logs:
            response_data.append(
                SymptomLogResponse(
                    id=log.id,
                    symptom_id=log.symptom_id,
                    symptom_name=symptom.name,
                    severity=log.severity.value,
                    logged_at=log.logged_at,
                    duration_minutes=log.duration_minutes,
                    notes=log.notes,
                    bristol_stool_type=log.bristol_stool_type.value
                    if log.bristol_stool_type
                    else None,
                    bowel_movement_frequency=log.bowel_movement_frequency,
                    pain_location=log.pain_location,
                    pain_type=log.pain_type,
                    stress_level=log.stress_level,
                    sleep_quality=log.sleep_quality,
                    exercise_minutes=log.exercise_minutes,
                    potential_triggers=log.potential_triggers,
                    created_at=log.created_at,
                )
            )

        logger.info(
            f"Retrieved {len(response_data)} initial symptom logs "
            f"for user {current_user.id}"
        )

        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} initial symptom logs",
            data=response_data,
        )

    except Exception as e:
        logger.error(
            f"Error retrieving initial symptom logs for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve initial symptom logs: {str(e)}"
        )


@router.get("/stats/summary", response_model=StandardResponse[SymptomStats])
async def get_symptom_stats_summary(
    days: int = Query(30, description="Number of days to retrieve stats for"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated symptom statistics for the specified time period.

    Returns summary statistics including total logs, average severity,
    most common symptoms, and severity distribution.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query symptom logs for the specified period
        result = await db.execute(
            select(SymptomLog, Symptom)
            .join(Symptom)
            .where(
                SymptomLog.user_id == current_user.id,
                SymptomLog.logged_at >= start_date,
                SymptomLog.logged_at <= end_date,
            )
        )
        logs = result.all()

        if not logs:
            return StandardResponse(
                success=True,
                message="No symptom logs found for the specified period",
                data=SymptomStats(
                    total_logs=0,
                    average_severity=0.0,
                    most_common_symptoms=[],
                    severity_distribution={"none": 0, "mild": 0, "moderate": 0, "severe": 0, "very_severe": 0},
                    bristol_distribution={},
                    pain_locations={},
                    weekly_trends={},
                ),
            )

        # Calculate statistics
        total_logs = len(logs)
        severity_counts = {"none": 0, "mild": 0, "moderate": 0, "severe": 0, "very_severe": 0}
        severity_values = {"none": 0, "mild": 1, "moderate": 2, "severe": 3, "very_severe": 4}
        total_severity = 0
        symptom_counts = {}
        bristol_counts = {}
        pain_location_counts = {}
        
        # Weekly trends calculation
        weekly_data = {}
        
        for log, symptom in logs:
            severity = log.severity.value
            severity_counts[severity] += 1
            total_severity += severity_values[severity]

            symptom_name = symptom.name
            symptom_counts[symptom_name] = symptom_counts.get(symptom_name, 0) + 1
            
            # Bristol stool type distribution
            if log.bristol_stool_type:
                bristol_type = log.bristol_stool_type.value
                bristol_counts[bristol_type] = bristol_counts.get(bristol_type, 0) + 1
            
            # Pain location distribution
            if log.pain_location:
                location = log.pain_location
                pain_location_counts[location] = pain_location_counts.get(location, 0) + 1
            
            # Weekly trends (group by week with severity tracking)
            week_key = log.logged_at.strftime("%Y-W%U")
            if week_key not in weekly_data:
                weekly_data[week_key] = {"total_severity": 0, "count": 0}
            weekly_data[week_key]["total_severity"] += severity_values[severity]
            weekly_data[week_key]["count"] += 1
        
        # Calculate average severity per week
        weekly_trends = {}
        for week_key, week_data_item in weekly_data.items():
            weekly_trends[week_key] = {
                "average_severity": round(week_data_item["total_severity"] / week_data_item["count"], 2) if week_data_item["count"] > 0 else 0,
                "count": week_data_item["count"]
            }

        # Calculate average severity
        average_severity = total_severity / total_logs if total_logs > 0 else 0.0

        # Find most common symptoms (top 3)
        sorted_symptoms = sorted(
            symptom_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]
        most_common_symptoms = [symptom[0] for symptom in sorted_symptoms]

        stats = SymptomStats(
            total_logs=total_logs,
            average_severity=round(average_severity, 2),
            most_common_symptoms=most_common_symptoms,
            severity_distribution=severity_counts,
            bristol_distribution=bristol_counts,
            pain_locations=pain_location_counts,
            weekly_trends=weekly_trends,
        )

        return StandardResponse(
            success=True,
            message=f"Retrieved symptom statistics for the last {days} days",
            data=stats,
        )

    except Exception as e:
        logger.error(
            f"Error retrieving symptom statistics for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve symptom statistics: {str(e)}"
        )
