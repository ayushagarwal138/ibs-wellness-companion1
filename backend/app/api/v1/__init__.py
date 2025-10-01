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
from .optimization import router as optimization_router
from .user_sync import router as user_sync_router
from .financial import router as financial_router
from .analytics import router as analytics_router
from .goals import router as goals_router
from .appointments import router as appointments_router
from .symptom_logs import router as symptom_logs_router
from .personalization import router as personalization_router
from .ibs_assessment import router as ibs_assessment_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(oauth_router, prefix="/auth", tags=["oauth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(user_sync_router, prefix="/sync", tags=["user-sync"])
api_router.include_router(symptoms_router, prefix="/symptoms", tags=["symptoms"])
api_router.include_router(medications_router, prefix="/medications", tags=["medications"])
api_router.include_router(diet_router, prefix="/diet", tags=["diet"])
api_router.include_router(ml_predictions_router, prefix="/ml", tags=["ml-predictions"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(profile_router, tags=["profile"])
api_router.include_router(notifications_router, tags=["notifications"])
api_router.include_router(recommendations_router, tags=["recommendations"])
api_router.include_router(optimization_router, prefix="/optimization", tags=["optimization"])
api_router.include_router(financial_router, prefix="/financial", tags=["financial"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(goals_router, prefix="/goals", tags=["goals"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(symptom_logs_router, prefix="/symptom-logs", tags=["symptom-logs"])
api_router.include_router(personalization_router, prefix="/personalization", tags=["personalization"])
api_router.include_router(ibs_assessment_router, tags=["ibs-assessment"])

__all__ = ["api_router"]