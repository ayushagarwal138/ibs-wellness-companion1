"""
User schemas for request/response validation.
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import GenderEnum, IBSTypeEnum


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)  # Changed from gt=0 to ge=50
    weight_kg: Optional[float] = Field(None, ge=20, le=500)  # Changed from gt=0 and le=1000 to ge=20, le=500
    ibs_type: Optional[IBSTypeEnum] = None
    diagnosis_date: Optional[date] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    allergies: Optional[str] = Field(None, max_length=500)
    current_medications: Optional[str] = Field(None, max_length=1000)
    medical_notes: Optional[str] = Field(None, max_length=2000)
    notification_preferences: Optional[str] = None  # JSON string
    privacy_settings: Optional[str] = None  # JSON string
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is not None and v.strip():
            # Basic phone number validation (can be enhanced)
            import re
            if not re.match(r'^\+?[\d\s\-\(\)]+$', v):
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth is not in the future."""
        if v is not None:
            from datetime import date
            if v > date.today():
                raise ValueError('Date of birth cannot be in the future')
        return v


class UserInDB(UserBase):
    """User schema as stored in database."""
    id: str  # Changed to str to handle UUID
    is_active: bool
    is_verified: bool  # Changed from email_verified to match the model
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    # Profile fields
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    
    # IBS-specific fields
    ibs_type: Optional[IBSTypeEnum]
    diagnosis_date: Optional[date]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    allergies: Optional[str]
    current_medications: Optional[str]
    medical_notes: Optional[str]
    
    # Settings (stored as JSON strings)
    notification_preferences: Optional[str]
    privacy_settings: Optional[str]
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response schema (public fields only)."""
    id: str  # Changed to str to handle UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool  # Changed from email_verified to match the model
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # Optional profile fields
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    
    # IBS-specific fields
    ibs_type: Optional[IBSTypeEnum] = None
    diagnosis_date: Optional[date] = None
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile schema with computed fields."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    age: Optional[int]
    gender: Optional[GenderEnum]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    ibs_type: Optional[IBSTypeEnum]
    diagnosis_date: Optional[date]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics schema."""
    total_symptom_logs: int
    total_diet_logs: int
    total_medication_logs: int
    days_since_registration: int
    last_symptom_log: Optional[datetime]
    last_diet_log: Optional[datetime]
    last_medication_log: Optional[datetime]
    average_symptom_severity: Optional[float]
    most_common_symptoms: list[str]
    most_common_triggers: list[str]