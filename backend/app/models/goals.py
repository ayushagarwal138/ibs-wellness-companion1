"""
Goals and achievements models for user progress tracking.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class GoalTypeEnum(enum.Enum):
    """Types of goals users can set."""
    SYMPTOM_REDUCTION = "symptom_reduction"
    MEDICATION_ADHERENCE = "medication_adherence"
    DIET_TRACKING = "diet_tracking"
    EXERCISE = "exercise"
    STRESS_MANAGEMENT = "stress_management"
    SLEEP_QUALITY = "sleep_quality"
    WEIGHT_MANAGEMENT = "weight_management"
    TRIGGER_IDENTIFICATION = "trigger_identification"
    CUSTOM = "custom"


class GoalStatusEnum(enum.Enum):
    """Goal status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class GoalFrequencyEnum(enum.Enum):
    """Goal frequency."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class AchievementTypeEnum(enum.Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    STREAK = "streak"
    IMPROVEMENT = "improvement"
    CONSISTENCY = "consistency"
    DISCOVERY = "discovery"
    SPECIAL = "special"


class UserGoal(Base):
    """User-defined goals and targets."""
    __tablename__ = "user_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_type: GoalTypeEnum = Column(Enum(GoalTypeEnum), nullable=False, index=True)  # type: ignore[assignment]

    # Target metrics
    target_value = Column(Float)
    target_unit = Column(String(50))
    current_value = Column(Float, default=0.0)

    # Timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date)
    frequency: GoalFrequencyEnum = Column(Enum(GoalFrequencyEnum), nullable=False)  # type: ignore[assignment]

    # Status
    status: GoalStatusEnum = Column(
        Enum(GoalStatusEnum), default=GoalStatusEnum.ACTIVE, nullable=False
    )  # type: ignore[assignment]
    completion_percentage = Column(Float, default=0.0)

    # Configuration
    is_public = Column(Boolean, default=False)  # share with healthcare provider
    reminder_enabled = Column(Boolean, default=True)
    auto_track = Column(Boolean, default=False)  # automatically track from logs

    # Metadata
    goal_metadata = Column(JSON)  # additional goal-specific data
    tags = Column(JSON)  # user-defined tags

    # Timestamps
    completed_at = Column(DateTime)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="goals")
    progress_entries = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")


class GoalProgress(Base):
    """Track daily/periodic progress towards goals."""
    __tablename__ = "goal_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("user_goals.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Progress data
    progress_date = Column(Date, nullable=False)
    value_achieved = Column(Float, nullable=False)
    notes = Column(Text)

    # Context
    data_source = Column(String(50))  # manual, automatic, imported
    related_logs = Column(JSON)  # IDs of related symptom/diet/medication logs

    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    goal = relationship("UserGoal", back_populates="progress_entries")
    user = relationship("User")


class Achievement(Base):
    """System-defined achievements users can unlock."""
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Achievement details
    name = Column(String(100), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    achievement_type: AchievementTypeEnum = Column(
        Enum(AchievementTypeEnum), nullable=False
    )  # type: ignore[assignment]

    # Requirements
    requirements = Column(JSON, nullable=False)  # criteria for unlocking
    points_awarded = Column(Integer, default=0)

    # Display
    icon_url = Column(String(500))
    badge_color = Column(String(7))  # hex color
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary

    # Status
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)  # hidden until unlocked

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """Track which achievements users have unlocked."""
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False)

    # Achievement details
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    progress_data = Column(JSON)  # data that led to unlocking

    # User interaction
    viewed_at = Column(DateTime)
    is_favorite = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


class Milestone(Base):
    """Track important milestones in user's health journey."""
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Milestone details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    milestone_type = Column(String(50), nullable=False)  # first_log, streak, improvement, etc.

    # Data
    value = Column(Float)
    unit = Column(String(50))
    context_data = Column(JSON)

    # Significance
    importance_level = Column(Integer, default=1)  # 1-5 scale
    is_major = Column(Boolean, default=False)

    # Timestamps
    achieved_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="milestones")


class Challenge(Base):
    """System or user-created challenges."""
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # null for system challenges

    # Challenge details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text)

    # Timeline
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=False)

    # Requirements
    requirements = Column(JSON, nullable=False)
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard

    # Rewards
    points_reward = Column(Integer, default=0)
    badge_reward = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    max_participants = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by_user_id])
    participants = relationship("ChallengeParticipation", back_populates="challenge")


class ChallengeParticipation(Base):
    """Track user participation in challenges."""
    __tablename__ = "challenge_participations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Participation details
    joined_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")  # active, completed, dropped_out

    # Progress
    current_progress = Column(Float, default=0.0)
    completion_percentage = Column(Float, default=0.0)
    progress_data = Column(JSON)

    # Results
    completed_at = Column(DateTime)
    final_score = Column(Float)
    rank = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User")
