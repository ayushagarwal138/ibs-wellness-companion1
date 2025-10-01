"""
Symptom Logging API Endpoints

Provides endpoints for tracking and managing IBS symptoms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field, validator

from ...core.database import get_db
from ...models.user import User
from ...models.symptom import SymptomLog, Symptom, SeverityEnum, BristolStoolTypeEnum
from ...core.dependencies import get_current_user
from ...schemas.response import StandardResponse
from ...schemas.symptom import SymptomStats

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Symptom Logs"])


# Pydantic models for request/response
class SymptomLogCreate(BaseModel):
    """Request model for creating a symptom log."""
    symptom_id: int = Field(..., description="ID of the symptom")
    severity: SeverityEnum = Field(..., description="Severity of the symptom")
    logged_at: datetime = Field(default_factory=datetime.now, description="When the symptom occurred")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Additional notes")
    bristol_stool_type: Optional[BristolStoolTypeEnum] = Field(None, description="Bristol stool type")
    bowel_movement_frequency: Optional[int] = Field(None, description="Bowel movement frequency")
    pain_location: Optional[str] = Field(None, description="Pain location")
    pain_type: Optional[str] = Field(None, description="Type of pain")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level (1-10)")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality (1-10)")
    exercise_minutes: Optional[int] = Field(None, description="Exercise minutes")
    potential_triggers: Optional[str] = Field(None, description="Potential triggers")
    
    class Config:
        schema_extra = {
            "example": {
                "symptom_id": 1,
                "severity": "moderate",
                "logged_at": "2024-05-28T14:30:00",
                "duration_minutes": 60,
                "notes": "Occurred after lunch",
                "stress_level": 6,
                "sleep_quality": 7
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
    
    class Config:
        orm_mode = True


class SymptomResponse(BaseModel):
    """Response model for symptom."""
    id: int
    name: str
    description: Optional[str] = None
    category: str
    
    class Config:
        orm_mode = True


@router.post("", response_model=StandardResponse[SymptomLogResponse])
async def create_symptom_log(
    log_data: SymptomLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new symptom log entry.
    
    This endpoint allows users to log their IBS symptoms with detailed information.
    """
    try:
        logger.info(f"Creating symptom log for user {current_user.id}")
        
        # Verify symptom exists
        result = await db.execute(select(Symptom).where(Symptom.id == log_data.symptom_id))
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
            potential_triggers=log_data.potential_triggers
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
            bristol_stool_type=new_log.bristol_stool_type.value if new_log.bristol_stool_type else None,
            bowel_movement_frequency=new_log.bowel_movement_frequency,
            pain_location=new_log.pain_location,
            pain_type=new_log.pain_type,
            stress_level=new_log.stress_level,
            sleep_quality=new_log.sleep_quality,
            exercise_minutes=new_log.exercise_minutes,
            potential_triggers=new_log.potential_triggers,
            created_at=new_log.created_at
        )
        
        logger.info(f"Symptom log created for user {current_user.id}")
        
        return StandardResponse(
            success=True,
            message="Symptom log created successfully",
            data=response_data
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating symptom log for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create symptom log: {str(e)}"
        )


@router.get("", response_model=StandardResponse[List[SymptomLogResponse]])
async def get_symptom_logs(
    days: int = Query(30, description="Number of days to retrieve logs for"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        result = await db.execute(
            select(SymptomLog, Symptom)
            .join(Symptom)
            .where(
                SymptomLog.user_id == current_user.id,
                SymptomLog.logged_at >= start_date,
                SymptomLog.logged_at <= end_date
            )
            .order_by(desc(SymptomLog.logged_at))
        )
        logs = result.all()
        
        # Create response
        response_data = []
        for log, symptom in logs:
            response_data.append(SymptomLogResponse(
                id=log.id,
                symptom_id=log.symptom_id,
                symptom_name=symptom.name,
                severity=log.severity.value,
                logged_at=log.logged_at,
                duration_minutes=log.duration_minutes,
                notes=log.notes,
                bristol_stool_type=log.bristol_stool_type.value if log.bristol_stool_type else None,
                bowel_movement_frequency=log.bowel_movement_frequency,
                pain_location=log.pain_location,
                pain_type=log.pain_type,
                stress_level=log.stress_level,
                sleep_quality=log.sleep_quality,
                exercise_minutes=log.exercise_minutes,
                potential_triggers=log.potential_triggers,
                created_at=log.created_at
            ))
        
        logger.info(f"Retrieved {len(response_data)} symptom logs for user {current_user.id}")
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} symptom logs",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving symptom logs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve symptom logs: {str(e)}"
        )


@router.get("/symptoms", response_model=StandardResponse[List[SymptomResponse]])
async def get_symptoms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available symptoms.
    
    This endpoint retrieves all available symptoms that can be logged.
    """
    try:
        logger.info(f"Retrieving available symptoms for user {current_user.id}")
        
        # Query symptoms
        result = await db.execute(select(Symptom).where(Symptom.is_active == True))
        symptoms = result.scalars().all()
        
        # Create response
        response_data = []
        for symptom in symptoms:
            response_data.append(SymptomResponse(
                id=symptom.id,
                name=symptom.name,
                description=symptom.description,
                category=symptom.category
            ))
        
        logger.info(f"Retrieved {len(response_data)} symptoms")
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} symptoms",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving symptoms: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve symptoms: {str(e)}"
        )


@router.get("/initial", response_model=StandardResponse[List[SymptomLogResponse]])
async def get_initial_symptom_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's initial symptom logs.
    
    This endpoint retrieves the user's first 5 symptom logs for the initial symptom log display.
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
            response_data.append(SymptomLogResponse(
                id=log.id,
                symptom_id=log.symptom_id,
                symptom_name=symptom.name,
                severity=log.severity.value,
                logged_at=log.logged_at,
                duration_minutes=log.duration_minutes,
                notes=log.notes,
                bristol_stool_type=log.bristol_stool_type.value if log.bristol_stool_type else None,
                bowel_movement_frequency=log.bowel_movement_frequency,
                pain_location=log.pain_location,
                pain_type=log.pain_type,
                stress_level=log.stress_level,
                sleep_quality=log.sleep_quality,
                exercise_minutes=log.exercise_minutes,
                potential_triggers=log.potential_triggers,
                created_at=log.created_at
            ))
        
        logger.info(f"Retrieved {len(response_data)} initial symptom logs for user {current_user.id}")
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(response_data)} initial symptom logs",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving initial symptom logs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve initial symptom logs: {str(e)}"
        )


@router.get("/stats/summary", response_model=StandardResponse[SymptomStats])
async def get_symptom_stats_summary(
    days: int = Query(30, description="Number of days to retrieve stats for"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
                SymptomLog.logged_at <= end_date
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
                    most_common_symptom="None",
                    symptoms_by_type={},
                    symptoms_by_severity={"mild": 0, "moderate": 0, "severe": 0}
                )
            )
        
        # Calculate statistics
        total_logs = len(logs)
        severity_counts = {"mild": 0, "moderate": 0, "severe": 0}
        severity_values = {"mild": 1, "moderate": 2, "severe": 3}
        total_severity = 0
        symptom_counts = {}
        symptom_type_counts = {}
        
        for log, symptom in logs:
            severity = log.severity.value
            severity_counts[severity] += 1
            total_severity += severity_values[severity]
            
            symptom_name = symptom.name
            symptom_counts[symptom_name] = symptom_counts.get(symptom_name, 0) + 1
            
            # Group by symptom category/type
            symptom_category = symptom.category
            symptom_type_counts[symptom_category] = symptom_type_counts.get(symptom_category, 0) + 1
        
        # Calculate average severity
        average_severity = total_severity / total_logs if total_logs > 0 else 0.0
        
        # Find most common symptom
        most_common_symptom = max(symptom_counts, key=symptom_counts.get) if symptom_counts else "None"
        
        stats = SymptomStats(
            total_logs=total_logs,
            average_severity=round(average_severity, 2),
            most_common_symptom=most_common_symptom,
            symptoms_by_type=symptom_type_counts,
            symptoms_by_severity=severity_counts
        )
        
        return StandardResponse(
            success=True,
            message=f"Retrieved symptom statistics for the last {days} days",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error retrieving symptom statistics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve symptom statistics: {str(e)}"
        )