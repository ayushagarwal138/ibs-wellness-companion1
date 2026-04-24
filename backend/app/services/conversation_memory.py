"""
Conversation Memory Service for maintaining context and follow-up capabilities.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ConversationState(Enum):
    GREETING = "greeting"
    SYMPTOM_DISCUSSION = "symptom_discussion"
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"
    RECOMMENDATION_REVIEW = "recommendation_review"
    FOLLOW_UP = "follow_up"
    GENERAL_INQUIRY = "general_inquiry"


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""

    timestamp: datetime
    user_message: str
    bot_response: str
    intent: str
    entities: List[Dict[str, Any]]
    sentiment: str
    context_used: List[str]
    followup_questions: List[str]
    quick_actions: List[Dict[str, str]]


class ConversationMemoryService:
    """Service for managing conversation context and memory."""

    def __init__(self):
        # In-memory storage for conversation history
        # In production, this would be backed by a database
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.conversation_states: Dict[str, ConversationState] = {}
        self.pending_followups: Dict[str, List[str]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}

    def add_conversation_turn(
        self, user_id: str, user_message: str, bot_response: Dict[str, Any]
    ) -> None:
        """Add a new conversation turn to memory."""

        if user_id not in self.conversations:
            self.conversations[user_id] = []

        turn = ConversationTurn(
            timestamp=datetime.utcnow(),
            user_message=user_message,
            bot_response=bot_response.get("message", ""),
            intent=bot_response.get("intent", "unknown"),
            entities=bot_response.get("entities", []),
            sentiment=bot_response.get("sentiment", "neutral"),
            context_used=bot_response.get("context_used", []),
            followup_questions=bot_response.get("followup_questions", []),
            quick_actions=bot_response.get("quick_actions", []),
        )

        self.conversations[user_id].append(turn)

        # Keep only last 50 turns to manage memory
        if len(self.conversations[user_id]) > 50:
            self.conversations[user_id] = self.conversations[user_id][-50:]

        # Update conversation state
        self._update_conversation_state(user_id, bot_response)

        # Store pending follow-ups
        if bot_response.get("followup_questions"):
            self.pending_followups[user_id] = bot_response["followup_questions"]

    def get_conversation_context(
        self, user_id: str, turns_back: int = 5
    ) -> Dict[str, Any]:
        """Get recent conversation context for the user."""

        if user_id not in self.conversations:
            return {
                "recent_turns": [],
                "current_state": ConversationState.GREETING,
                "pending_followups": [],
                "conversation_summary": {},
                "user_preferences": {},
            }

        recent_turns = (
            self.conversations[user_id][-turns_back:]
            if self.conversations[user_id]
            else []
        )

        return {
            "recent_turns": [asdict(turn) for turn in recent_turns],
            "current_state": self.conversation_states.get(
                user_id, ConversationState.GREETING
            ),
            "pending_followups": self.pending_followups.get(user_id, []),
            "conversation_summary": self._generate_conversation_summary(user_id),
            "user_preferences": self.user_preferences.get(user_id, {}),
        }

    def get_contextual_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate contextual insights from conversation history."""

        if user_id not in self.conversations or not self.conversations[user_id]:
            return {
                "frequent_topics": [],
                "sentiment_trend": "neutral",
                "engagement_level": "new_user",
                "preferred_response_style": "detailed",
                "common_concerns": [],
            }

        turns = self.conversations[user_id]
        recent_turns = turns[-10:]  # Last 10 turns

        # Analyze frequent topics
        topics = []
        for turn in recent_turns:
            if "symptom" in turn.intent.lower():
                topics.append("symptoms")
            elif "diet" in turn.intent.lower() or "food" in turn.user_message.lower():
                topics.append("diet")
            elif "stress" in turn.user_message.lower():
                topics.append("stress")
            elif "assessment" in turn.intent.lower():
                topics.append("assessment")

        frequent_topics = list(set(topics))

        # Analyze sentiment trend
        sentiments = [turn.sentiment for turn in recent_turns if turn.sentiment]
        sentiment_trend = self._analyze_sentiment_trend(sentiments)

        # Determine engagement level
        engagement_level = (
            "high" if len(turns) > 20 else "medium" if len(turns) > 5 else "new_user"
        )

        # Analyze response preferences
        avg_response_length = (
            sum(len(turn.bot_response) for turn in recent_turns) / len(recent_turns)
            if recent_turns
            else 0
        )
        preferred_style = "detailed" if avg_response_length > 200 else "concise"

        # Extract common concerns
        concerns = []
        for turn in recent_turns:
            if any(
                word in turn.user_message.lower()
                for word in ["pain", "severe", "worried", "concerned"]
            ):
                concerns.append("pain_management")
            if any(
                word in turn.user_message.lower() for word in ["diet", "food", "eat"]
            ):
                concerns.append("dietary_guidance")
            if any(word in turn.user_message.lower() for word in ["stress", "anxiety"]):
                concerns.append("stress_management")

        return {
            "frequent_topics": frequent_topics,
            "frequent_symptoms": [],  # Add this field to prevent KeyError
            "sentiment_trend": sentiment_trend,
            "engagement_level": engagement_level,
            "preferred_response_style": preferred_style,
            "common_concerns": list(set(concerns)),
            "suggested_actions": [],  # Add this field for quick actions
            "progress_indicators": {},  # Add this field for progress context
        }

    def should_follow_up(self, user_id: str) -> Dict[str, Any]:
        """Determine if a follow-up is needed and what type."""

        if user_id not in self.conversations:
            return {"should_follow_up": False}

        last_turn = (
            self.conversations[user_id][-1] if self.conversations[user_id] else None
        )
        if not last_turn:
            return {"should_follow_up": False}

        # Check if enough time has passed since last interaction
        time_since_last = datetime.utcnow() - last_turn.timestamp

        # Follow up scenarios
        if time_since_last > timedelta(hours=24):
            if "symptom" in last_turn.intent.lower():
                return {
                    "should_follow_up": True,
                    "follow_up_type": "symptom_check",
                    "message": "How are your symptoms today? Any changes since we last talked?",
                }
            elif "assessment" in last_turn.intent.lower():
                return {
                    "should_follow_up": True,
                    "follow_up_type": "progress_check",
                    "message": "I wanted to check in on how you're feeling after our assessment yesterday.",
                }

        # Check for pending follow-ups
        if user_id in self.pending_followups and self.pending_followups[user_id]:
            return {
                "should_follow_up": True,
                "follow_up_type": "pending_questions",
                "questions": self.pending_followups[user_id],
            }

        return {"should_follow_up": False}

    def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> None:
        """Update user preferences based on interaction patterns."""

        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        self.user_preferences[user_id].update(preferences)

    def _update_conversation_state(
        self, user_id: str, bot_response: Dict[str, Any]
    ) -> None:
        """Update the current conversation state."""

        intent = bot_response.get("intent", "").lower()

        if "greeting" in intent:
            self.conversation_states[user_id] = ConversationState.GREETING
        elif "symptom" in intent:
            self.conversation_states[user_id] = ConversationState.SYMPTOM_DISCUSSION
        elif "assessment" in intent:
            self.conversation_states[user_id] = ConversationState.ASSESSMENT_IN_PROGRESS
        elif "recommendation" in intent:
            self.conversation_states[user_id] = ConversationState.RECOMMENDATION_REVIEW
        elif bot_response.get("requires_followup"):
            self.conversation_states[user_id] = ConversationState.FOLLOW_UP
        else:
            self.conversation_states[user_id] = ConversationState.GENERAL_INQUIRY

    def _generate_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate a summary of the conversation history."""

        if user_id not in self.conversations:
            return {}

        turns = self.conversations[user_id]
        if not turns:
            return {}

        # Count different types of interactions
        symptom_discussions = sum(
            1 for turn in turns if "symptom" in turn.intent.lower()
        )
        assessments = sum(1 for turn in turns if "assessment" in turn.intent.lower())
        recommendations_requested = sum(
            1 for turn in turns if "recommendation" in turn.intent.lower()
        )

        # Get most recent topics
        recent_topics = []
        for turn in turns[-5:]:
            if turn.entities:
                recent_topics.extend(
                    [entity.get("value", "") for entity in turn.entities]
                )

        return {
            "total_interactions": len(turns),
            "symptom_discussions": symptom_discussions,
            "assessments_completed": assessments,
            "recommendations_requested": recommendations_requested,
            "recent_topics": list(set(recent_topics))[:5],
            "first_interaction": turns[0].timestamp.isoformat() if turns else None,
            "last_interaction": turns[-1].timestamp.isoformat() if turns else None,
        }

    def _analyze_sentiment_trend(self, sentiments: List[str]) -> str:
        """Analyze the trend in user sentiment."""

        if not sentiments:
            return "neutral"

        # Simple sentiment trend analysis
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")

        if positive_count > negative_count:
            return "improving"
        elif negative_count > positive_count:
            return "declining"
        else:
            return "stable"

    def clear_old_conversations(self, days_old: int = 30) -> None:
        """Clear conversations older than specified days."""

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        for user_id in list(self.conversations.keys()):
            if self.conversations[user_id]:
                # Keep only recent conversations
                self.conversations[user_id] = [
                    turn
                    for turn in self.conversations[user_id]
                    if turn.timestamp > cutoff_date
                ]

                # Remove empty conversation histories
                if not self.conversations[user_id]:
                    del self.conversations[user_id]
                    if user_id in self.conversation_states:
                        del self.conversation_states[user_id]
                    if user_id in self.pending_followups:
                        del self.pending_followups[user_id]
