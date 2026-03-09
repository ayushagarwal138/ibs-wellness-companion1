"""
Notification models for managing user notifications and preferences.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class NotificationTypeEnum(enum.Enum):
    """Notification types."""
    MEDICATION_REMINDER = "medication_reminder"
    SYMPTOM_LOG_REMINDER = "symptom_log_reminder"
    DIET_LOG_REMINDER = "diet_log_reminder"
    APPOINTMENT_REMINDER = "appointment_reminder"
    HEALTH_INSIGHT = "health_insight"
    SYSTEM_UPDATE = "system_update"
    ACHIEVEMENT = "achievement"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    EDUCATIONAL = "educational"


class NotificationPriorityEnum(enum.Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatusEnum(enum.Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DISMISSED = "dismissed"
    FAILED = "failed"


class DeliveryChannelEnum(enum.Enum):
    """Notification delivery channels."""
    IN_APP = "in_app"
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class NotificationPreferences(Base):
    """User notification preferences."""
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # General preferences
    notifications_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format
    timezone = Column(String(50), default="UTC")

    # Channel preferences
    in_app_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)

    # Notification type preferences
    medication_reminders = Column(Boolean, default=True)
    symptom_log_reminders = Column(Boolean, default=True)
    diet_log_reminders = Column(Boolean, default=True)
    appointment_reminders = Column(Boolean, default=True)
    health_insights = Column(Boolean, default=True)
    system_updates = Column(Boolean, default=True)
    achievements = Column(Boolean, default=True)
    recommendations = Column(Boolean, default=True)
    alerts = Column(Boolean, default=True)
    educational = Column(Boolean, default=True)

    # Advanced preferences
    # Digest settings
    digest_frequency = Column(String(20), default="daily")  # never, daily, weekly
    minimum_priority: NotificationPriorityEnum = Column(
        Enum(NotificationPriorityEnum), 
        default=NotificationPriorityEnum.LOW
    )  # type: ignore[assignment]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notification_preferences_rel")


class Notification(Base):
    """Individual notifications."""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type: NotificationTypeEnum = Column(
        Enum(NotificationTypeEnum), 
        nullable=False
    )  # type: ignore[assignment]
    priority: NotificationPriorityEnum = Column(
        Enum(NotificationPriorityEnum), 
        default=NotificationPriorityEnum.MEDIUM
    )  # type: ignore[assignment]

    # Delivery settings
    delivery_channels = Column(JSON)  # list of channels to deliver to
    status: NotificationStatusEnum = Column(
        Enum(NotificationStatusEnum), 
        default=NotificationStatusEnum.PENDING
    )  # type: ignore[assignment]

    # Scheduling
    scheduled_for = Column(DateTime)  # when to send (null for immediate)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    dismissed_at = Column(DateTime)

    # Additional data
    notification_metadata = Column(JSON)  # additional data for the notification
    action_url = Column(String(500))  # deep link or URL for action
    expires_at = Column(DateTime)  # when notification becomes irrelevant

    # Related entities
    related_entity_type = Column(String(50))  # medication, symptom, diet, etc.
    related_entity_id = Column(String(100))  # ID of related entity

    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_retry_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


class NotificationTemplate(Base):
    """Templates for generating notifications."""
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template details
    name = Column(String(100), nullable=False, unique=True)
    notification_type: NotificationTypeEnum = Column(
        Enum(NotificationTypeEnum), 
        nullable=False
    )  # type: ignore[assignment]
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)

    # Default settings
    default_priority: NotificationPriorityEnum = Column(
        Enum(NotificationPriorityEnum), 
        default=NotificationPriorityEnum.MEDIUM
    )  # type: ignore[assignment]
    default_channels = Column(JSON)

    # Template variables
    required_variables = Column(JSON)  # list of required template variables
    optional_variables = Column(JSON)  # list of optional template variables

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(Base):
    """Log of notification delivery attempts."""
    __tablename__ = "notification_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)

    # Delivery attempt details
    channel: DeliveryChannelEnum = Column(Enum(DeliveryChannelEnum), nullable=False)  # type: ignore[assignment]
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, pending

    # Response details
    response_code = Column(String(10))
    response_message = Column(Text)
    external_id = Column(String(200))  # ID from external service (FCM, email provider, etc.)

    # Timestamps
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notification = relationship("Notification")


class DeviceToken(Base):
    """Store device tokens for push notifications."""
    __tablename__ = "device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Token details
    token = Column(String(500), nullable=False, unique=True)
    platform = Column(String(20), nullable=False)  # ios, android, web
    device_id = Column(String(200))
    device_name = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="device_tokens")
