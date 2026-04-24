"""
User model for the IBS Wellness Companion.
"""

import uuid
from datetime import date, datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, Date, Float, Text, String
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class GenderEnum(str, Enum):
    """Gender enumeration."""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class IBSTypeEnum(str, Enum):
    """IBS type enumeration."""
    IBS_C = "IBS_C"  # Constipation-predominant
    IBS_D = "IBS_D"  # Diarrhea-predominant
    IBS_M = "IBS_M"  # Mixed
    IBS_U = "IBS_U"  # Unclassified


class RoleEnum(str, Enum):
    """User role enumeration."""
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: "Column[uuid.UUID]" = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    is_active: "Column[bool]" = Column(Boolean, default=True, nullable=False)
    is_verified: "Column[bool]" = Column(Boolean, default=False, nullable=False)
    role: "Column[str]" = Column(
        ENUM('PATIENT', 'DOCTOR', 'ADMIN', name='user_role'), 
        default="PATIENT", 
        nullable=False
    )

    # OAuth fields
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    github_id = Column(String(255), nullable=True, unique=True, index=True)

    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender: "Column[Optional[GenderEnum]]" = Column(
        ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY', name='gender_enum'), 
        nullable=True
    )
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(String(255), nullable=True)  # Added avatar_url field

    # Health information
    ibs_type: "Column[Optional[IBSTypeEnum]]" = Column(
        ENUM('IBS_C', 'IBS_D', 'IBS_M', 'IBS_U', name='ibs_type_enum'), 
        nullable=True
    )
    diagnosis_date = Column(Date, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    medical_notes = Column(Text, nullable=True)

    # Settings and preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    notification_preferences = Column(JSONB, nullable=True)  # JSON string
    privacy_settings = Column(JSONB, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Additional fields from database
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    # Relationships
    symptom_logs = relationship("SymptomLog", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    diet_logs = relationship("DietLog", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    food_reactions = relationship("FoodReaction", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    medication_logs = relationship("MedicationLog", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Financial relationships
    payment_methods = relationship(
        "PaymentMethod", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    billing_addresses = relationship(
        "BillingAddress", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    medication_costs = relationship(
        "MedicationCost", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Analytics relationships
    analytics = relationship("UserAnalytics", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    insights = relationship("DataInsights", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    reports = relationship("ReportGeneration", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Notification relationships
    notification_preferences_rel = relationship(
        "NotificationPreferences", 
        back_populates="user", 
        uselist=False, 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    notifications = relationship(
        "Notification", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    device_tokens = relationship("DeviceToken", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Goals and achievements relationships
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    milestones = relationship("Milestone", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Healthcare relationships
    healthcare_providers = relationship(
        "UserProvider", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="noload"
    )
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan", lazy="noload")
    medical_records = relationship("MedicalRecord", back_populates="user", cascade="all, delete-orphan", lazy="noload")

    # Personalization relationships
    preferences = relationship(
        "UserPreferences", 
        back_populates="user", 
        uselist=False, 
        cascade="all, delete-orphan", 
        lazy="noload"
    )

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{str(self.first_name)} {str(self.last_name)}"

    @property
    def age(self) -> Optional[int]:
        """Calculate user's age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            birth_date = self.date_of_birth
            age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return int(age_years)
        return None

    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI from height and weight."""
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            return float(self.weight_kg) / (height_m ** 2)
        return None

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"
