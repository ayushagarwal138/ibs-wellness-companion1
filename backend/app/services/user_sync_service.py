"""
User Synchronization Service

This service handles real-time user data synchronization, validation,
and integration with ML prediction services.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid
import logging

from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.services.user_service import UserService
from app.services.ml_integration_service import MLIntegrationService
from app.services.enhanced_recommendation_service import EnhancedRecommendationService

logger = logging.getLogger(__name__)


class UserSyncEvent:
    """Represents a user synchronization event."""
    
    def __init__(self, user_id: str, event_type: str, data: Dict[str, Any], timestamp: datetime = None):
        self.user_id = user_id
        self.event_type = event_type  # 'profile_update', 'ml_prediction', 'validation_error'
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.event_id = str(uuid.uuid4())


class UserSyncService:
    """Service for real-time user data synchronization and ML integration."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[Any]] = {}  # user_id -> set of websocket connections
        self.pending_updates: Dict[str, List[UserSyncEvent]] = {}  # user_id -> list of pending events
        self.ml_service: Optional[MLIntegrationService] = None
        self.enhanced_service: Optional[EnhancedRecommendationService] = None
    
    async def initialize_ml_services(self, db: AsyncSession):
        """Initialize ML services for predictions."""
        try:
            # Note: MLIntegrationService expects Session, not AsyncSession
            # We'll handle this in the actual implementation
            self.enhanced_service = EnhancedRecommendationService()
            await self.enhanced_service.initialize()
            logger.info("ML services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ML services: {e}")
    
    async def sync_user_profile(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        update_data: Dict[str, Any],
        trigger_ml_update: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronize user profile data with validation and ML integration.
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Data to update
            trigger_ml_update: Whether to trigger ML predictions update
            
        Returns:
            Synchronization result with updated user data and predictions
        """
        try:
            # Validate update data
            validation_result = await self._validate_update_data(update_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'details': validation_result['errors'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get current user
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'user_not_found',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Store previous state for comparison
            previous_state = self._extract_user_state(user)
            
            # Update user profile
            updated_user = await UserService.update_user_profile(db, user_id, update_data)
            if not updated_user:
                return {
                    'success': False,
                    'error': 'update_failed',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Prepare response data
            user_response = UserResponse(
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
            )
            
            # Determine what changed
            current_state = self._extract_user_state(updated_user)
            changes = self._detect_changes(previous_state, current_state)
            
            # Prepare sync result with proper datetime serialization
            sync_result = {
                'success': True,
                'user': user_response.model_dump(mode='json'),  # Use model_dump with json mode for proper serialization
                'changes': changes,
                'timestamp': datetime.utcnow().isoformat(),
                'sync_id': str(uuid.uuid4())
            }
            
            # Trigger ML predictions if significant changes occurred
            if trigger_ml_update and self._should_trigger_ml_update(changes):
                ml_predictions = await self._generate_ml_predictions(updated_user, db)
                sync_result['ml_predictions'] = ml_predictions
            
            # Broadcast update to connected clients
            await self._broadcast_user_update(str(user_id), sync_result)
            
            # Log successful sync
            logger.info(f"User profile synchronized successfully for user {user_id}")
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error synchronizing user profile: {e}")
            return {
                'success': False,
                'error': 'sync_failed',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _validate_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user update data."""
        errors = []
        
        # Validate email format
        if 'email' in update_data:
            email = update_data['email']
            if not email or '@' not in email:
                errors.append('Invalid email format')
        
        # Validate height and weight ranges
        if 'height_cm' in update_data:
            height = update_data['height_cm']
            if height is not None and (height < 50 or height > 300):
                errors.append('Height must be between 50-300 cm')
        
        if 'weight_kg' in update_data:
            weight = update_data['weight_kg']
            if weight is not None and (weight < 20 or weight > 500):
                errors.append('Weight must be between 20-500 kg')
        
        # Validate date of birth
        if 'date_of_birth' in update_data:
            dob = update_data['date_of_birth']
            if dob:
                try:
                    if isinstance(dob, str):
                        datetime.fromisoformat(dob.replace('Z', '+00:00'))
                except ValueError:
                    errors.append('Invalid date of birth format')
        
        # Validate and normalize enum values
        if 'gender' in update_data:
            gender = update_data['gender']
            if gender:
                # Normalize gender value
                gender_mapping = {
                    'male': 'MALE',
                    'female': 'FEMALE', 
                    'other': 'OTHER',
                    'prefer_not_to_say': 'PREFER_NOT_TO_SAY'
                }
                
                if gender.lower() in gender_mapping:
                    update_data['gender'] = gender_mapping[gender.lower()]
                elif gender.upper() not in ['MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY']:
                    errors.append('Gender must be one of: male, female, other, prefer_not_to_say')

        if 'ibs_type' in update_data:
            ibs_type = update_data['ibs_type']
            if ibs_type:
                # Normalize IBS type value
                ibs_mapping = {
                    'ibs-c': 'IBS_C',
                    'ibs-d': 'IBS_D',
                    'ibs-m': 'IBS_M', 
                    'ibs-u': 'IBS_U'
                }
                
                if ibs_type.lower() in ibs_mapping:
                    update_data['ibs_type'] = ibs_mapping[ibs_type.lower()]
                elif ibs_type.upper() not in ['IBS_C', 'IBS_D', 'IBS_M', 'IBS_U']:
                    errors.append('IBS type must be one of: ibs-c, ibs-d, ibs-m, ibs-u')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _extract_user_state(self, user: User) -> Dict[str, Any]:
        """Extract relevant user state for change detection."""
        return {
            'height_cm': user.height_cm,
            'weight_kg': user.weight_kg,
            'ibs_type': getattr(user, 'ibs_type', None),
            'gender': getattr(user, 'gender', None),
            'date_of_birth': user.date_of_birth,
            'diagnosis_date': user.diagnosis_date,
            'medical_notes': user.medical_notes
        }
    
    def _detect_changes(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Detect what changed between user states."""
        changes = {}
        significant_changes = []
        
        for key in current:
            if previous.get(key) != current.get(key):
                changes[key] = {
                    'from': previous.get(key),
                    'to': current.get(key)
                }
                
                # Track significant changes that should trigger ML updates
                if key in ['height_cm', 'weight_kg', 'ibs_type', 'diagnosis_date']:
                    significant_changes.append(key)
        
        return {
            'fields': changes,
            'significant': significant_changes,
            'has_significant_changes': len(significant_changes) > 0
        }
    
    def _should_trigger_ml_update(self, changes: Dict[str, Any]) -> bool:
        """Determine if changes warrant ML prediction updates."""
        return changes.get('has_significant_changes', False)
    
    async def _generate_ml_predictions(self, user: User, db: AsyncSession) -> Dict[str, Any]:
        """Generate ML predictions for updated user data."""
        try:
            if not self.enhanced_service:
                return {'error': 'ML service not available'}
            
            # Prepare user features
            user_features = {
                'age': user.age if user.age else 30,
                'gender': getattr(user, 'gender', 'OTHER'),
                'bmi': user.bmi if user.bmi else 25.0,
                'ibs_type': getattr(user, 'ibs_type', 'IBS_M'),
                'height_cm': user.height_cm or 170,
                'weight_kg': user.weight_kg or 70
            }
            
            # Generate predictions
            risk_prediction = self.enhanced_service.predict_symptom_risk(user_features)
            
            # Generate recommendations
            recommendations = await self.enhanced_service.generate_enhanced_recommendations(
                user, user_features, db
            )
            
            return {
                'risk_assessment': risk_prediction,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat(),
                'model_version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Error generating ML predictions: {e}")
            return {'error': f'Prediction generation failed: {str(e)}'}
    
    async def _broadcast_user_update(self, user_id: str, update_data: Dict[str, Any]):
        """Broadcast user update to connected clients."""
        if user_id in self.active_connections:
            # In a real implementation, this would use WebSocket connections
            # For now, we'll store the update for potential retrieval
            if user_id not in self.pending_updates:
                self.pending_updates[user_id] = []
            
            event = UserSyncEvent(
                user_id=user_id,
                event_type='profile_update',
                data=update_data
            )
            
            self.pending_updates[user_id].append(event)
            
            # Keep only the last 10 events per user
            if len(self.pending_updates[user_id]) > 10:
                self.pending_updates[user_id] = self.pending_updates[user_id][-10:]
    
    async def get_pending_updates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending updates for a user."""
        if user_id not in self.pending_updates:
            return []
        
        events = self.pending_updates[user_id]
        # Clear pending updates after retrieval
        self.pending_updates[user_id] = []
        
        return [
            {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'data': event.data,
                'timestamp': event.timestamp.isoformat()
            }
            for event in events
        ]
    
    async def register_connection(self, user_id: str, connection: Any):
        """Register a client connection for real-time updates."""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(connection)
    
    async def unregister_connection(self, user_id: str, connection: Any):
        """Unregister a client connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(connection)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]


# Global instance
user_sync_service = UserSyncService()