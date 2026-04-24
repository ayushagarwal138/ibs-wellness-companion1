"""
User Preferences model for storing detailed personalization settings.
"""

import uuid
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column, DateTime, Float, String, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.core.database import Base


class RiskToleranceEnum(str, Enum):
    """Risk tolerance levels for personalization."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActivityLevelEnum(str, Enum):
    """Activity level enumeration."""
    SEDENTARY = "SEDENTARY"
    LIGHT = "LIGHT"
    MODERATE = "MODERATE"
    ACTIVE = "ACTIVE"
    VERY_ACTIVE = "VERY_ACTIVE"


class LearningProgressEnum(str, Enum):
    """Learning progress stages."""
    INITIAL = "INITIAL"
    COLLECTING = "COLLECTING"
    ADAPTING = "ADAPTING"
    OPTIMIZED = "OPTIMIZED"


class UserPreferences(Base):
    """User preferences model for detailed personalization settings."""
    __tablename__ = "user_preferences"

    id: "Column[uuid.UUID]" = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: "Column[uuid.UUID]" = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Personalization Settings
    risk_tolerance: "Column[Optional[RiskToleranceEnum]]" = Column(
        ENUM('LOW', 'MEDIUM', 'HIGH', name='risk_tolerance_enum'), 
        default="MEDIUM",
        nullable=False
    )
    activity_level: "Column[Optional[ActivityLevelEnum]]" = Column(
        ENUM(
            'SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', 'VERY_ACTIVE', 
            name='activity_level_enum'
        ), 
        default="MODERATE",
        nullable=False
    )
    learning_progress: "Column[Optional[LearningProgressEnum]]" = Column(
        ENUM(
            'INITIAL', 'COLLECTING', 'ADAPTING', 'OPTIMIZED', 
            name='learning_progress_enum'
        ), 
        default="INITIAL",
        nullable=False
    )

    # ML Personalization Thresholds
    high_risk_threshold = Column(Float, default=0.7, nullable=False)
    medium_risk_threshold = Column(Float, default=0.4, nullable=False)
    confidence_threshold = Column(Float, default=0.75, nullable=False)
    sensitivity_factor = Column(Float, default=1.0, nullable=False)

    # Weights for ML Models
    symptom_weight = Column(Float, default=0.4, nullable=False)
    stress_weight = Column(Float, default=0.3, nullable=False)
    sleep_weight = Column(Float, default=0.3, nullable=False)
    diet_weight = Column(Float, default=0.5, nullable=False)
    exercise_weight = Column(Float, default=0.2, nullable=False)

    # Engagement and Learning Metrics
    engagement_score = Column(Float, default=0.5, nullable=False)
    adaptation_confidence = Column(Float, default=0.5, nullable=False)
    personalization_score = Column(Float, default=0.5, nullable=False)
    data_points_collected = Column(Integer, default=0, nullable=False)

    # Dietary Preferences (JSONB for flexibility)
    dietary_restrictions = Column(JSONB, nullable=True)  # List of restrictions
    food_allergies = Column(JSONB, nullable=True)  # List of allergies
    preferred_diets = Column(JSONB, nullable=True)  # List of diet types
    trigger_foods = Column(JSONB, nullable=True)  # Identified trigger foods
    safe_foods = Column(JSONB, nullable=True)  # List of safe foods
    meal_preferences = Column(JSONB, nullable=True)  # Meal timing, frequency

    # Lifestyle Preferences
    exercise_preferences = Column(JSONB, nullable=True)  # Exercise types
    stress_management_preferences = Column(JSONB, nullable=True)  # Stress
    sleep_preferences = Column(JSONB, nullable=True)  # Sleep schedule

    # Medical Preferences
    medication_preferences = Column(JSONB, nullable=True)  # Medication
    supplement_preferences = Column(JSONB, nullable=True)  # Supplements
    healthcare_preferences = Column(JSONB, nullable=True)  # Healthcare

    # Learning Patterns (JSONB for complex data)
    symptom_patterns = Column(JSONB, nullable=True)  # Symptom patterns
    trigger_patterns = Column(JSONB, nullable=True)  # Trigger patterns
    effectiveness_scores = Column(JSONB, nullable=True)  # Effectiveness
    behavioral_patterns = Column(JSONB, nullable=True)  # Behavior patterns

    # Recommendation Preferences
    recommendation_frequency = Column(
        String(50), default="daily", nullable=False
    )
    intervention_aggressiveness = Column(
        String(50), default="moderate", nullable=False
    )
    communication_style = Column(
        String(50), default="detailed", nullable=False
    )
    notification_timing = Column(JSONB, nullable=True)  # Notification times

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=text('CURRENT_TIMESTAMP'), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=text('CURRENT_TIMESTAMP'), 
        onupdate=text('CURRENT_TIMESTAMP'), 
        nullable=False
    )
    last_learning_update = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return (
            f"<UserPreferences(user_id={self.user_id}, "
            f"learning_progress={self.learning_progress})>"
        )

    @property
    def is_well_personalized(self) -> bool:
        """Check if user has enough data for good personalization."""
        return (
            self.data_points_collected >= 50 and
            self.personalization_score >= 0.7 and
            self.learning_progress in ["ADAPTING", "OPTIMIZED"]
        )

    @property
    def needs_more_data(self) -> bool:
        """Check if more data collection is needed."""
        return (
            self.data_points_collected < 20 or
            self.personalization_score < 0.4
        )

    def update_learning_metrics(
        self, 
        new_data_points: int = 1, 
        effectiveness_feedback: Optional[float] = None
    ):
        """Update learning metrics based on new data."""
        self.data_points_collected += new_data_points
        self.last_learning_update = datetime.utcnow()
        
        # Update personalization score based on data points
        if self.data_points_collected < 10:
            self.personalization_score = 0.3
            self.learning_progress = LearningProgressEnum.INITIAL
        elif self.data_points_collected < 30:
            self.personalization_score = 0.5
            self.learning_progress = LearningProgressEnum.COLLECTING
        elif self.data_points_collected < 100:
            self.personalization_score = 0.7
            self.learning_progress = LearningProgressEnum.ADAPTING
        else:
            self.personalization_score = 0.9
            self.learning_progress = LearningProgressEnum.OPTIMIZED

        # Adjust based on effectiveness feedback
        if effectiveness_feedback is not None:
            confidence_update = (
                self.adaptation_confidence + effectiveness_feedback
            ) / 2
            self.adaptation_confidence = confidence_update
            score_multiplier = 0.8 + 0.4 * effectiveness_feedback
            self.personalization_score = min(
                1.0, self.personalization_score * score_multiplier
            )