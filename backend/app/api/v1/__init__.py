"""
API v1 package.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .oauth import router as oauth_router
from .symptoms import router as symptoms_router
from .medications import router as medications_router
from .diet import router as diet_router
from .ml_predictions import router as ml_predictions_router
from .chat import router as chat_router
from .users import router as users_router
from .onboarding import router as onboarding_router
from .profile import router as profile_router
from .notifications import router as notifications_router
from .recommendations import router as recommendations_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(oauth_router, prefix="/auth", tags=["oauth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(symptoms_router, prefix="/symptoms", tags=["symptoms"])
api_router.include_router(medications_router, prefix="/medications", tags=["medications"])
api_router.include_router(diet_router, prefix="/diet", tags=["diet"])
api_router.include_router(ml_predictions_router, prefix="/ml", tags=["ml-predictions"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(profile_router, tags=["profile"])
api_router.include_router(notifications_router, tags=["notifications"])
api_router.include_router(recommendations_router, tags=["recommendations"])

__all__ = ["api_router"]