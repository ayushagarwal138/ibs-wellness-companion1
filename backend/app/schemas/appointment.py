"""
Appointment schemas for IBS wellness appointment scheduling and management.
"""

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class AppointmentTypeEnum(str, Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ROUTINE_CHECKUP = "routine_checkup"
    SPECIALIST = "specialist"
    THERAPY = "therapy"
    DIAGNOSTIC = "diagnostic"


class AppointmentStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AppointmentBase(BaseModel):
    """Base schema for appointments."""
    title: str = Field(..., min_length=1, max_length=200, description="Appointment title")
    description: Optional[str] = Field(None, max_length=1000, description="Appointment description")
    appointment_type: AppointmentTypeEnum = Field(..., description="Type of appointment")
    appointment_date: date = Field(..., description="Date of appointment")
    appointment_time: time = Field(..., description="Time of appointment")
    duration_minutes: int = Field(default=30, ge=15, le=480, description="Duration in minutes")
    provider_name: Optional[str] = Field(None, max_length=200, description="Healthcare provider name")
    provider_specialty: Optional[str] = Field(None, max_length=100, description="Provider specialty")
    location: Optional[str] = Field(None, max_length=500, description="Appointment location")
    is_virtual: bool = Field(default=False, description="Whether appointment is virtual")
    virtual_link: Optional[str] = Field(None, description="Virtual meeting link")
    priority: AppointmentPriorityEnum = Field(default=AppointmentPriorityEnum.MEDIUM, description="Appointment priority")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    preparation_instructions: Optional[str] = Field(None, max_length=1000, description="Preparation instructions")


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""
    
    @validator('appointment_date')
    def validate_future_date(cls, v):
        if v < date.today():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    appointment_type: Optional[AppointmentTypeEnum] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    provider_name: Optional[str] = Field(None, max_length=200)
    provider_specialty: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=500)
    is_virtual: Optional[bool] = None
    virtual_link: Optional[str] = None
    priority: Optional[AppointmentPriorityEnum] = None
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = Field(None, max_length=1000)
    preparation_instructions: Optional[str] = Field(None, max_length=1000)
    
    @validator('appointment_date')
    def validate_future_date(cls, v):
        if v and v < date.today():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response."""
    id: UUID
    user_id: UUID
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    reminder_sent: bool
    
    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Schema for appointment list response."""
    appointments: List[AppointmentResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True


class AppointmentReminderResponse(BaseModel):
    """Schema for appointment reminder."""
    id: UUID
    appointment_id: UUID
    reminder_type: str  # "email", "sms", "push"
    reminder_time: datetime
    sent: bool
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AppointmentSummaryResponse(BaseModel):
    """Schema for appointment summary."""
    total_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    appointments_this_month: int
    next_appointment: Optional[AppointmentResponse]
    recent_appointments: List[AppointmentResponse]
    
    class Config:
        from_attributes = True


class AppointmentOutcomeBase(BaseModel):
    """Base schema for appointment outcomes."""
    diagnosis: Optional[str] = Field(None, max_length=500, description="Diagnosis or findings")
    treatment_plan: Optional[str] = Field(None, max_length=1000, description="Treatment plan")
    medications_prescribed: Optional[List[str]] = Field(None, description="Medications prescribed")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is required")
    follow_up_date: Optional[date] = Field(None, description="Recommended follow-up date")
    notes: Optional[str] = Field(None, max_length=1000, description="Outcome notes")
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5, description="Satisfaction rating (1-5)")


class AppointmentOutcomeCreate(AppointmentOutcomeBase):
    """Schema for creating appointment outcome."""
    appointment_id: UUID = Field(..., description="Appointment ID")


class AppointmentOutcomeUpdate(AppointmentOutcomeBase):
    """Schema for updating appointment outcome."""
    pass


class AppointmentOutcomeResponse(AppointmentOutcomeBase):
    """Schema for appointment outcome response."""
    id: UUID
    appointment_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentCalendarResponse(BaseModel):
    """Schema for calendar view of appointments."""
    date: date
    appointments: List[AppointmentResponse]
    total_appointments: int
    
    class Config:
        from_attributes = True


class AppointmentStatsResponse(BaseModel):
    """Schema for appointment statistics."""
    total_appointments: int
    appointments_by_type: Dict[str, int]
    appointments_by_status: Dict[str, int]
    appointments_by_provider: Dict[str, int]
    average_duration: float
    most_common_time_slot: str
    cancellation_rate: float
    no_show_rate: float
    satisfaction_average: Optional[float]
    
    class Config:
        from_attributes = True


class AppointmentConflictResponse(BaseModel):
    """Schema for appointment conflict detection."""
    has_conflict: bool
    conflicting_appointments: List[AppointmentResponse]
    suggested_times: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class BulkAppointmentCreate(BaseModel):
    """Schema for bulk appointment creation."""
    appointments: List[AppointmentCreate] = Field(..., min_items=1, max_items=20)
    
    @validator('appointments')
    def validate_no_time_conflicts(cls, v):
        # Check for time conflicts within the batch
        time_slots = []
        for apt in v:
            slot = (apt.appointment_date, apt.appointment_time)
            if slot in time_slots:
                raise ValueError('Time conflicts detected within the batch')
            time_slots.append(slot)
        return v


class BulkAppointmentResponse(BaseModel):
    """Schema for bulk appointment creation response."""
    created_appointments: List[AppointmentResponse]
    failed_appointments: List[Dict[str, Any]]
    total_processed: int
    success_count: int
    failure_count: int
    
    class Config:
        from_attributes = True