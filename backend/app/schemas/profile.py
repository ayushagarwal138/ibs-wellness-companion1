"""
Comprehensive profile schemas with validation for all profile sections.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from enum import Enum

from app.models.user import GenderEnum, IBSTypeEnum


class ExerciseFrequencyEnum(str, Enum):
    """Exercise frequency enumeration."""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    INTENSE = "intense"


class SeverityLevelEnum(str, Enum):
    """Severity level enumeration."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class BasicInfoUpdate(BaseModel):
    """Schema for basic information updates."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[GenderEnum] = Field(None, description="Gender")
    height_cm: Optional[float] = Field(None, gt=0, le=300, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, gt=0, le=1000, description="Weight in kilograms")
    emergency_contact_name: Optional[str] = Field(None, max_length=100, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    
    @validator('phone_number', 'emergency_contact_phone')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is not None and v.strip():
            import re
            # Enhanced phone number validation
            if not re.match(r'^\+?[\d\s\-\(\)\.]{7,20}$', v.strip()):
                raise ValueError('Invalid phone number format')
        return v.strip() if v else v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth is reasonable."""
        if v is not None:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 0 or age > 120:
                raise ValueError('Invalid date of birth')
        return v


class MedicalHistoryUpdate(BaseModel):
    """Schema for medical history updates."""
    ibs_type: Optional[IBSTypeEnum] = Field(None, description="IBS type")
    diagnosis_date: Optional[date] = Field(None, description="IBS diagnosis date")
    severity_level: Optional[SeverityLevelEnum] = Field(None, description="Current severity level")
    known_triggers: Optional[List[str]] = Field(None, description="Known trigger foods/factors")
    common_symptoms: Optional[List[str]] = Field(None, description="Common symptoms experienced")
    symptom_patterns: Optional[List[str]] = Field(None, description="Symptom patterns")
    current_medications: Optional[List[str]] = Field(None, description="Current medications")
    allergies: Optional[List[str]] = Field(None, description="Known allergies")
    other_conditions: Optional[List[str]] = Field(None, description="Other medical conditions")
    medical_notes: Optional[str] = Field(None, max_length=2000, description="Additional medical notes")
    
    @validator('diagnosis_date')
    def validate_diagnosis_date(cls, v):
        """Validate diagnosis date is not in the future."""
        if v is not None and v > date.today():
            raise ValueError('Diagnosis date cannot be in the future')
        return v
    
    @validator('known_triggers', 'common_symptoms', 'symptom_patterns', 'current_medications', 'allergies', 'other_conditions')
    def validate_lists(cls, v):
        """Validate list fields."""
        if v is not None:
            # Remove empty strings and duplicates
            cleaned = list(set([item.strip() for item in v if item and item.strip()]))
            return cleaned[:50]  # Limit to 50 items
        return v


class DietaryPreferencesUpdate(BaseModel):
    """Schema for dietary preferences updates."""
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    food_allergies: Optional[List[str]] = Field(None, description="Food allergies")
    preferred_cuisines: Optional[List[str]] = Field(None, description="Preferred cuisines")
    meal_frequency: Optional[int] = Field(None, ge=1, le=10, description="Meals per day")
    water_intake_goal: Optional[float] = Field(None, ge=0, le=10, description="Daily water intake goal in liters")
    special_diets: Optional[List[str]] = Field(None, description="Special diets followed")
    trigger_foods: Optional[List[str]] = Field(None, description="Known trigger foods")
    safe_foods: Optional[List[str]] = Field(None, description="Known safe foods")
    
    @validator('dietary_restrictions', 'food_allergies', 'preferred_cuisines', 'special_diets', 'trigger_foods', 'safe_foods')
    def validate_food_lists(cls, v):
        """Validate food-related list fields."""
        if v is not None:
            cleaned = list(set([item.strip().lower() for item in v if item and item.strip()]))
            return cleaned[:100]  # Limit to 100 items
        return v


class LifestyleFactorsUpdate(BaseModel):
    """Schema for lifestyle factors updates."""
    exercise_frequency: Optional[ExerciseFrequencyEnum] = Field(None, description="Exercise frequency")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality rating 1-10")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level rating 1-10")
    work_schedule: Optional[str] = Field(None, max_length=100, description="Work schedule description")
    smoking_status: Optional[str] = Field(None, max_length=50, description="Smoking status")
    alcohol_consumption: Optional[str] = Field(None, max_length=50, description="Alcohol consumption level")
    
    @validator('work_schedule', 'smoking_status', 'alcohol_consumption')
    def validate_text_fields(cls, v):
        """Validate text fields."""
        if v is not None:
            return v.strip()
        return v


class GoalsPreferencesUpdate(BaseModel):
    """Schema for goals and preferences updates."""
    primary_goals: Optional[List[str]] = Field(None, description="Primary health goals")
    preferred_treatments: Optional[List[str]] = Field(None, description="Preferred treatment approaches")
    communication_preferences: Optional[List[str]] = Field(None, description="Communication preferences")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="Notification settings")
    privacy_settings: Optional[Dict[str, Any]] = Field(None, description="Privacy settings")
    
    @validator('primary_goals', 'preferred_treatments', 'communication_preferences')
    def validate_preference_lists(cls, v):
        """Validate preference list fields."""
        if v is not None:
            cleaned = list(set([item.strip() for item in v if item and item.strip()]))
            return cleaned[:20]  # Limit to 20 items
        return v


class ComprehensiveProfileUpdate(BaseModel):
    """Schema for comprehensive profile updates combining all sections."""
    basic_info: Optional[BasicInfoUpdate] = None
    medical_history: Optional[MedicalHistoryUpdate] = None
    dietary_preferences: Optional[DietaryPreferencesUpdate] = None
    lifestyle_factors: Optional[LifestyleFactorsUpdate] = None
    goals_preferences: Optional[GoalsPreferencesUpdate] = None
    
    @root_validator(skip_on_failure=True)
    def validate_at_least_one_section(cls, values):
        """Ensure at least one section is provided for update."""
        sections = [v for v in values.values() if v is not None]
        if not sections:
            raise ValueError('At least one profile section must be provided for update')
        return values


class ProfileValidationResponse(BaseModel):
    """Schema for profile validation responses."""
    valid: bool
    errors: Dict[str, List[str]] = Field(default_factory=dict)
    warnings: Dict[str, List[str]] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)


class ProfileCompletionStatus(BaseModel):
    """Schema for profile completion status."""
    overall_completion: float = Field(..., ge=0, le=100, description="Overall completion percentage")
    section_completion: Dict[str, float] = Field(..., description="Completion percentage by section")
    missing_required_fields: List[str] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "overall_completion": 75.5,
                "section_completion": {
                    "basic_info": 100.0,
                    "medical_history": 80.0,
                    "dietary_preferences": 60.0,
                    "lifestyle_factors": 70.0,
                    "goals_preferences": 50.0
                },
                "missing_required_fields": ["ibs_type", "diagnosis_date"],
                "recommended_next_steps": [
                    "Complete IBS type selection",
                    "Add dietary preferences",
                    "Set health goals"
                ]
            }
        }
