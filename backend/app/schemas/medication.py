"""
Pydantic schemas for medication tracking.
"""

from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.medication import MedicationTypeEnum, AdherenceEnum


class MedicationLogBase(BaseModel):
    """Base schema for medication logs."""

    medication_name: str = Field(
        ..., max_length=200, description="Name of the medication"
    )
    medication_type: MedicationTypeEnum = Field(..., description="Type of medication")
    dosage: str = Field(..., max_length=100, description="Dosage information")
    scheduled_time: Optional[time] = Field(
        None, description="Scheduled time for medication"
    )
    taken_at: Optional[datetime] = Field(
        None, description="When medication was actually taken"
    )
    adherence_status: AdherenceEnum = Field(..., description="Adherence status")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    side_effects: Optional[str] = Field(
        None, max_length=500, description="Any side effects experienced"
    )


class MedicationLogCreate(MedicationLogBase):
    """Schema for creating a medication log."""

    pass


class MedicationLogUpdate(BaseModel):
    """Schema for updating a medication log."""

    medication_id: Optional[int] = None
    dosage_amount: Optional[float] = Field(None, gt=0)
    dosage_unit: Optional[str] = Field(None, max_length=20)
    frequency_per_day: Optional[int] = Field(None, ge=1, le=10)
    taken_at: Optional[datetime] = None
    adherence: Optional[AdherenceEnum] = None
    taken_with_food: Optional[bool] = None
    reason_for_taking: Optional[str] = Field(None, max_length=200)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=10)
    side_effects_experienced: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)
    prescriber_name: Optional[str] = Field(None, max_length=100)
    prescription_date: Optional[datetime] = None
    prescription_duration_days: Optional[int] = Field(None, gt=0)


class MedicationLogResponse(MedicationLogBase):
    """Schema for medication log responses."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicationLogList(BaseModel):
    """Schema for paginated medication log list."""

    items: List[MedicationLogResponse]
    total: int
    page: int
    size: int
    pages: int


class MedicationStats(BaseModel):
    """Schema for medication statistics."""

    total_logs: int
    adherence_rate: float = Field(
        ..., ge=0, le=100, description="Adherence rate as percentage"
    )
    most_taken_medication: Optional[str] = None
    medications_by_type: dict
    adherence_by_status: dict
    recent_adherence_trend: Optional[str] = None  # "improving", "declining", "stable"


class MedicationSchedule(BaseModel):
    """Schema for medication schedule."""

    medication_name: str
    medication_type: MedicationTypeEnum
    dosage: str
    scheduled_times: List[time]
    frequency: str  # "daily", "twice_daily", "as_needed", etc.
    start_date: datetime
    end_date: Optional[datetime] = None
    active: bool = True


class MedicationReminder(BaseModel):
    """Schema for medication reminders."""

    id: int
    medication_name: str
    scheduled_time: time
    next_reminder: datetime
    is_active: bool
    user_id: int

    class Config:
        from_attributes = True


class AdherenceReport(BaseModel):
    """Schema for adherence reports."""

    date_range: dict
    overall_adherence_rate: float
    medication_adherence: dict
    missed_doses: List[dict]
    side_effects_reported: int
    recommendations: List[str]
