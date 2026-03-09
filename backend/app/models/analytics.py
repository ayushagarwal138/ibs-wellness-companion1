"""
Analytics models for tracking user data insights and system metrics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class UserAnalytics(Base):
    """Store user-specific analytics and insights."""
    __tablename__ = "user_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Analytics period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly

    # Symptom analytics
    total_symptom_logs = Column(Integer, default=0)
    average_symptom_severity = Column(Float)
    most_common_symptoms = Column(JSON)
    symptom_frequency_score = Column(Float)

    # Diet analytics
    total_diet_logs = Column(Integer, default=0)
    total_food_reactions = Column(Integer, default=0)
    trigger_foods_identified = Column(JSON)
    safe_foods_identified = Column(JSON)
    nutrition_adherence_score = Column(Float)

    # Medication analytics
    total_medication_logs = Column(Integer, default=0)
    medication_adherence_rate = Column(Float)
    missed_doses_count = Column(Integer, default=0)
    side_effects_reported = Column(Integer, default=0)

    # Lifestyle analytics
    average_stress_level = Column(Float)
    average_sleep_quality = Column(Float)
    exercise_frequency = Column(Float)

    # Overall health metrics
    health_improvement_score = Column(Float)
    quality_of_life_score = Column(Float)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analytics")


class SystemMetrics(Base):
    """Store system-wide metrics and performance data."""
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    metric_category = Column(String(50), nullable=False)  # performance, usage, health, etc.

    # Context
    context_data = Column(JSON)
    tags = Column(JSON)

    # Timestamps
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataInsights(Base):
    """Store AI-generated insights and patterns from user data."""
    __tablename__ = "data_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Insight details
    insight_type = Column(String(50), nullable=False)  # pattern, correlation, prediction, recommendation
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0

    # Supporting data
    supporting_data = Column(JSON)
    data_sources = Column(JSON)  # which data was used to generate this insight

    # Insight metadata
    severity = Column(String(20))  # low, medium, high, critical
    category = Column(String(50))  # symptom, diet, medication, lifestyle
    actionable = Column(Boolean, default=True)

    # User interaction
    viewed_by_user = Column(Boolean, default=False)
    user_feedback = Column(String(20))  # helpful, not_helpful, irrelevant
    dismissed = Column(Boolean, default=False)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # when this insight becomes stale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="insights")


class ReportGeneration(Base):
    """Track generated reports and their metadata."""
    __tablename__ = "report_generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Report details
    report_type = Column(String(50), nullable=False)  # symptom_summary, diet_analysis, medication_adherence, etc.
    report_title = Column(String(200), nullable=False)
    report_format = Column(String(20), nullable=False)  # pdf, json, html

    # Report parameters
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    filters_applied = Column(JSON)

    # Report content
    report_data = Column(JSON)
    file_path = Column(String(500))  # if saved as file
    file_size = Column(Integer)

    # Status
    generation_status = Column(String(20), default="pending")  # pending, generating, completed, failed
    error_message = Column(Text)

    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")
