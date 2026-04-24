"""
Natural Language Processing Service for IBS Wellness Chatbot

This service provides advanced intent recognition, entity extraction,
and contextual understanding for more intelligent chatbot responses.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Enumeration of possible user intents."""

    GREETING = "greeting"
    SYMPTOM_INQUIRY = "symptom_inquiry"
    SYMPTOM_REPORT = "symptom_report"
    FOOD_INQUIRY = "food_inquiry"
    FOOD_REPORT = "food_report"
    MEDICATION_INQUIRY = "medication_inquiry"
    MEDICATION_REPORT = "medication_report"
    ASSESSMENT_REQUEST = "assessment_request"
    RECOMMENDATION_REQUEST = "recommendation_request"
    PROGRESS_INQUIRY = "progress_inquiry"
    EMERGENCY = "emergency"
    GENERAL_QUESTION = "general_question"
    FOLLOWUP_RESPONSE = "followup_response"
    GRATITUDE = "gratitude"
    GOODBYE = "goodbye"


class Sentiment(Enum):
    """Sentiment analysis results."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CONCERNED = "concerned"
    FRUSTRATED = "frustrated"


@dataclass
class Entity:
    """Represents an extracted entity from user input."""

    type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class IntentResult:
    """Result of intent classification."""

    intent: IntentType
    confidence: float
    entities: List[Entity]
    sentiment: Sentiment
    urgency: str  # low, medium, high, critical
    keywords: List[str]
    context_clues: List[str]


class NLPService:
    """Advanced NLP service for chatbot intelligence."""

    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        self.sentiment_patterns = self._initialize_sentiment_patterns()
        self.urgency_patterns = self._initialize_urgency_patterns()

    def analyze_message(
        self, message: str, conversation_history: Optional[List[str]] = None
    ) -> IntentResult:
        """
        Perform comprehensive analysis of user message.

        Args:
            message: User's input message
            conversation_history: Previous messages for context

        Returns:
            IntentResult with classified intent, entities, and metadata
        """
        message_lower = message.lower().strip()

        # Extract entities first
        entities = self._extract_entities(message)

        # Classify intent
        intent, intent_confidence = self._classify_intent(
            message_lower, entities, conversation_history
        )

        # Analyze sentiment
        sentiment = self._analyze_sentiment(message_lower)

        # Determine urgency
        urgency = self._determine_urgency(message_lower, entities, sentiment)

        # Extract keywords
        keywords = self._extract_keywords(message_lower)

        # Find context clues
        context_clues = self._find_context_clues(message_lower, conversation_history)

        return IntentResult(
            intent=intent,
            confidence=intent_confidence,
            entities=entities,
            sentiment=sentiment,
            urgency=urgency,
            keywords=keywords,
            context_clues=context_clues,
        )

    def _initialize_intent_patterns(self) -> Dict[IntentType, List[Dict]]:
        """Initialize patterns for intent classification."""
        return {
            IntentType.GREETING: [
                {
                    "patterns": [
                        "hello",
                        "hi",
                        "hey",
                        "good morning",
                        "good afternoon",
                        "good evening",
                    ],
                    "weight": 1.0,
                },
                {"patterns": ["start", "begin", "new session"], "weight": 0.8},
            ],
            IntentType.SYMPTOM_REPORT: [
                {
                    "patterns": [
                        "i have",
                        "i'm experiencing",
                        "i feel",
                        "i'm feeling",
                        "my stomach",
                    ],
                    "weight": 1.0,
                },
                {
                    "patterns": [
                        "pain",
                        "cramp",
                        "bloat",
                        "diarrhea",
                        "constipation",
                        "nausea",
                    ],
                    "weight": 0.9,
                },
                {
                    "patterns": ["hurts", "ache", "uncomfortable", "terrible", "awful"],
                    "weight": 0.8,
                },
            ],
            IntentType.SYMPTOM_INQUIRY: [
                {
                    "patterns": [
                        "what causes",
                        "why do i",
                        "what triggers",
                        "how to prevent",
                    ],
                    "weight": 1.0,
                },
                {
                    "patterns": [
                        "about symptoms",
                        "symptom information",
                        "tell me about",
                    ],
                    "weight": 0.8,
                },
            ],
            IntentType.FOOD_REPORT: [
                {
                    "patterns": ["i ate", "i had", "after eating", "when i eat"],
                    "weight": 1.0,
                },
                {
                    "patterns": ["food makes me", "trigger food", "bad reaction"],
                    "weight": 0.9,
                },
            ],
            IntentType.FOOD_INQUIRY: [
                {
                    "patterns": [
                        "can i eat",
                        "is it safe",
                        "what foods",
                        "diet advice",
                    ],
                    "weight": 1.0,
                },
                {
                    "patterns": ["food recommendations", "safe foods", "avoid foods"],
                    "weight": 0.9,
                },
            ],
            IntentType.MEDICATION_REPORT: [
                {
                    "patterns": ["i took", "i'm taking", "medication", "medicine"],
                    "weight": 1.0,
                },
                {"patterns": ["pill", "tablet", "dose", "prescription"], "weight": 0.8},
            ],
            IntentType.ASSESSMENT_REQUEST: [
                {
                    "patterns": [
                        "assess",
                        "evaluate",
                        "how bad",
                        "severity",
                        "rate my",
                    ],
                    "weight": 1.0,
                },
                {
                    "patterns": ["check my condition", "analyze my symptoms"],
                    "weight": 0.9,
                },
            ],
            IntentType.RECOMMENDATION_REQUEST: [
                {
                    "patterns": [
                        "recommend",
                        "suggest",
                        "advice",
                        "help me",
                        "what should i",
                    ],
                    "weight": 1.0,
                },
                {"patterns": ["tips", "guidance", "best practices"], "weight": 0.8},
            ],
            IntentType.EMERGENCY: [
                {
                    "patterns": [
                        "emergency",
                        "urgent",
                        "severe pain",
                        "can't stop",
                        "blood",
                    ],
                    "weight": 1.0,
                },
                {
                    "patterns": ["hospital", "doctor", "call 911", "help me"],
                    "weight": 0.9,
                },
            ],
            IntentType.GRATITUDE: [
                {
                    "patterns": ["thank you", "thanks", "appreciate", "helpful"],
                    "weight": 1.0,
                },
            ],
            IntentType.GOODBYE: [
                {
                    "patterns": ["bye", "goodbye", "see you", "talk later"],
                    "weight": 1.0,
                },
            ],
        }

    def _initialize_entity_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for entity extraction."""
        return {
            "symptoms": [
                "pain",
                "cramp",
                "cramping",
                "bloat",
                "bloating",
                "gas",
                "diarrhea",
                "constipation",
                "nausea",
                "vomiting",
                "heartburn",
                "reflux",
                "urgency",
                "incomplete evacuation",
                "mucus",
                "blood",
                "fatigue",
                "headache",
            ],
            "foods": [
                "dairy",
                "milk",
                "cheese",
                "yogurt",
                "gluten",
                "wheat",
                "bread",
                "pasta",
                "beans",
                "legumes",
                "onions",
                "garlic",
                "spicy",
                "fatty",
                "fried",
                "coffee",
                "alcohol",
                "soda",
                "artificial sweeteners",
                "fiber",
            ],
            "medications": [
                "imodium",
                "loperamide",
                "pepto",
                "bismuth",
                "fiber supplement",
                "probiotics",
                "antispasmodic",
                "rifaximin",
                "lubiprostone",
            ],
            "severity": [
                "mild",
                "moderate",
                "severe",
                "terrible",
                "unbearable",
                "slight",
                "intense",
                "sharp",
                "dull",
                "throbbing",
            ],
            "frequency": [
                "daily",
                "weekly",
                "monthly",
                "occasionally",
                "frequently",
                "rarely",
                "always",
                "never",
                "sometimes",
                "often",
            ],
            "time": [
                "morning",
                "afternoon",
                "evening",
                "night",
                "after meals",
                "before meals",
                "today",
                "yesterday",
                "last week",
                "recently",
            ],
        }

    def _initialize_sentiment_patterns(self) -> Dict[Sentiment, List[str]]:
        """Initialize patterns for sentiment analysis."""
        return {
            Sentiment.POSITIVE: [
                "better",
                "good",
                "great",
                "excellent",
                "improved",
                "helpful",
                "working",
                "relief",
                "comfortable",
                "happy",
                "satisfied",
            ],
            Sentiment.NEGATIVE: [
                "worse",
                "bad",
                "terrible",
                "awful",
                "horrible",
                "painful",
                "uncomfortable",
                "frustrated",
                "disappointed",
                "sad",
            ],
            Sentiment.CONCERNED: [
                "worried",
                "concerned",
                "anxious",
                "scared",
                "nervous",
                "uncertain",
                "confused",
                "unsure",
                "afraid",
            ],
            Sentiment.FRUSTRATED: [
                "frustrated",
                "annoyed",
                "fed up",
                "tired of",
                "can't take",
                "nothing works",
                "giving up",
            ],
        }

    def _initialize_urgency_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for urgency detection."""
        return {
            "critical": [
                "emergency",
                "severe pain",
                "can't stop",
                "blood",
                "vomiting blood",
                "dehydrated",
                "faint",
                "dizzy",
                "chest pain",
            ],
            "high": [
                "urgent",
                "severe",
                "unbearable",
                "can't function",
                "missed work",
                "can't sleep",
                "getting worse",
                "very painful",
            ],
            "medium": [
                "uncomfortable",
                "bothering me",
                "affecting my day",
                "moderate pain",
                "need help",
                "not sure what to do",
            ],
            "low": [
                "mild",
                "slight",
                "occasional",
                "manageable",
                "curious about",
                "wondering",
                "general question",
            ],
        }

    def _classify_intent(
        self,
        message: str,
        entities: List[Entity],
        conversation_history: Optional[List[str]] = None,
    ) -> Tuple[IntentType, float]:
        """Classify the intent of the message."""
        intent_scores = {}

        for intent_type, pattern_groups in self.intent_patterns.items():
            score = 0.0
            for pattern_group in pattern_groups:
                patterns = pattern_group["patterns"]
                weight = pattern_group["weight"]

                for pattern in patterns:
                    if pattern in message:
                        score += weight
                        break  # Only count each pattern group once

            if score > 0:
                intent_scores[intent_type] = score

        # Boost scores based on entities
        for entity in entities:
            if entity.type == "symptoms" and IntentType.SYMPTOM_REPORT in intent_scores:
                intent_scores[IntentType.SYMPTOM_REPORT] += 0.5
            elif entity.type == "foods" and IntentType.FOOD_REPORT in intent_scores:
                intent_scores[IntentType.FOOD_REPORT] += 0.5

        # Consider conversation context
        if conversation_history:
            last_message = (
                conversation_history[-1].lower() if conversation_history else ""
            )
            if "how are you" in last_message and any(
                word in message for word in ["good", "bad", "better", "worse"]
            ):
                intent_scores[IntentType.FOLLOWUP_RESPONSE] = (
                    intent_scores.get(IntentType.FOLLOWUP_RESPONSE, 0) + 1.0
                )

        if not intent_scores:
            return IntentType.GENERAL_QUESTION, 0.5

        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / 2.0, 1.0)  # Normalize confidence

        return best_intent, confidence

    def _extract_entities(self, message: str) -> List[Entity]:
        """Extract entities from the message."""
        entities = []
        message_lower = message.lower()

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    start_pos = message_lower.find(pattern)
                    end_pos = start_pos + len(pattern)

                    entities.append(
                        Entity(
                            type=entity_type,
                            value=pattern,
                            confidence=0.8,
                            start_pos=start_pos,
                            end_pos=end_pos,
                        )
                    )

        return entities

    def _analyze_sentiment(self, message: str) -> Sentiment:
        """Analyze the sentiment of the message."""
        sentiment_scores = {}

        for sentiment, patterns in self.sentiment_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message)
            if score > 0:
                sentiment_scores[sentiment] = score

        if not sentiment_scores:
            return Sentiment.NEUTRAL

        return max(sentiment_scores, key=sentiment_scores.get)

    def _determine_urgency(
        self, message: str, entities: List[Entity], sentiment: Sentiment
    ) -> str:
        """Determine the urgency level of the message."""
        for urgency_level, patterns in self.urgency_patterns.items():
            if any(pattern in message for pattern in patterns):
                return urgency_level

        # Boost urgency based on sentiment and entities
        if sentiment in [Sentiment.CONCERNED, Sentiment.FRUSTRATED]:
            return "medium"

        severe_symptoms = ["severe", "unbearable", "blood", "vomiting"]
        if any(entity.value in severe_symptoms for entity in entities):
            return "high"

        return "low"

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract important keywords from the message."""
        # Remove common stop words
        stop_words = {
            "i",
            "me",
            "my",
            "myself",
            "we",
            "our",
            "ours",
            "ourselves",
            "you",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "he",
            "him",
            "his",
            "himself",
            "she",
            "her",
            "hers",
            "herself",
            "it",
            "its",
            "itself",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "what",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
        }

        words = re.findall(r"\b\w+\b", message.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords[:10]  # Return top 10 keywords

    def _find_context_clues(
        self, message: str, conversation_history: Optional[List[str]] = None
    ) -> List[str]:
        """Find contextual clues that might influence the response."""
        clues = []

        # Time-based clues
        if any(
            time_word in message
            for time_word in ["today", "yesterday", "this morning", "last night"]
        ):
            clues.append("recent_timeframe")

        # Comparison clues
        if any(
            comp_word in message
            for comp_word in ["better", "worse", "same", "different"]
        ):
            clues.append("comparison_mentioned")

        # Question indicators
        if message.startswith(
            ("what", "how", "why", "when", "where", "can", "should", "would")
        ):
            clues.append("direct_question")

        # Emotional indicators
        if any(
            emotion in message
            for emotion in ["frustrated", "worried", "scared", "happy", "relieved"]
        ):
            clues.append("emotional_content")

        return clues
