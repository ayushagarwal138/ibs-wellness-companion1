"""
Firebase Admin SDK service for backend operations.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from firebase_admin import credentials, initialize_app, auth, messaging
import firebase_admin

from app.core.config import settings

logger = logging.getLogger(__name__)


class FirebaseAdminService:
    """Firebase Admin SDK service for backend operations."""
    
    def __init__(self):
        self._app: Optional[firebase_admin.App] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize Firebase Admin SDK with service account credentials."""
        if self._initialized:
            return True
            
        try:
            # Check if required settings are available
            if not all([
                settings.FIREBASE_PROJECT_ID,
                settings.FIREBASE_PRIVATE_KEY,
                settings.FIREBASE_CLIENT_EMAIL
            ]):
                logger.warning("Firebase Admin credentials not configured. Skipping initialization.")
                return False
            
            # Create service account credentials
            service_account_info = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if settings.FIREBASE_PRIVATE_KEY else None,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
                "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN
            }
            
            # Initialize Firebase Admin
            cred = credentials.Certificate(service_account_info)
            self._app = initialize_app(cred)
            self._initialized = True
            
            logger.info("Firebase Admin SDK initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            return False
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return decoded claims."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Failed to verify ID token: {e}")
            return None
    
    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user information by UID."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            user_record = auth.get_user(uid)
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "email_verified": user_record.email_verified,
                "display_name": user_record.display_name,
                "photo_url": user_record.photo_url,
                "disabled": user_record.disabled,
                "metadata": {
                    "creation_timestamp": user_record.user_metadata.creation_timestamp,
                    "last_sign_in_timestamp": user_record.user_metadata.last_sign_in_timestamp,
                }
            }
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {e}")
            return None
    
    async def create_user(self, email: str, password: str, display_name: Optional[str] = None) -> Optional[str]:
        """Create a new Firebase user and return UID."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=False
            )
            return user_record.uid
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            return None
    
    async def update_user(self, uid: str, **kwargs) -> bool:
        """Update Firebase user information."""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            auth.update_user(uid, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to update user {uid}: {e}")
            return False
    
    async def delete_user(self, uid: str) -> bool:
        """Delete Firebase user."""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {uid}: {e}")
            return False
    
    async def send_push_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send push notification to a specific device token."""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    async def send_multicast_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send push notification to multiple device tokens."""
        if not self._initialized:
            if not self.initialize():
                return {"success_count": 0, "failure_count": len(tokens)}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            logger.info(f"Successfully sent {response.success_count} messages, {response.failure_count} failed")
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {
                        "success": resp.success,
                        "message_id": resp.message_id if resp.success else None,
                        "error": str(resp.exception) if not resp.success else None
                    }
                    for resp in response.responses
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to send multicast notification: {e}")
            return {"success_count": 0, "failure_count": len(tokens)}
    
    async def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send push notification to a topic."""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Successfully sent topic message: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send topic notification: {e}")
            return False


# Global Firebase Admin service instance
firebase_admin_service = FirebaseAdminService()