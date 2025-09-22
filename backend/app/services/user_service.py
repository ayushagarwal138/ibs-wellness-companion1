"""
User service for managing user operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
import uuid

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination."""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            full_name=user.full_name,
            age=user.age,
            gender=user.gender,
            is_active=True,
            is_verified=False
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user information."""
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update separately
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Delete a user."""
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def activate_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Activate a user account."""
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_active = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Deactivate a user account."""
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_active = False
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def verify_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Verify a user's email."""
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_verified = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: uuid.UUID, profile_data: dict) -> Optional[User]:
        """Update user profile with arbitrary data (used for onboarding)."""
        from datetime import datetime, date
        from app.models.user import GenderEnum, IBSTypeEnum
        
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Date fields that need conversion from string to date object
        date_fields = {'date_of_birth', 'diagnosis_date'}
        
        # Gender mapping for string to enum conversion
        gender_mapping = {
            'male': GenderEnum.MALE,
            'female': GenderEnum.FEMALE,
            'other': GenderEnum.OTHER,
            'prefer_not_to_say': GenderEnum.PREFER_NOT_TO_SAY
        }
        
        # IBS type mapping for string to enum conversion
        ibs_mapping = {
            'ibs-d': IBSTypeEnum.IBS_D,
            'ibs-c': IBSTypeEnum.IBS_C,
            'ibs-m': IBSTypeEnum.IBS_M,
            'ibs-u': IBSTypeEnum.IBS_U
        }
        
        # Update user attributes with the provided profile data
        for field, value in profile_data.items():
            if hasattr(db_user, field):
                # Convert date strings to date objects for date fields
                if field in date_fields and isinstance(value, str) and value:
                    try:
                        # Parse ISO date string (YYYY-MM-DD) to date object
                        converted_value = datetime.strptime(value, '%Y-%m-%d').date()
                        setattr(db_user, field, converted_value)
                    except ValueError:
                        # If parsing fails, skip this field to avoid database errors
                        continue
                # Convert gender string to enum
                elif field == 'gender' and isinstance(value, str) and value:
                    gender_value = value.lower()
                    if gender_value in gender_mapping:
                        setattr(db_user, field, gender_mapping[gender_value])
                    else:
                        # Skip invalid gender values to avoid database errors
                        continue
                # Convert IBS type string to enum
                elif field == 'ibs_type' and isinstance(value, str) and value:
                    ibs_value = value.lower()
                    if ibs_value in ibs_mapping:
                        setattr(db_user, field, ibs_mapping[ibs_value])
                    else:
                        # Skip invalid IBS type values to avoid database errors
                        continue
                else:
                    setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: uuid.UUID) -> dict:
        """Get user statistics."""
        # This would typically involve querying related tables
        # For now, return basic stats
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return {}
        
        return {
            "total_symptom_logs": 0,  # TODO: Implement when symptom logs are created
            "total_medication_logs": 0,  # TODO: Implement when medication logs are created
            "total_diet_logs": 0,  # TODO: Implement when diet logs are created
            "account_created": user.created_at,
            "last_login": user.last_login,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }