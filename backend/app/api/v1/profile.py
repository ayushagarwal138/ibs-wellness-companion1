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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get complete user profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
        "gender": current_user.gender,
        "avatar_url": current_user.avatar_url,
        "emergency_contact_name": current_user.emergency_contact_name,
        "emergency_contact_phone": current_user.emergency_contact_phone,
        "timezone": current_user.timezone,
        "age": current_user.age,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "bmi": current_user.bmi,
        "medical_history": {
            "ibs_type": current_user.ibs_type,
            "diagnosis_date": current_user.diagnosis_date.isoformat() if current_user.diagnosis_date else None,
            "medical_notes": current_user.medical_notes
        },
        "preferences": {
            "notification_preferences": current_user.notification_preferences or {},
            "privacy_settings": current_user.privacy_settings or {}
        },
        "role": current_user.role.value if current_user.role else None,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
    }


@router.get("/basic-info")
async def get_basic_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's basic information."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
        "gender": current_user.gender,
        "avatar_url": current_user.avatar_url,
        "emergency_contact_name": current_user.emergency_contact_name,
        "emergency_contact_phone": current_user.emergency_contact_phone,
        "timezone": current_user.timezone
    }


@router.put("/basic-info")
async def update_basic_info(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user's basic information."""
    # Filter allowed fields for basic info
    allowed_fields = {
        "first_name", "last_name", "phone_number", "date_of_birth", 
        "gender", "avatar_url", "emergency_contact_name", 
        "emergency_contact_phone", "timezone"
    }
    
    filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    
    updated_user = await UserService.update_user_profile(db, current_user.id, filtered_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "Basic information updated successfully",
        "updated_fields": list(filtered_data.keys())
    }


@router.get("/medical-history")
async def get_medical_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's medical history."""
    return {
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "ibs_type": current_user.ibs_type,
        "diagnosis_date": current_user.diagnosis_date.isoformat() if current_user.diagnosis_date else None,
        "medical_notes": current_user.medical_notes,
        "bmi": round(current_user.weight_kg / ((current_user.height_cm / 100) ** 2), 2) if current_user.height_cm and current_user.weight_kg else None
    }


@router.put("/medical-history")
async def update_medical_history(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user's medical history."""
    # Filter allowed fields for medical history
    allowed_fields = {
        "height_cm", "weight_kg", "ibs_type", "diagnosis_date", "medical_notes"
    }
    
    filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    
    updated_user = await UserService.update_user_profile(db, current_user.id, filtered_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "Medical history updated successfully",
        "updated_fields": list(filtered_data.keys())
    }


@router.get("/dietary-preferences")
async def get_dietary_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's dietary preferences."""
    # For now, return empty structure since dietary preferences aren't in the User model
    # This could be extended to include a separate DietaryPreferences model
    return {
        "dietary_restrictions": [],
        "food_allergies": [],
        "preferred_cuisines": [],
        "meal_frequency": None,
        "water_intake_goal": None,
        "special_diets": []
    }


@router.put("/dietary-preferences")
async def update_dietary_preferences(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user's dietary preferences."""
    # For now, just return success since we don't have a dietary preferences model
    # This would need to be implemented with a proper DietaryPreferences model
    return {
        "message": "Dietary preferences updated successfully",
        "note": "Dietary preferences storage not yet implemented in database"
    }


@router.get("/lifestyle-factors")
async def get_lifestyle_factors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's lifestyle factors."""
    # For now, return empty structure since lifestyle factors aren't in the User model
    return {
        "exercise_frequency": None,
        "sleep_hours": None,
        "stress_level": None,
        "smoking_status": None,
        "alcohol_consumption": None,
        "work_schedule": None,
        "activity_level": None
    }


@router.put("/lifestyle-factors")
async def update_lifestyle_factors(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user's lifestyle factors."""
    # For now, just return success since we don't have a lifestyle factors model
    return {
        "message": "Lifestyle factors updated successfully",
        "note": "Lifestyle factors storage not yet implemented in database"
    }


@router.get("/goals-preferences")
async def get_goals_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's goals and preferences."""
    # Extract notification and privacy preferences from existing JSON fields
    notification_prefs = current_user.notification_preferences or {}
    privacy_settings = current_user.privacy_settings or {}
    
    return {
        "health_goals": [],
        "notification_preferences": notification_prefs,
        "privacy_settings": privacy_settings,
        "data_sharing_consent": privacy_settings.get("data_sharing_consent", False),
        "research_participation": privacy_settings.get("research_participation", False)
    }


@router.put("/goals-preferences")
async def update_goals_preferences(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user's goals and preferences."""
    # Extract notification and privacy preferences to update JSON fields
    update_data = {}
    
    if "notification_preferences" in profile_data:
        update_data["notification_preferences"] = profile_data["notification_preferences"]
    
    if "privacy_settings" in profile_data:
        update_data["privacy_settings"] = profile_data["privacy_settings"]
    
    if update_data:
        updated_user = await UserService.update_user_profile(db, current_user.id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    return {
        "message": "Goals and preferences updated successfully",
        "updated_fields": list(update_data.keys())
    }