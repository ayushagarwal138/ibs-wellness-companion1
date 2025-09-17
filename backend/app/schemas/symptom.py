"""
Pydantic schemas for symptom logging.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.symptom import SeverityEnum, BristolStoolTypeEnum


class SymptomLogBase(BaseModel):
    """Base schema for symptom logs."""
    symptom_id: int = Field(..., description="ID of the symptom")
    severity: SeverityEnum = Field(..., description="Severity of the symptom")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration in minutes")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    bristol_stool_type: Optional[BristolStoolTypeEnum] = Field(None, description="Bristol stool chart type")
    bowel_movement_frequency: Optional[int] = Field(None, ge=0, le=20, description="Bowel movements per day")
    pain_location: Optional[str] = Field(None, max_length=100, description="Location of pain")
    pain_type: Optional[str] = Field(None, max_length=50, description="Type of pain")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level (1-10)")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality (1-10)")
    exercise_minutes: Optional[int] = Field(None, ge=0, description="Exercise minutes")
    potential_triggers: Optional[str] = Field(None, description="Potential triggers")
    logged_at: datetime = Field(..., description="When the symptom occurred")


class SymptomLogCreate(SymptomLogBase):
    """Schema for creating a symptom log."""
    pass


class SymptomLogUpdate(BaseModel):
    """Schema for updating a symptom log."""
    symptom_id: Optional[int] = None
    severity: Optional[SeverityEnum] = None
    bristol_stool_type: Optional[BristolStoolTypeEnum] = None
    bowel_movement_frequency: Optional[int] = Field(None, ge=0, le=20)
    pain_location: Optional[str] = Field(None, max_length=100)
    pain_type: Optional[str] = Field(None, max_length=50)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    exercise_minutes: Optional[int] = Field(None, ge=0)
    potential_triggers: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    logged_at: Optional[datetime] = None


class SymptomLogResponse(SymptomLogBase):
    """Schema for symptom log responses."""
    id: int
    user_id: UUID
    logged_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SymptomLogList(BaseModel):
    """Schema for paginated symptom log list."""
    items: List[SymptomLogResponse]
    total: int
    page: int
    size: int
    pages: int


class SymptomStats(BaseModel):
    """Schema for symptom statistics."""
    total_logs: int
    most_common_symptom: Optional[str] = None
    average_severity: Optional[float] = None
    symptoms_by_type: dict
    symptoms_by_severity: dict
    recent_trend: Optional[str] = None  # "improving", "worsening", "stable"


class SymptomAnalytics(BaseModel):
    """Schema for symptom analytics."""
    date_range: dict
    symptom_frequency: dict
    severity_trends: dict
    trigger_analysis: dict
    patterns: List[dict]