"""
Goal schemas for IBS wellness goal tracking and progress monitoring.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class GoalTypeEnum(str, Enum):
    SYMPTOM_REDUCTION = "symptom_reduction"
    DIET_ADHERENCE = "diet_adherence"
    MEDICATION_ADHERENCE = "medication_adherence"
    EXERCISE = "exercise"
    STRESS_MANAGEMENT = "stress_management"
    SLEEP_QUALITY = "sleep_quality"
    WEIGHT_MANAGEMENT = "weight_management"
    CUSTOM = "custom"


class GoalStatusEnum(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GoalBase(BaseModel):
    """Base schema for goals."""

    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Goal description"
    )
    goal_type: GoalTypeEnum = Field(..., description="Type of goal")
    priority: GoalPriorityEnum = Field(
        default=GoalPriorityEnum.MEDIUM, description="Goal priority"
    )
    target_value: Optional[float] = Field(
        None, description="Target value for measurable goals"
    )
    target_unit: Optional[str] = Field(
        None, max_length=50, description="Unit for target value"
    )
    target_date: Optional[date] = Field(None, description="Target completion date")
    is_recurring: bool = Field(default=False, description="Whether goal repeats")
    recurrence_pattern: Optional[str] = Field(
        None, description="Recurrence pattern (daily, weekly, monthly)"
    )


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""

    pass


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[GoalPriorityEnum] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = Field(None, max_length=50)
    target_date: Optional[date] = None
    status: Optional[GoalStatusEnum] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None


class GoalResponse(GoalBase):
    """Schema for goal response."""

    id: UUID
    user_id: UUID
    status: GoalStatusEnum
    current_value: Optional[float]
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """Schema for goal list response."""

    goals: List[GoalResponse]
    total: int
    active_goals: int
    completed_goals: int

    class Config:
        from_attributes = True


class GoalProgressBase(BaseModel):
    """Base schema for goal progress."""

    progress_value: float = Field(..., description="Progress value")
    notes: Optional[str] = Field(None, max_length=500, description="Progress notes")
    recorded_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="When progress was recorded"
    )


class GoalProgressCreate(GoalProgressBase):
    """Schema for creating goal progress entry."""

    goal_id: UUID = Field(..., description="Goal ID")


class GoalProgressUpdate(BaseModel):
    """Schema for updating goal progress."""

    progress_value: Optional[float] = None
    notes: Optional[str] = Field(None, max_length=500)


class GoalProgressResponse(GoalProgressBase):
    """Schema for goal progress response."""

    id: UUID
    goal_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalProgressListResponse(BaseModel):
    """Schema for goal progress list response."""

    progress_entries: List[GoalProgressResponse]
    total: int
    goal_id: UUID
    current_progress: float

    class Config:
        from_attributes = True


class GoalSummaryResponse(BaseModel):
    """Schema for goal summary response."""

    total_goals: int
    active_goals: int
    completed_goals: int
    paused_goals: int
    cancelled_goals: int
    overall_completion_rate: float
    goals_by_type: Dict[str, int]
    goals_by_priority: Dict[str, int]
    recent_achievements: List[GoalResponse]
    upcoming_deadlines: List[GoalResponse]

    class Config:
        from_attributes = True


class GoalAnalyticsResponse(BaseModel):
    """Schema for goal analytics response."""

    goal_id: UUID
    goal_title: str
    completion_trend: List[Dict[str, Any]]  # [{date, progress_value}]
    average_daily_progress: float
    estimated_completion_date: Optional[date]
    consistency_score: float  # 0-100
    milestone_achievements: List[Dict[str, Any]]
    challenges_identified: List[str]
    recommendations: List[str]

    class Config:
        from_attributes = True


class GoalMilestoneResponse(BaseModel):
    """Schema for goal milestone response."""

    id: UUID
    goal_id: UUID
    milestone_name: str
    milestone_value: float
    achieved: bool
    achieved_at: Optional[datetime]
    reward_points: int

    class Config:
        from_attributes = True


class GoalRecommendationResponse(BaseModel):
    """Schema for goal recommendations."""

    recommended_goals: List[Dict[str, Any]]
    personalization_factors: List[str]
    success_probability: Dict[str, float]
    suggested_timeline: Dict[str, str]

    class Config:
        from_attributes = True


class BulkGoalProgressCreate(BaseModel):
    """Schema for bulk goal progress creation."""

    progress_entries: List[GoalProgressCreate] = Field(..., min_items=1, max_items=50)

    @validator("progress_entries")
    def validate_unique_goals(cls, v):
        goal_ids = [entry.goal_id for entry in v]
        if len(goal_ids) != len(set(goal_ids)):
            raise ValueError(
                "Duplicate goal IDs are not allowed in bulk progress update"
            )
        return v


class BulkGoalProgressResponse(BaseModel):
    """Schema for bulk goal progress response."""

    created_entries: List[GoalProgressResponse]
    failed_entries: List[Dict[str, Any]]
    total_processed: int
    success_count: int
    failure_count: int

    class Config:
        from_attributes = True
