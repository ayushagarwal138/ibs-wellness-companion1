"""
Chat schemas for IBS wellness chatbot.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


# Enums
class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IBSSeverity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    UNKNOWN = "unknown"


class RecommendationType(str, Enum):
    DIET = "diet"
    LIFESTYLE = "lifestyle"
    MEDICATION = "medication"
    EXERCISE = "exercise"


# Base schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessageBase(BaseModel):
    content: str
    message_type: MessageType
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Request schemas
class ChatSessionCreate(ChatSessionBase):
    pass


class ChatMessageCreate(ChatMessageBase):
    session_id: str


class ChatMessageSend(BaseModel):
    message: str
    session_id: Optional[str] = None
    include_context: bool = True


# Response schemas
class ChatSessionResponse(ChatSessionBase):
    id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime


class ChatMessageResponse(ChatMessageBase):
    id: str
    session_id: str
    user_id: str
    sent_at: datetime
    created_at: datetime


class IBSAssessment(BaseModel):
    severity: IBSSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    factors: List[str] = Field(default_factory=list)
    symptoms_score: float = Field(ge=0.0, le=10.0)
    frequency_score: float = Field(ge=0.0, le=10.0)
    impact_score: float = Field(ge=0.0, le=10.0)
    last_assessment: Optional[datetime] = None


class Recommendation(BaseModel):
    type: RecommendationType
    title: str
    description: str
    priority: int = Field(ge=1, le=5)
    evidence_level: str
    actionable_steps: List[str] = Field(default_factory=list)
    expected_benefit: str
    timeframe: str


class ChatbotResponse(BaseModel):
    message: str
    session_id: str
    message_id: str
    ibs_assessment: Optional[IBSAssessment] = None
    recommendations: List[Recommendation] = Field(default_factory=list)
    context_used: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    requires_followup: bool = False
    followup_questions: List[str] = Field(default_factory=list)


class ConversationContext(BaseModel):
    user_id: Optional[str] = None
    current_message: Optional[str] = None
    recent_symptoms: List[Dict[str, Any]] = Field(default_factory=list)
    recent_foods: List[Dict[str, Any]] = Field(default_factory=list)
    recent_medications: List[Dict[str, Any]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    previous_assessments: List[IBSAssessment] = Field(default_factory=list)
    conversation_history: List[str] = Field(default_factory=list)
    current_state: Union[str, Dict[str, Any]] = Field(default_factory=dict)
    pending_followups: List[str] = Field(default_factory=list)


# List schemas
class ChatSessionList(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int
    page: int
    size: int


class ChatMessageList(BaseModel):
    messages: List[ChatMessageResponse]
    total: int
    page: int
    size: int


# Analytics schemas
class ChatAnalytics(BaseModel):
    total_sessions: int
    total_messages: int
    avg_session_length: float
    most_common_topics: List[Dict[str, Any]]
    ibs_severity_distribution: Dict[str, int]
    recommendation_effectiveness: Dict[str, float]


class UserChatStats(BaseModel):
    total_sessions: int
    total_messages: int
    avg_messages_per_session: float
    last_chat: Optional[datetime] = None
    current_ibs_severity: IBSSeverity
    improvement_trend: Optional[str] = None
