"""
Appointment and healthcare provider models.
"""

from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Text, ForeignKey, JSON, Boolean, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class AppointmentTypeEnum(enum.Enum):
    """Types of appointments."""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ROUTINE_CHECKUP = "routine_checkup"
    SPECIALIST = "specialist"
    TELEMEDICINE = "telemedicine"
    PROCEDURE = "procedure"
    LAB_WORK = "lab_work"
    IMAGING = "imaging"
    THERAPY = "therapy"


class AppointmentStatusEnum(enum.Enum):
    """Appointment status."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    IN_PROGRESS = "in_progress"


class ProviderTypeEnum(enum.Enum):
    """Healthcare provider types."""
    PRIMARY_CARE = "primary_care"
    GASTROENTEROLOGIST = "gastroenterologist"
    NUTRITIONIST = "nutritionist"
    DIETITIAN = "dietitian"
    THERAPIST = "therapist"
    PSYCHIATRIST = "psychiatrist"
    SPECIALIST = "specialist"
    NURSE_PRACTITIONER = "nurse_practitioner"
    PHYSICIAN_ASSISTANT = "physician_assistant"


class HealthcareProvider(Base):
    """Healthcare providers and practitioners."""
    __tablename__ = "healthcare_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Provider details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(50))  # Dr., NP, PA, etc.
    provider_type: ProviderTypeEnum = Column(Enum(ProviderTypeEnum), nullable=False)  # type: ignore[assignment]
    specialties = Column(JSON)  # list of specialties

    # Contact information
    email = Column(String(255))
    phone = Column(String(20))
    office_address = Column(JSON)  # structured address

    # Professional details
    license_number = Column(String(100))
    npi_number = Column(String(20))  # National Provider Identifier
    practice_name = Column(String(200))
    years_experience = Column(Integer)

    # System integration
    external_provider_id = Column(String(100))  # ID in external system
    accepts_telemedicine = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Metadata
    bio = Column(Text)
    languages_spoken = Column(JSON)
    insurance_accepted = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="provider")
    user_providers = relationship("UserProvider", back_populates="provider")


class UserProvider(Base):
    """Link users to their healthcare providers."""
    __tablename__ = "user_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("healthcare_providers.id"), nullable=False)

    # Relationship details
    relationship_type = Column(String(50), nullable=False)  # primary, specialist, consultant
    is_primary = Column(Boolean, default=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # null if ongoing

    # Permissions
    can_view_data = Column(Boolean, default=False)
    can_receive_reports = Column(Boolean, default=False)
    data_sharing_consent = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="healthcare_providers")
    provider = relationship("HealthcareProvider", back_populates="user_providers")


class Appointment(Base):
    """User appointments with healthcare providers."""
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("healthcare_providers.id"), nullable=False)

    # Appointment details
    appointment_type: AppointmentTypeEnum = Column(
        Enum(AppointmentTypeEnum), nullable=False
    )  # type: ignore[assignment]
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Scheduling
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    timezone = Column(String(50), default="UTC")

    # Status
    status: AppointmentStatusEnum = Column(
        Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED
    )  # type: ignore[assignment]

    # Location/Method
    is_telemedicine = Column(Boolean, default=False)
    location = Column(JSON)  # address or virtual meeting details
    meeting_link = Column(String(500))

    # Preparation
    preparation_instructions = Column(Text)
    required_documents = Column(JSON)
    fasting_required = Column(Boolean, default=False)

    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_in_days = Column(Integer)

    # Metadata
    external_appointment_id = Column(String(100))  # ID in external system
    booking_reference = Column(String(50))

    # Timestamps
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="appointments")
    provider = relationship("HealthcareProvider", back_populates="appointments")
    notes = relationship("AppointmentNote", back_populates="appointment", cascade="all, delete-orphan")
    reminders = relationship("AppointmentReminder", back_populates="appointment", cascade="all, delete-orphan")


class AppointmentNote(Base):
    """Notes and outcomes from appointments."""
    __tablename__ = "appointment_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)

    # Note details
    note_type = Column(String(50), nullable=False)  # pre_visit, visit_summary, follow_up
    title = Column(String(200))
    content = Column(Text, nullable=False)

    # Author
    created_by = Column(String(50), nullable=False)  # user, provider, system
    author_name = Column(String(200))

    # Visibility
    is_visible_to_user = Column(Boolean, default=True)
    is_confidential = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointment = relationship("Appointment", back_populates="notes")


class AppointmentReminder(Base):
    """Reminders for upcoming appointments."""
    __tablename__ = "appointment_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)

    # Reminder details
    reminder_time = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    reminder_type = Column(String(50), default="general")  # general, preparation, confirmation

    # Delivery
    delivery_method = Column(String(20), nullable=False)  # push, email, sms
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)

    # Status
    is_sent = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointment = relationship("Appointment", back_populates="reminders")


class MedicalRecord(Base):
    """Medical records and documents."""
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("healthcare_providers.id"))
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"))

    # Record details
    record_type = Column(String(50), nullable=False)  # lab_result, imaging, prescription, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Content
    file_path = Column(String(500))
    file_type = Column(String(20))
    file_size = Column(Integer)
    structured_data = Column(JSON)  # parsed/structured data from the record

    # Metadata
    record_date = Column(Date, nullable=False)
    external_record_id = Column(String(100))

    # Access control
    is_sensitive = Column(Boolean, default=False)
    access_level = Column(String(20), default="user")  # user, provider, system

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="medical_records")
    provider = relationship("HealthcareProvider")
    appointment = relationship("Appointment")
