"""Models package for the IBS Wellness Companion."""

from .user import User, GenderEnum, IBSTypeEnum, RoleEnum
from .medication import (
    Medication, MedicationLog, MedicationTypeEnum, DosageUnitEnum
)
from .symptom import Symptom, SymptomLog, SeverityEnum, BristolStoolTypeEnum
from .diet import (
    Food, DietLog, FoodReaction, FoodCategoryEnum, FODMAPLevelEnum,
    MealTypeEnum, ReactionSeverityEnum
)
from .food_item import FoodItem
from .chat import ChatSession, ChatMessage
from .financial import (
    PaymentMethod, BillingAddress, Transaction, Subscription,
    MedicationCost, Invoice
)
from .analytics import (
    UserAnalytics, SystemMetrics, DataInsights, ReportGeneration
)
from .notifications import (
    NotificationPreferences, Notification, NotificationTemplate,
    NotificationLog, DeviceToken
)
from .goals import (
    UserGoal, GoalProgress, Achievement, UserAchievement,
    Milestone, Challenge, ChallengeParticipation
)
from .appointments import (
    HealthcareProvider, UserProvider, Appointment, AppointmentNote,
    AppointmentReminder, MedicalRecord
)
from .ml_prediction import MLPrediction
from .user_preferences import (
    UserPreferences, RiskToleranceEnum, ActivityLevelEnum, 
    LearningProgressEnum
)

__all__ = [
    # Core models
    "User",
    "Symptom",
    "SymptomLog",
    "Food",
    "DietLog",
    "FoodReaction",
    "Medication",
    "MedicationLog",
    "FoodItem",
    "ChatSession",
    "ChatMessage",
    "MLPrediction",
    "UserPreferences",

    # Enums
    "GenderEnum",
    "IBSTypeEnum",
    "RoleEnum",
    "RiskToleranceEnum",
    "ActivityLevelEnum",
    "LearningProgressEnum",
    "MedicationTypeEnum",
    "DosageUnitEnum",
    "SeverityEnum",
    "BristolStoolTypeEnum",
    "FoodCategoryEnum",
    "FODMAPLevelEnum",
    "MealTypeEnum",
    "ReactionSeverityEnum",

    # Financial models
    "PaymentMethod",
    "BillingAddress",
    "Transaction",
    "Subscription",
    "MedicationCost",
    "Invoice",

    # Analytics models
    "UserAnalytics",
    "SystemMetrics",
    "DataInsights",
    "ReportGeneration",

    # Notification models
    "NotificationPreferences",
    "Notification",
    "NotificationTemplate",
    "NotificationLog",
    "DeviceToken",

    # Goals and achievements models
    "UserGoal",
    "GoalProgress",
    "Achievement",
    "UserAchievement",
    "Milestone",
    "Challenge",
    "ChallengeParticipation",

    # Healthcare models
    "HealthcareProvider",
    "UserProvider",
    "Appointment",
    "AppointmentNote",
    "AppointmentReminder",
    "MedicalRecord",
]
