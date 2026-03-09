"""
Symptom models for tracking IBS symptoms and their logs.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from typing import Optional

from app.core.database import Base


class SeverityEnum(str, enum.Enum):
    """Symptom severity enumeration."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"


class BristolStoolTypeEnum(str, enum.Enum):
    """Bristol Stool Chart types."""
    TYPE_1 = "type_1"  # Separate hard lumps
    TYPE_2 = "type_2"  # Lumpy and sausage like
    TYPE_3 = "type_3"  # A sausage shape with cracks in the surface
    TYPE_4 = "type_4"  # Like a smooth, soft sausage or snake
    TYPE_5 = "type_5"  # Soft blobs with clear-cut edges
    TYPE_6 = "type_6"  # Mushy consistency with ragged edges
    TYPE_7 = "type_7"  # Liquid consistency with no solid pieces


class Symptom(Base):
    """Symptom reference table."""

    __tablename__ = "symptoms"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Symptom details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # e.g., "digestive", "pain", "mood"
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    symptom_logs = relationship("SymptomLog", back_populates="symptom")

    def __repr__(self) -> str:
        return f"<Symptom(id={self.id}, name='{self.name}', category='{self.category}')>"


class SymptomLog(Base):
    """User symptom log entries."""

    __tablename__ = "symptom_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    symptom_id = Column(Integer, ForeignKey("symptoms.id"), nullable=False, index=True)

    # Symptom details
    severity: "Column[SeverityEnum]" = Column(Enum(SeverityEnum), nullable=False)
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes
    notes = Column(Text, nullable=True)

    # Bowel movement specific fields
    bristol_stool_type: "Column[BristolStoolTypeEnum]" = Column(Enum(BristolStoolTypeEnum), nullable=True)
    bowel_movement_frequency = Column(Integer, nullable=True)  # Times per day

    # Pain specific fields
    pain_location = Column(String(100), nullable=True)  # e.g., "lower left abdomen"
    pain_type = Column(String(50), nullable=True)  # e.g., "cramping", "sharp", "dull"

    # Context
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    sleep_quality = Column(Integer, nullable=True)  # 1-10 scale
    exercise_minutes = Column(Integer, nullable=True)  # Minutes of exercise that day

    # Triggers
    potential_triggers = Column(Text, nullable=True)  # JSON string of potential triggers

    # Timestamps
    logged_at = Column(DateTime(timezone=True), nullable=False, index=True)  # When symptom occurred
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="symptom_logs")
    symptom = relationship("Symptom", back_populates="symptom_logs")

    def __repr__(self) -> str:
        return (f"<SymptomLog(id={self.id}, user_id={self.user_id}, "
                f"symptom_id={self.symptom_id}, severity='{self.severity}')>")

    @property
    def severity_score(self) -> int:
        """Convert severity enum to numeric score."""
        severity_scores = {
            SeverityEnum.NONE: 0,
            SeverityEnum.MILD: 1,
            SeverityEnum.MODERATE: 2,
            SeverityEnum.SEVERE: 3,
            SeverityEnum.VERY_SEVERE: 4,
        }
        severity_value = SeverityEnum(self.severity)
        return severity_scores.get(severity_value, 0)

    @property
    def bristol_score(self) -> Optional[int]:
        """Convert Bristol stool type to numeric score."""
        if self.bristol_stool_type:
            return int(self.bristol_stool_type.value.split('_')[1])
        return None
