"""
Profile API endpoints for user profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get complete user profile."""
    # Compute full_name manually to avoid async issues
    full_name = ""
    if current_user.first_name and current_user.last_name:
        full_name = f"{current_user.first_name} {current_user.last_name}"
    elif current_user.first_name:
        full_name = current_user.first_name
    elif current_user.last_name:
        full_name = current_user.last_name

    # Compute age manually to avoid async issues
    age = None
    if current_user.date_of_birth:
        from datetime import date

        today = date.today()
        age = (
            today.year
            - current_user.date_of_birth.year
            - (
                (today.month, today.day)
                < (current_user.date_of_birth.month, current_user.date_of_birth.day)
            )
        )

    # Compute BMI manually to avoid async issues
    bmi = None
    if current_user.height_cm and current_user.weight_kg:
        height_m = current_user.height_cm / 100
        bmi = round(current_user.weight_kg / (height_m**2), 2)

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": full_name,
        "phone_number": current_user.phone_number,
        "date_of_birth": current_user.date_of_birth.isoformat()
        if current_user.date_of_birth
        else None,
        "gender": current_user.gender,
        "avatar_url": current_user.avatar_url,
        "emergency_contact_name": current_user.emergency_contact_name,
        "emergency_contact_phone": current_user.emergency_contact_phone,
        "timezone": current_user.timezone,
        "age": age,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "bmi": bmi,
        "medical_history": {
            "ibs_type": current_user.ibs_type,
            "diagnosis_date": current_user.diagnosis_date.isoformat()
            if current_user.diagnosis_date
            else None,
            "medical_notes": current_user.medical_notes,
        },
        "preferences": {
            "notification_preferences": current_user.notification_preferences or {},
            "privacy_settings": current_user.privacy_settings or {},
        },
        "role": current_user.role if current_user.role else None,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat()
        if current_user.created_at
        else None,
        "updated_at": current_user.updated_at.isoformat()
        if current_user.updated_at
        else None,
        "last_login_at": current_user.last_login_at.isoformat()
        if current_user.last_login_at
        else None,
    }


@router.get("/basic-info")
async def get_basic_info(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's basic information."""
    # Transform gender enum to string format expected by frontend
    gender_value = None
    if current_user.gender:
        gender_mapping = {
            "MALE": "male",
            "FEMALE": "female",
            "OTHER": "other",
            "PREFER_NOT_TO_SAY": "prefer_not_to_say",
        }
        gender_value = gender_mapping.get(
            current_user.gender.value
            if hasattr(current_user.gender, "value")
            else str(current_user.gender)
        )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "date_of_birth": current_user.date_of_birth.isoformat()
        if current_user.date_of_birth
        else None,
        "gender": gender_value,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "avatar_url": current_user.avatar_url,
        "emergency_contact_name": current_user.emergency_contact_name,
        "emergency_contact_phone": current_user.emergency_contact_phone,
        "timezone": current_user.timezone,
    }


@router.put("/basic-info")
async def update_basic_info(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update user's basic information."""
    # Filter allowed fields for basic info
    allowed_fields = {
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "avatar_url",
        "emergency_contact_name",
        "emergency_contact_phone",
        "timezone",
        "height_cm",
        "weight_kg",
    }

    filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}

    updated_user = await UserService.update_user_profile(
        db, current_user.id, filtered_data
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "message": "Basic information updated successfully",
        "updated_fields": list(filtered_data.keys()),
    }


@router.get("/medical-history")
async def get_medical_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's medical history."""
    # Transform IBS type enum to string format expected by frontend
    ibs_type_value = None
    if current_user.ibs_type:
        ibs_mapping = {
            "IBS_C": "ibs_c",
            "IBS_D": "ibs_d",
            "IBS_M": "ibs_m",
            "IBS_U": "ibs_u",
        }
        ibs_type_value = ibs_mapping.get(
            current_user.ibs_type.value
            if hasattr(current_user.ibs_type, "value")
            else str(current_user.ibs_type)
        )

    return {
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "ibs_type": ibs_type_value,
        "diagnosis_date": current_user.diagnosis_date.isoformat()
        if current_user.diagnosis_date
        else None,
        "medical_notes": current_user.medical_notes,
        "bmi": round(current_user.weight_kg / ((current_user.height_cm / 100) ** 2), 2)
        if current_user.height_cm and current_user.weight_kg
        else None,
    }


@router.put("/medical-history")
async def update_medical_history(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update user's medical history."""
    # Filter allowed fields for medical history
    allowed_fields = {
        "height_cm",
        "weight_kg",
        "ibs_type",
        "diagnosis_date",
        "medical_notes",
    }

    filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}

    updated_user = await UserService.update_user_profile(
        db, current_user.id, filtered_data
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "message": "Medical history updated successfully",
        "updated_fields": list(filtered_data.keys()),
    }


@router.get("/dietary-preferences")
async def get_dietary_preferences(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's dietary preferences."""
    # Get dietary preferences from user's privacy_settings JSON field
    dietary_prefs = {}
    if current_user.privacy_settings and isinstance(
        current_user.privacy_settings, dict
    ):
        dietary_prefs = current_user.privacy_settings.get("dietary_preferences", {})

    # Return with default values if not set
    return {
        "dietaryRestrictions": dietary_prefs.get("dietaryRestrictions", []),
        "foodAllergies": dietary_prefs.get("foodAllergies", []),
        "preferredDiets": dietary_prefs.get("preferredDiets", []),
        "mealsPerDay": dietary_prefs.get("mealsPerDay", 3),
        "waterIntake": dietary_prefs.get("waterIntake", 8),
        "alcoholConsumption": dietary_prefs.get("alcoholConsumption", "none"),
        "caffeineIntake": dietary_prefs.get("caffeineIntake", "moderate"),
        "cookingFrequency": dietary_prefs.get("cookingFrequency", "few_times_week"),
        "eatingOutFrequency": dietary_prefs.get("eatingOutFrequency", "weekly"),
        "favoritefoods": dietary_prefs.get("favoritefoods", []),
        "dislikedFoods": dietary_prefs.get("dislikedFoods", []),
        "supplementsUsed": dietary_prefs.get("supplementsUsed", []),
        "mealTiming": dietary_prefs.get("mealTiming", "regular"),
        "snackingHabits": dietary_prefs.get("snackingHabits", "occasional"),
        "foodBudget": dietary_prefs.get("foodBudget", "moderate"),
        "specialNotes": dietary_prefs.get("specialNotes", ""),
    }


@router.put("/dietary-preferences")
async def update_dietary_preferences(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update user's dietary preferences."""
    # Get current privacy settings or initialize empty dict
    privacy_settings = current_user.privacy_settings or {}
    if not isinstance(privacy_settings, dict):
        privacy_settings = {}

    # Store dietary preferences in privacy_settings JSON field
    privacy_settings["dietary_preferences"] = profile_data

    # Update user with new privacy settings
    updated_user = await UserService.update_user_profile(
        db, current_user.id, {"privacy_settings": privacy_settings}
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": "Dietary preferences updated successfully", "data": profile_data}


@router.get("/lifestyle-factors")
async def get_lifestyle_factors(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's lifestyle factors."""
    # Get lifestyle factors from user's notification_preferences JSON field
    lifestyle_factors = {}
    if current_user.notification_preferences and isinstance(
        current_user.notification_preferences, dict
    ):
        lifestyle_factors = current_user.notification_preferences.get(
            "lifestyle_factors", {}
        )

    # Return with default values if not set
    return {
        "exerciseFrequency": lifestyle_factors.get("exerciseFrequency", ""),
        "exerciseTypes": lifestyle_factors.get("exerciseTypes", []),
        "sleepHours": lifestyle_factors.get("sleepHours", 8),
        "sleepQuality": lifestyle_factors.get("sleepQuality", "good"),
        "stressLevel": lifestyle_factors.get("stressLevel", 5),
        "stressManagement": lifestyle_factors.get("stressManagement", []),
        "smokingStatus": lifestyle_factors.get("smokingStatus", "never"),
        "workSchedule": lifestyle_factors.get("workSchedule", "regular"),
        "workStressLevel": lifestyle_factors.get("workStressLevel", 5),
        "socialSupport": lifestyle_factors.get("socialSupport", "good"),
        "hobbies": lifestyle_factors.get("hobbies", []),
        "travelFrequency": lifestyle_factors.get("travelFrequency", "occasional"),
        "environmentalFactors": lifestyle_factors.get("environmentalFactors", []),
        "dailyRoutine": lifestyle_factors.get("dailyRoutine", "structured"),
        "specialNotes": lifestyle_factors.get("specialNotes", ""),
    }


@router.put("/lifestyle-factors")
async def update_lifestyle_factors(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update user's lifestyle factors."""
    # Get current notification preferences or initialize empty dict
    notification_preferences = current_user.notification_preferences or {}
    if not isinstance(notification_preferences, dict):
        notification_preferences = {}

    # Store lifestyle factors in notification_preferences JSON field
    notification_preferences["lifestyle_factors"] = profile_data

    # Update user with new notification preferences
    updated_user = await UserService.update_user_profile(
        db, current_user.id, {"notification_preferences": notification_preferences}
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": "Lifestyle factors updated successfully", "data": profile_data}


@router.get("/goals-preferences")
async def get_goals_preferences(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's goals and preferences."""
    # Get goals and preferences from user's privacy_settings JSON field
    goals_preferences = {}
    if current_user.privacy_settings and isinstance(
        current_user.privacy_settings, dict
    ):
        goals_preferences = current_user.privacy_settings.get("goals_preferences", {})

    # Return with default values if not set
    return {
        "primaryGoals": goals_preferences.get("primaryGoals", []),
        "symptomManagementGoals": goals_preferences.get("symptomManagementGoals", []),
        "dietaryGoals": goals_preferences.get("dietaryGoals", []),
        "lifestyleGoals": goals_preferences.get("lifestyleGoals", []),
        "timeframe": goals_preferences.get("timeframe", "3-6 months"),
        "motivationLevel": goals_preferences.get("motivationLevel", 5),
        "supportPreferences": goals_preferences.get("supportPreferences", []),
        "trackingPreferences": goals_preferences.get("trackingPreferences", []),
        "reminderFrequency": goals_preferences.get("reminderFrequency", "daily"),
        "preferredCommunicationStyle": goals_preferences.get(
            "preferredCommunicationStyle", "encouraging"
        ),
        "challengeLevel": goals_preferences.get("challengeLevel", "moderate"),
        "focusAreas": goals_preferences.get("focusAreas", []),
        "successMetrics": goals_preferences.get("successMetrics", []),
        "barriers": goals_preferences.get("barriers", []),
        "additionalNotes": goals_preferences.get("additionalNotes", ""),
    }


@router.put("/goals-preferences")
async def update_goals_preferences(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update user's goals and preferences."""
    # Get current privacy settings or initialize empty dict
    privacy_settings = current_user.privacy_settings or {}
    if not isinstance(privacy_settings, dict):
        privacy_settings = {}

    # Store goals and preferences in privacy_settings JSON field
    privacy_settings["goals_preferences"] = profile_data

    # Update user with new privacy settings
    updated_user = await UserService.update_user_profile(
        db, current_user.id, {"privacy_settings": privacy_settings}
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "message": "Goals and preferences updated successfully",
        "data": profile_data,
    }
