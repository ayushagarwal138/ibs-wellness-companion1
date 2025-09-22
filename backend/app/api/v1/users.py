"""
User management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.services.user_service import UserService
from app.services.ml_integration_service import MLIntegrationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/onboarding")
async def save_onboarding_data(
    onboarding_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save user onboarding questionnaire data and update profile.
    
    Args:
        onboarding_data: Complete onboarding questionnaire responses
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        Success message with updated user profile
    """
    try:
        # Extract basic profile data from onboarding responses
        profile_updates = {}
        
        # Map onboarding data to user profile fields
        if 'age' in onboarding_data:
            # Calculate birth year from age (approximate)
            current_year = datetime.now().year
            birth_year = current_year - onboarding_data['age']
            profile_updates['date_of_birth'] = datetime(birth_year, 1, 1)
            
        if 'gender' in onboarding_data:
            # Map frontend gender values to backend enum values
            gender_mapping = {
                'male': 'MALE',
                'female': 'FEMALE', 
                'other': 'OTHER',
                'prefer_not_to_say': 'PREFER_NOT_TO_SAY'
            }
            frontend_gender = onboarding_data['gender'].lower()
            if frontend_gender in gender_mapping:
                profile_updates['gender'] = gender_mapping[frontend_gender]
            
        if 'height' in onboarding_data:
            profile_updates['height_cm'] = int(onboarding_data['height'])
            
        if 'weight' in onboarding_data:
            profile_updates['weight_kg'] = float(onboarding_data['weight'])
            
        if 'ibsType' in onboarding_data:
            # Map frontend IBS type values to backend enum values
            ibs_type_mapping = {
                'ibs-d': 'IBS_D',
                'ibs-c': 'IBS_C',
                'ibs-m': 'IBS_M', 
                'ibs-u': 'IBS_U',
                'not_diagnosed': None  # Don't set if not diagnosed
            }
            frontend_ibs_type = onboarding_data['ibsType'].lower()
            if frontend_ibs_type in ibs_type_mapping:
                mapped_value = ibs_type_mapping[frontend_ibs_type]
                if mapped_value is not None:  # Only set if not None
                    profile_updates['ibs_type'] = mapped_value
            
        if 'diagnosisYear' in onboarding_data:
            profile_updates['diagnosis_date'] = datetime(int(onboarding_data['diagnosisYear']), 1, 1)
        
        # Store additional onboarding data as JSON in medical_notes
        additional_data = {
            'onboarding_completed': True,
            'completion_date': datetime.now().isoformat(),
            'severity_level': onboarding_data.get('severityLevel'),
            'known_triggers': onboarding_data.get('knownTriggers', []),
            'common_symptoms': onboarding_data.get('commonSymptoms', []),
            'symptom_patterns': onboarding_data.get('symptomPatterns', []),
            'stress_level': onboarding_data.get('stressLevel'),
            'sleep_quality': onboarding_data.get('sleepQuality'),
            'exercise_frequency': onboarding_data.get('exerciseFrequency'),
            'dietary_restrictions': onboarding_data.get('dietaryRestrictions', []),
            'medications': onboarding_data.get('medications', []),
            'allergies': onboarding_data.get('allergies', []),
            'other_conditions': onboarding_data.get('otherConditions', []),
            'primary_goals': onboarding_data.get('primaryGoals', []),
            'preferred_treatments': onboarding_data.get('preferredTreatments', []),
            'predictions': onboarding_data.get('predictions')
        }
        
        # Store allergies in the dedicated field (User model doesn't have allergies field)
        # if onboarding_data.get('allergies'):
        #     profile_updates['allergies'] = ', '.join(onboarding_data['allergies'])
            
        # Store medications in the dedicated field (User model doesn't have current_medications field)
        # if onboarding_data.get('medications'):
        #     profile_updates['current_medications'] = ', '.join(onboarding_data['medications'])
        
        # Store the complete onboarding data in medical_notes
        profile_updates['medical_notes'] = json.dumps(additional_data)
        
        # Update user profile
        user_service = UserService()
        updated_user = await user_service.update_user_profile(
            db=db,
            user_id=current_user.id,
            profile_data=profile_updates
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user profile"
            )
        
        # Return updated user data
        return {
            "message": "Onboarding data saved successfully",
            "user": UserResponse(
                id=str(updated_user.id),
                email=updated_user.email,
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                is_active=updated_user.is_active,
                is_verified=updated_user.is_verified,
                created_at=updated_user.created_at,
                last_login=updated_user.last_login_at,
                phone_number=getattr(updated_user, 'phone_number', None),
                date_of_birth=updated_user.date_of_birth,
                gender=getattr(updated_user, 'gender', None),
                height_cm=updated_user.height_cm,
                weight_kg=updated_user.weight_kg,
                ibs_type=getattr(updated_user, 'ibs_type', None),
                diagnosis_date=updated_user.diagnosis_date
            ).dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save onboarding data: {str(e)}"
        )


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete user profile including onboarding data.
    
    Args:
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        Complete user profile with onboarding data
    """
    try:
        # Get basic user data
        user_response = UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at,
            last_login=current_user.last_login_at,
            phone_number=getattr(current_user, 'phone_number', None),
            date_of_birth=current_user.date_of_birth,
            gender=getattr(current_user, 'gender', None),
            height_cm=current_user.height_cm,
            weight_kg=current_user.weight_kg,
            ibs_type=getattr(current_user, 'ibs_type', None),
            diagnosis_date=current_user.diagnosis_date
        )
        
        # Parse onboarding data from medical_notes if available
        onboarding_data = None
        if current_user.medical_notes:
            try:
                onboarding_data = json.loads(current_user.medical_notes)
            except json.JSONDecodeError:
                onboarding_data = None
        
        return {
            "user": user_response.dict(),
            "onboarding_data": onboarding_data,
            "onboarding_completed": onboarding_data is not None and onboarding_data.get('onboarding_completed', False)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.patch("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile with comprehensive data."""
    try:
        # Update user profile
        updated_user = await UserService.update_user(
            db=db,
            user_id=current_user.id,
            user_update=profile_update
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert UUID to string for response
        user_dict = {
            "id": str(updated_user.id),
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "is_active": updated_user.is_active,
            "is_verified": updated_user.is_verified,
            "created_at": updated_user.created_at,
            "last_login": updated_user.last_login_at,  # Use last_login_at from model
            "phone_number": updated_user.phone_number,
            "date_of_birth": updated_user.date_of_birth,
            "gender": updated_user.gender,
            "height_cm": updated_user.height_cm,
            "weight_kg": updated_user.weight_kg,
            "ibs_type": updated_user.ibs_type,
            "diagnosis_date": updated_user.diagnosis_date
        }
        
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error updating profile: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if user has completed onboarding.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Onboarding completion status
    """
    try:
        onboarding_completed = False
        completion_date = None
        
        if current_user.medical_notes:
            try:
                onboarding_data = json.loads(current_user.medical_notes)
                onboarding_completed = onboarding_data.get('onboarding_completed', False)
                completion_date = onboarding_data.get('completion_date')
            except json.JSONDecodeError:
                pass
        
        return {
            "onboarding_completed": onboarding_completed,
            "completion_date": completion_date,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get onboarding status: {str(e)}"
        )
