"""
Pydantic schemas for diet management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.diet import ReactionSeverityEnum, MealTypeEnum


class FoodReactionBase(BaseModel):
    """Base schema for food reactions."""
    food_name: str = Field(..., max_length=200, description="Name of the food")
    severity: ReactionSeverityEnum = Field(..., description="Severity of the reaction")
    symptoms: List[str] = Field(..., description="List of symptoms experienced")
    onset_time: Optional[int] = Field(None, ge=0, description="Time after eating when reaction started (minutes)")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration of reaction in minutes")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    consumed_at: Optional[datetime] = Field(None, description="When the food was consumed")


class FoodReactionCreate(FoodReactionBase):
    """Schema for creating a food reaction."""
    pass


class FoodReactionUpdate(BaseModel):
    """Schema for updating a food reaction."""
    food_name: Optional[str] = Field(None, max_length=200)
    severity: Optional[ReactionSeverityEnum] = None
    symptoms: Optional[List[str]] = None
    onset_time_minutes: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    consumed_at: Optional[datetime] = None


class FoodReactionResponse(FoodReactionBase):
    """Schema for food reaction responses."""
    id: int
    user_id: int
    reaction_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FoodReactionList(BaseModel):
    """Schema for paginated food reaction list."""
    items: List[FoodReactionResponse]
    total: int
    page: int
    size: int
    pages: int


class DietLogBase(BaseModel):
    """Base schema for diet logs."""
    meal_type: MealTypeEnum = Field(..., description="Type of meal")
    foods: List[str] = Field(..., description="List of food items consumed")
    portion_size: Optional[str] = Field(None, max_length=100, description="Portion size description")
    calories: Optional[int] = Field(None, ge=0, description="Estimated calories")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    consumed_at: Optional[datetime] = Field(None, description="When the meal was consumed")
    mood_before: Optional[int] = Field(None, ge=1, le=10, description="Mood rating 1-10")
    mood_after: Optional[int] = Field(None, ge=1, le=10, description="Mood rating 1-10")


class DietLogCreate(DietLogBase):
    """Schema for creating a diet log."""
    pass


class DietLogUpdate(BaseModel):
    """Schema for updating a diet log."""
    meal_type: Optional[str] = None
    foods: Optional[List[str]] = Field(None, min_items=1)
    portion_size: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    mood_before: Optional[int] = Field(None, ge=1, le=10)
    mood_after: Optional[int] = Field(None, ge=1, le=10)


class DietLogResponse(BaseModel):
    """Schema for diet log responses."""
    id: int
    user_id: str
    food_id: int
    meal_type: MealTypeEnum
    portion_size_g: Optional[float] = None
    portion_description: Optional[str] = None
    preparation_method: Optional[str] = None
    cooking_time_minutes: Optional[int] = None
    added_ingredients: Optional[str] = None
    eaten_at_home: Optional[bool] = None
    restaurant_name: Optional[str] = None
    meal_companions: Optional[int] = None
    stress_level_before: Optional[int] = None
    notes: Optional[str] = None
    consumed_at: datetime
    time_since_last_meal_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    foods: List[str] = Field(default_factory=list, description="List of food names for frontend compatibility")

    class Config:
        from_attributes = True
    
    @validator('user_id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string for JSON serialization."""
        if hasattr(v, 'hex'):
            return str(v)
        return str(v)


class DietLogList(BaseModel):
    """Schema for paginated diet log list."""
    items: List[DietLogResponse]
    total: int
    page: int
    size: int
    pages: int


class FoodStats(BaseModel):
    """Schema for food statistics."""
    total_reactions: int
    most_problematic_foods: List[str]
    reaction_severity_distribution: dict
    reaction_types_distribution: dict
    safe_foods: List[str]
    trigger_foods: List[str]


class DietStats(BaseModel):
    """Schema for diet statistics."""
    total_meals_logged: int
    meals_by_type: dict
    average_daily_calories: Optional[float] = None
    mood_correlation: dict
    most_consumed_foods: List[str]


class NutritionalAnalysis(BaseModel):
    """Schema for nutritional analysis."""
    date_range: dict
    total_calories: int
    macronutrients: dict  # carbs, protein, fat percentages
    micronutrients: dict
    food_groups: dict
    recommendations: List[str]


class TriggerFoodAnalysis(BaseModel):
    """Schema for trigger food analysis."""
    identified_triggers: List[dict]
    safe_alternatives: List[dict]
    elimination_suggestions: List[str]
    reintroduction_plan: List[dict]
    confidence_scores: dict
