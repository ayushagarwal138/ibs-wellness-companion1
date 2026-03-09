"""
Medication models for tracking medications and their usage logs.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from typing import Optional

from app.core.database import Base


class MedicationTypeEnum(str, enum.Enum):
    """Medication type enumeration."""
    PRESCRIPTION = "prescription"
    OTC = "otc"  # Over-the-counter
    SUPPLEMENT = "supplement"
    PROBIOTIC = "probiotic"
    HERBAL = "herbal"


class DosageUnitEnum(str, enum.Enum):
    """Dosage unit enumeration."""
    MG = "mg"
    G = "g"
    ML = "ml"
    TABLET = "tablet"
    CAPSULE = "capsule"
    TEASPOON = "teaspoon"
    TABLESPOON = "tablespoon"
    DROP = "drop"
    SPRAY = "spray"
    PATCH = "patch"


class AdherenceEnum(str, enum.Enum):
    """Medication adherence enumeration."""
    TAKEN = "taken"
    MISSED = "missed"
    PARTIAL = "partial"
    LATE = "late"


class Medication(Base):
    """Medication reference table."""

    __tablename__ = "medications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Medication details
    name = Column(String(200), nullable=False, index=True)
    generic_name = Column(String(200), nullable=True, index=True)
    brand_name = Column(String(200), nullable=True)
    medication_type: Column[MedicationTypeEnum] = Column(Enum(MedicationTypeEnum), nullable=False, index=True)

    # Classification
    category = Column(String(100), nullable=True, index=True)  # e.g., "antispasmodic", "probiotic"
    therapeutic_class = Column(String(100), nullable=True)

    # Drug information
    active_ingredients = Column(Text, nullable=True)  # JSON string
    contraindications = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    medication_logs = relationship("MedicationLog", back_populates="medication")
    medication_costs = relationship("MedicationCost", back_populates="medication")

    def __repr__(self) -> str:
        return f"<Medication(id={self.id}, name='{self.name}', type='{self.medication_type}')>"


class MedicationLog(Base):
    """User medication log entries."""

    __tablename__ = "medication_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False, index=True)

    # Dosage information
    dosage_amount = Column(Float, nullable=False)
    dosage_unit: Column[DosageUnitEnum] = Column(Enum(DosageUnitEnum), nullable=False)
    frequency_per_day = Column(Integer, nullable=True)  # How many times per day

    # Administration details
    taken_at = Column(DateTime(timezone=True), nullable=False, index=True)
    adherence: Column[AdherenceEnum] = Column(Enum(AdherenceEnum), nullable=False)

    # Context
    taken_with_food = Column(Boolean, nullable=True)
    reason_for_taking = Column(String(200), nullable=True)  # e.g., "preventive", "symptom relief"

    # Effectiveness tracking
    effectiveness_rating = Column(Integer, nullable=True)  # 1-10 scale
    side_effects_experienced = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Prescription details (if applicable)
    prescribed_by = Column(String(200), nullable=True)  # Doctor name
    prescription_date = Column(DateTime, nullable=True)
    prescription_duration_days = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="medication_logs")
    medication = relationship("Medication", back_populates="medication_logs")

    def __repr__(self) -> str:
        return (
            f"<MedicationLog(id={self.id}, user_id={self.user_id}, "
            f"medication_id={self.medication_id}, adherence='{self.adherence}')>"
        )

    @property
    def daily_dosage(self) -> Optional[float]:
        """Calculate total daily dosage."""
        if self.frequency_per_day:
            return float(self.dosage_amount * self.frequency_per_day)
        return float(self.dosage_amount)

    @property
    def is_adherent(self) -> bool:
        """Check if medication was taken as prescribed."""
        return bool(self.adherence == AdherenceEnum.TAKEN)

    @property
    def dosage_display(self) -> str:
        """Get formatted dosage string."""
        return f"{self.dosage_amount} {self.dosage_unit.value}"
