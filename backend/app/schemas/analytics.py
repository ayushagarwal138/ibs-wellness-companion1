"""
Analytics schemas for IBS wellness analytics and insights.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class UserAnalyticsResponse(BaseModel):
    """Schema for user analytics response."""

    user_id: UUID
    total_symptom_logs: int
    total_diet_logs: int
    total_medication_logs: int
    avg_symptom_severity: float
    symptom_free_days: int
    most_common_symptoms: List[Dict[str, Any]]
    trigger_foods: List[Dict[str, Any]]
    medication_adherence_rate: float
    improvement_trend: str  # "improving", "stable", "declining"
    period_start: date
    period_end: date

    class Config:
        from_attributes = True


class SymptomTrendResponse(BaseModel):
    """Schema for symptom trend analysis."""

    symptom_name: str
    trend_data: List[Dict[str, Any]]  # [{date, severity, frequency}]
    average_severity: float
    frequency_per_week: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    correlation_factors: List[str]

    class Config:
        from_attributes = True


class TriggerAnalysisResponse(BaseModel):
    """Schema for trigger analysis response."""

    food_triggers: List[Dict[str, Any]]
    lifestyle_triggers: List[Dict[str, Any]]
    environmental_triggers: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    recommendations: List[str]

    class Config:
        from_attributes = True


class SystemMetricsResponse(BaseModel):
    """Schema for system-wide metrics."""

    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    total_symptom_logs: int
    total_diet_logs: int
    total_medication_logs: int
    avg_user_engagement: float
    most_logged_symptoms: List[Dict[str, Any]]
    most_common_triggers: List[Dict[str, Any]]
    generated_at: datetime

    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    """Schema for user achievements."""

    id: UUID
    user_id: UUID
    achievement_type: str
    title: str
    description: str
    icon: str
    points: int
    unlocked_at: datetime
    category: str  # "consistency", "improvement", "milestone"

    class Config:
        from_attributes = True


class UserAchievementsResponse(BaseModel):
    """Schema for user achievements list."""

    achievements: List[AchievementResponse]
    total_points: int
    current_streak: int
    next_milestone: Optional[Dict[str, Any]]
    progress_to_next: float

    class Config:
        from_attributes = True


class AnalyticsRequest(BaseModel):
    """Schema for analytics request with date range."""

    start_date: Optional[date] = Field(None, description="Start date for analysis")
    end_date: Optional[date] = Field(None, description="End date for analysis")
    include_trends: bool = Field(True, description="Include trend analysis")
    include_triggers: bool = Field(True, description="Include trigger analysis")

    model_config = {
        "json_schema_extra": {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "include_trends": True,
                "include_triggers": True,
            }
        }
    }


class WeeklyReportResponse(BaseModel):
    """Schema for weekly report."""

    week_start: date
    week_end: date
    symptom_summary: Dict[str, Any]
    diet_summary: Dict[str, Any]
    medication_summary: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]
    improvement_areas: List[str]
    achievements_earned: List[AchievementResponse]

    class Config:
        from_attributes = True


class MonthlyReportResponse(BaseModel):
    """Schema for monthly report."""

    month: int
    year: int
    overall_health_score: float
    symptom_trends: List[SymptomTrendResponse]
    trigger_analysis: TriggerAnalysisResponse
    medication_effectiveness: Dict[str, Any]
    lifestyle_impact: Dict[str, Any]
    goals_progress: List[Dict[str, Any]]
    key_achievements: List[AchievementResponse]
    recommendations: List[str]

    class Config:
        from_attributes = True


class HealthScoreResponse(BaseModel):
    """Schema for health score calculation."""

    overall_score: float  # 0-100
    symptom_score: float
    diet_score: float
    medication_score: float
    lifestyle_score: float
    trend_direction: str
    factors_affecting_score: List[str]
    improvement_suggestions: List[str]
    calculated_at: datetime

    class Config:
        from_attributes = True


class ComparisonAnalysisResponse(BaseModel):
    """Schema for period comparison analysis."""

    current_period: Dict[str, Any]
    previous_period: Dict[str, Any]
    improvements: List[str]
    regressions: List[str]
    stable_areas: List[str]
    overall_change: str  # "improved", "declined", "stable"
    change_percentage: float

    class Config:
        from_attributes = True
