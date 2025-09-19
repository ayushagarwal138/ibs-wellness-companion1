"""
Dynamic response templates for personalized and contextual chatbot responses.
"""

import random
from typing import Dict, List, Any
from enum import Enum

class ResponseTone(Enum):
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    ENTHUSIASTIC = "enthusiastic"
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"

class ResponseTemplateService:
    """Service for generating dynamic, personalized response templates."""
    
    def __init__(self):
        self.greeting_templates = {
            ResponseTone.SUPPORTIVE: [
                "Hello! I'm here to support you with your IBS journey. How can I help you today?",
                "Hi there! I'm your wellness companion, ready to assist with any IBS-related questions or concerns.",
                "Welcome back! I'm here to provide personalized support for your digestive health needs.",
                "Hello! Let's work together to manage your IBS symptoms effectively. What's on your mind?",
                "Hi! I'm here to offer guidance and support for your wellness journey. How are you feeling today?"
            ],
            ResponseTone.ENCOURAGING: [
                "Hello! You're taking great steps by seeking support for your IBS management. How can I help?",
                "Hi there! Every conversation is a step forward in your wellness journey. What would you like to discuss?",
                "Welcome! You're doing amazing by being proactive about your health. How can I assist you today?",
                "Hello! Your commitment to managing your IBS is inspiring. What can I help you with?",
                "Hi! You're on the right path to better digestive health. How can I support you today?"
            ],
            ResponseTone.ENTHUSIASTIC: [
                "Hello! I'm excited to help you on your IBS wellness journey! What can we tackle together today?",
                "Hi there! Ready to make some positive changes for your digestive health? Let's get started!",
                "Welcome! I'm thrilled to be your wellness companion. What exciting progress can we make today?",
                "Hello! Let's turn your IBS challenges into victories! How can I help you succeed today?",
                "Hi! Your wellness journey is full of possibilities. What would you like to explore today?"
            ]
        }
        
        self.symptom_acknowledgment_templates = {
            ResponseTone.EMPATHETIC: [
                "I understand how challenging {symptom} can be. Let's work together to find some relief.",
                "Thank you for sharing about your {symptom}. I'm here to help you manage this effectively.",
                "I hear you about the {symptom} you're experiencing. Let's explore some strategies to help.",
                "Dealing with {symptom} can be really tough. I'm here to support you through this.",
                "I appreciate you trusting me with your {symptom} concerns. Let's find ways to improve this."
            ],
            ResponseTone.SUPPORTIVE: [
                "I'm glad you're sharing your {symptom} experience with me. Together, we can work on managing this.",
                "Thank you for being open about your {symptom}. This information helps me provide better support.",
                "Your {symptom} is important to address. Let's look at some personalized approaches.",
                "I'm here to help with your {symptom} management. Let's explore what might work best for you.",
                "Sharing about your {symptom} is a positive step. Let's work on strategies to help you feel better."
            ]
        }
        
        self.progress_celebration_templates = {
            ResponseTone.ENTHUSIASTIC: [
                "That's fantastic progress! Your dedication to managing your IBS is really paying off!",
                "Wonderful news! You're making excellent strides in your wellness journey!",
                "Amazing! Your commitment to your health is showing great results!",
                "That's incredible progress! You should be proud of how far you've come!",
                "Excellent work! Your positive changes are making a real difference!"
            ],
            ResponseTone.ENCOURAGING: [
                "Great progress! You're moving in the right direction with your IBS management.",
                "Well done! These positive changes show your dedication is working.",
                "Nice work! You're building healthy habits that will serve you well.",
                "Good progress! Every positive step counts in your wellness journey.",
                "Keep it up! You're making meaningful improvements to your health."
            ]
        }
        
        self.recommendation_templates = {
            "dietary": {
                ResponseTone.PROFESSIONAL: [
                    "Based on your symptoms, I recommend considering these dietary adjustments:",
                    "Here are some evidence-based dietary strategies that might help:",
                    "Let's explore these nutritional approaches for your symptoms:",
                    "These dietary modifications could provide relief for your condition:"
                ],
                ResponseTone.SUPPORTIVE: [
                    "I'd like to suggest some gentle dietary changes that might help you feel better:",
                    "Here are some food-related strategies we could try together:",
                    "Let's look at some nourishing approaches to support your digestive health:",
                    "I have some dietary suggestions that might bring you some relief:"
                ]
            },
            "lifestyle": {
                ResponseTone.ENCOURAGING: [
                    "Here are some lifestyle changes that could make a positive difference:",
                    "Let's explore these empowering lifestyle strategies:",
                    "These lifestyle adjustments could help you feel more in control:",
                    "Consider these positive lifestyle changes for better symptom management:"
                ],
                ResponseTone.ENTHUSIASTIC: [
                    "I'm excited to share these lifestyle strategies that could transform your wellness:",
                    "Let's dive into these amazing lifestyle approaches for better health:",
                    "These lifestyle changes could be game-changers for your IBS management:",
                    "Get ready to embrace these powerful lifestyle modifications:"
                ]
            }
        }
        
        self.follow_up_templates = {
            "symptom_check": [
                "I wanted to check in about the {symptom} you mentioned {timeframe}. How are you feeling now?",
                "How has your {symptom} been since we last talked {timeframe}?",
                "I'm following up on the {symptom} from our previous conversation. Any changes?",
                "Let's see how you're doing with the {symptom} we discussed {timeframe}."
            ],
            "recommendation_follow_up": [
                "How did the {recommendation_type} suggestion work out for you?",
                "I'd love to hear how the {recommendation_type} recommendation went!",
                "Have you had a chance to try the {recommendation_type} approach we discussed?",
                "How has your experience been with the {recommendation_type} strategy?"
            ]
        }
        
        self.quick_action_templates = {
            "symptom_related": [
                {"text": "Log this symptom", "action": "log_symptom"},
                {"text": "Get recommendations", "action": "get_recommendations"},
                {"text": "Track severity", "action": "track_severity"},
                {"text": "View similar cases", "action": "view_patterns"}
            ],
            "assessment_related": [
                {"text": "Start assessment", "action": "start_assessment"},
                {"text": "Quick check-in", "action": "quick_checkin"},
                {"text": "View progress", "action": "view_progress"},
                {"text": "Compare trends", "action": "compare_trends"}
            ],
            "general_support": [
                {"text": "Get tips", "action": "get_tips"},
                {"text": "Find resources", "action": "find_resources"},
                {"text": "Connect with community", "action": "community_connect"},
                {"text": "Schedule reminder", "action": "set_reminder"}
            ]
        }
    
    def get_greeting_message(self, tone: ResponseTone = ResponseTone.SUPPORTIVE, user_name: str = None) -> str:
        """Get a personalized greeting message."""
        templates = self.greeting_templates.get(tone, self.greeting_templates[ResponseTone.SUPPORTIVE])
        message = random.choice(templates)
        
        if user_name:
            message = message.replace("Hello!", f"Hello, {user_name}!")
            message = message.replace("Hi there!", f"Hi, {user_name}!")
            message = message.replace("Welcome!", f"Welcome, {user_name}!")
        
        return message
    
    def get_symptom_acknowledgment(self, symptom: str, tone: ResponseTone = ResponseTone.EMPATHETIC) -> str:
        """Get an empathetic symptom acknowledgment message."""
        templates = self.symptom_acknowledgment_templates.get(tone, self.symptom_acknowledgment_templates[ResponseTone.EMPATHETIC])
        message = random.choice(templates)
        return message.format(symptom=symptom)
    
    def get_progress_celebration(self, tone: ResponseTone = ResponseTone.ENCOURAGING) -> str:
        """Get a progress celebration message."""
        templates = self.progress_celebration_templates.get(tone, self.progress_celebration_templates[ResponseTone.ENCOURAGING])
        return random.choice(templates)
    
    def get_recommendation_intro(self, recommendation_type: str, tone: ResponseTone = ResponseTone.SUPPORTIVE) -> str:
        """Get an introduction for recommendations."""
        category_templates = self.recommendation_templates.get(recommendation_type, self.recommendation_templates["lifestyle"])
        templates = category_templates.get(tone, category_templates[ResponseTone.SUPPORTIVE])
        return random.choice(templates)
    
    def get_follow_up_message(self, follow_up_type: str, **kwargs) -> str:
        """Get a follow-up message with context."""
        templates = self.follow_up_templates.get(follow_up_type, self.follow_up_templates["symptom_check"])
        message = random.choice(templates)
        return message.format(**kwargs)
    
    def get_contextual_quick_actions(self, context_type: str, additional_actions: List[Dict] = None) -> List[Dict]:
        """Get contextual quick action buttons."""
        base_actions = self.quick_action_templates.get(context_type, self.quick_action_templates["general_support"])
        actions = base_actions.copy()
        
        if additional_actions:
            actions.extend(additional_actions)
        
        # Limit to 4 actions for better UX
        return actions[:4]
    
    def personalize_message(self, message: str, user_context: Dict[str, Any]) -> str:
        """Personalize a message based on user context."""
        # Add user name if available
        if user_context.get("name"):
            message = message.replace("{user_name}", user_context["name"])
        
        # Add time-based personalization
        if user_context.get("time_of_day"):
            time_greetings = {
                "morning": "Good morning",
                "afternoon": "Good afternoon", 
                "evening": "Good evening"
            }
            time_greeting = time_greetings.get(user_context["time_of_day"], "Hello")
            message = message.replace("Hello", time_greeting)
            message = message.replace("Hi", time_greeting)
        
        # Add frequency-based personalization
        if user_context.get("visit_frequency") == "frequent":
            message = message.replace("Welcome!", "Welcome back!")
            message = message.replace("Hello!", "Hello again!")
        
        return message
    
    def generate_dynamic_response(self, intent: str, context: Dict[str, Any], tone: ResponseTone = ResponseTone.SUPPORTIVE) -> Dict[str, Any]:
        """Generate a complete dynamic response with templates."""
        
        response = {
            "message": "",
            "quick_actions": [],
            "followup_questions": [],
            "tone": tone.value
        }
        
        if intent == "greeting":
            response["message"] = self.get_greeting_message(tone, context.get("user_name"))
            response["quick_actions"] = self.get_contextual_quick_actions("general_support")
            
        elif intent == "symptom_discussion":
            symptom = context.get("symptom", "symptoms")
            response["message"] = self.get_symptom_acknowledgment(symptom, ResponseTone.EMPATHETIC)
            response["quick_actions"] = self.get_contextual_quick_actions("symptom_related")
            
        elif intent == "progress_inquiry":
            if context.get("has_progress"):
                response["message"] = self.get_progress_celebration(ResponseTone.ENCOURAGING)
            response["quick_actions"] = self.get_contextual_quick_actions("assessment_related")
        
        # Personalize the final message
        response["message"] = self.personalize_message(response["message"], context)
        
        return response