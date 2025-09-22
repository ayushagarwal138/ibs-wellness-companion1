"""
Pydantic schemas for the IBS Wellness Companion API.
"""

from .auth import *
from .user import *
from .symptom import *
from .medication import *
from .diet import *
from .analytics import *
from .goal import *
from .appointment import *

__all__ = [
    # Auth schemas
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    "PasswordReset",
    "PasswordResetConfirm",
    "EmailVerification",
    
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserProfile",
    
    # Symptom schemas
    "SymptomLogBase",
    "SymptomLogCreate",
    "SymptomLogUpdate",
    "SymptomLogResponse",
    "SymptomLogList",
    "SymptomStats",
    "SymptomAnalytics",
    
    # Medication schemas
    "MedicationLogBase",
    "MedicationLogCreate", 
    "MedicationLogUpdate",
    "MedicationLogResponse",
    "MedicationLogList",
    "MedicationStats",
    "MedicationSchedule",
    "MedicationReminder",
    "AdherenceReport",
    
    # Diet schemas
    "FoodReactionBase",
    "FoodReactionCreate",
    "FoodReactionUpdate", 
    "FoodReactionResponse",
    "FoodReactionList",
    "DietLogBase",
    "DietLogCreate",
    "DietLogUpdate",
    "DietLogResponse", 
    "DietLogList",
    "FoodStats",
    "DietStats",
    "NutritionalAnalysis",
    "TriggerFoodAnalysis",
    
    # Analytics schemas
    "UserAnalyticsResponse",
    "SystemMetricsResponse",
    "AchievementResponse",
    "AchievementListResponse",
    
    # Goal schemas
    "GoalBase",
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    "GoalListResponse",
    "GoalProgressCreate",
    "GoalProgressResponse",
    "GoalSummaryResponse",
    
    # Appointment schemas
    "AppointmentBase",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentListResponse",
    "AppointmentSummaryResponse",
    "AppointmentReminderResponse",
    "AppointmentResultCreate",
    "AppointmentResultResponse",
    "AppointmentStatsResponse",
]