"""
IBS Chat Service

This service handles chatbot conversations, maintains context,
integrates IBS severity detection, and provides personalized recommendations.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, select

from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse,
    ChatbotResponse, ConversationContext, IBSAssessment, MessageType
)
from app.services.ibs_detection_service import IBSDetectionService
from app.services.recommendation_service import RecommendationService
from app.services.ml_integration_service import MLIntegrationService
from app.services.nlp_service import NLPService, IntentType
from app.services.conversation_memory import ConversationMemoryService
from app.services.response_templates import ResponseTemplateService, ResponseTone
from app.core.logging import StructuredLogger


class ChatService:
    """Service for managing IBS chatbot conversations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = StructuredLogger("chat_service")
        self.ibs_detection = IBSDetectionService(db)
        self.recommendation = RecommendationService(db)
        self.ml_integration = MLIntegrationService(db)
        self.nlp = NLPService()  # Initialize NLP service
        self.memory = ConversationMemoryService()
        self.templates = ResponseTemplateService()
        
        # Enhanced greeting messages with more variety
        self.greeting_messages = [
            "Hello! I'm your IBS wellness assistant. I'm here to help you manage your symptoms and improve your quality of life.",
            "Hi there! Ready to take control of your IBS journey? I can help with symptom tracking, diet advice, and personalized recommendations.",
            "Welcome! I'm here to support you with your IBS management. Whether you need symptom analysis or lifestyle tips, I've got you covered.",
            "Hello! Let's work together to understand your IBS patterns and find what works best for you.",
            "Hi! I'm your personal IBS companion. I can help you track symptoms, identify triggers, and provide tailored advice."
        ]
        
        self.assessment_questions = [
            "How have your IBS symptoms been over the past few weeks?",
            "Have you noticed any specific foods that trigger your symptoms?",
            "How would you rate your current pain and discomfort levels?",
            "Are you currently taking any medications for your IBS?",
            "How are your symptoms affecting your daily activities?"
        ]
    
    async def create_session(self, user: User, title: Optional[str] = None) -> ChatSessionResponse:
        """Create a new chat session for the user."""
        session_data = ChatSessionCreate(
            title=title or f"Chat Session - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            metadata={"created_via": "api", "user_agent": "web"}
        )
        
        # Create database record
        db_session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=session_data.title,
            session_metadata=session_data.metadata,
            started_at=datetime.utcnow(),
            is_active=True
        )
        
        self.db.add(db_session)
        await self.db.commit()
        await self.db.refresh(db_session)
        
        # Send welcome message
        welcome_message = self._get_welcome_message(user)
        await self._add_system_message(db_session.id, user.id, welcome_message)
        
        return ChatSessionResponse(
            id=str(db_session.id),
            user_id=str(db_session.user_id),
            title=db_session.title,
            started_at=db_session.started_at,
            ended_at=db_session.ended_at,
            is_active=db_session.is_active,
            metadata=db_session.session_metadata,
            created_at=db_session.created_at or db_session.started_at
        )
    
    async def send_message(self, user: User, session_id: str, message: str, 
                    include_assessment: bool = True) -> ChatbotResponse:
        """Process user message and generate chatbot response."""
        
        # Get or create session
        session = await self._get_or_create_session(user, session_id)
        
        # Store user message
        user_message = await self._add_user_message(session.id, user.id, message)
        
        # Get conversation context
        context = await self._build_conversation_context(user, session.id)
        
        # Generate response based on message content and context
        response_data = await self._generate_response(user, message, context, include_assessment)
        
        # Store assistant response
        assistant_message = await self._add_assistant_message(
            session.id, user.id, response_data["message"], response_data.get("metadata", {})
        )
        
        return ChatbotResponse(
            message=response_data["message"],
            session_id=str(session.id),
            message_id=str(assistant_message.id),
            ibs_assessment=response_data.get("ibs_assessment"),
            recommendations=response_data.get("recommendations", []),
            context_used=response_data.get("context_used", []),
            confidence=response_data.get("confidence", 0.8),
            requires_followup=response_data.get("requires_followup", False),
            followup_questions=response_data.get("followup_questions", [])
        )
    
    async def get_session_history(self, user: User, session_id: str, limit: int = 50) -> List[ChatMessageResponse]:
        """Get chat history for a session."""
        stmt = select(ChatMessage).filter(
            and_(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user.id
            )
        ).order_by(ChatMessage.sent_at).limit(limit)
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        return [
            ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                user_id=msg.user_id,
                content=msg.content,
                message_type=MessageType(msg.message_type),
                metadata=msg.message_metadata,
                sent_at=msg.sent_at,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    
    async def get_user_sessions(self, user: User, limit: int = 20) -> List[ChatSessionResponse]:
        """Get user's chat sessions."""
        stmt = select(ChatSession).filter(
            ChatSession.user_id == user.id
        ).order_by(desc(ChatSession.started_at)).limit(limit)
        
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        return [
            ChatSessionResponse(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                started_at=session.started_at,
                ended_at=session.ended_at,
                is_active=session.is_active,
                metadata=session.session_metadata,
                created_at=session.created_at
            )
            for session in sessions
        ]
    
    async def _get_or_create_session(self, user: User, session_id: Optional[str]) -> ChatSession:
        """Get existing session or create new one."""
        if session_id:
            stmt = select(ChatSession).filter(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user.id,
                    ChatSession.is_active == True
                )
            )
            result = await self.db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                return session
        
        # Create new session
        session_response = await self.create_session(user)
        stmt = select(ChatSession).filter(ChatSession.id == session_response.id)
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def _build_conversation_context(self, user: User, session_id: str) -> ConversationContext:
        """Build conversation context from user data and chat history."""
        
        # Get recent symptoms (last 30 days)
        recent_symptoms = await self._get_recent_user_data(user.id, "symptoms", 30)
        
        # Get recent food reactions (last 30 days)
        recent_foods = await self._get_recent_user_data(user.id, "food_reactions", 30)
        
        # Get recent medications (last 30 days)
        recent_medications = await self._get_recent_user_data(user.id, "medications", 30)
        
        # Get conversation history (last 10 messages)
        stmt = select(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(desc(ChatMessage.sent_at)).limit(10)
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        conversation_history = [msg.content for msg in reversed(messages)]
        
        # Get previous assessments
        previous_assessments = await self._get_previous_assessments(user.id)
        
        return ConversationContext(
            recent_symptoms=recent_symptoms,
            recent_foods=recent_foods,
            recent_medications=recent_medications,
            user_preferences=await self._get_user_preferences(user),
            previous_assessments=previous_assessments,
            conversation_history=conversation_history
        )
    
    async def _generate_response(self, user: User, message: str, context: ConversationContext, 
                         include_assessment: bool) -> Dict[str, Any]:
        """Generate intelligent chatbot response using advanced NLP analysis and conversation memory."""
        
        # Get conversation history and insights
        conversation_context = self.memory.get_conversation_context(user.id)
        contextual_insights = self.memory.get_contextual_insights(user.id)
        
        # Enhance context with conversation memory
        enhanced_context = ConversationContext(
            user_id=str(user.id),
            current_message=message,
            recent_symptoms=context.recent_symptoms,
            recent_foods=context.recent_foods,
            recent_medications=context.recent_medications,
            user_preferences=context.user_preferences,
            previous_assessments=context.previous_assessments,
            conversation_history=conversation_context["recent_turns"],
            current_state=conversation_context["current_state"].value if hasattr(conversation_context["current_state"], 'value') else str(conversation_context["current_state"]),
            pending_followups=conversation_context["pending_followups"]
        )
        
        # Analyze message with NLP service using enhanced context
        nlp_result = self.nlp.analyze_message(message, enhanced_context.conversation_history)
        
        # Base response structure
        response_data = {
            "message": "",
            "metadata": {
                "intent": nlp_result.intent.value,
                "confidence": nlp_result.confidence,
                "sentiment": nlp_result.sentiment.value,
                "urgency": nlp_result.urgency,
                "entities": [{"type": e.type, "value": e.value} for e in nlp_result.entities]
            },
            "context_used": [],
            "confidence": nlp_result.confidence,
            "requires_followup": False,
            "followup_questions": [],
            "quick_actions": []  # New field for quick action buttons
        }
        
        # Check for follow-up scenarios
        follow_up_check = self.memory.should_follow_up(user.id)
        if follow_up_check["should_follow_up"] and not nlp_result.intent == IntentType.GREETING:
            # Handle follow-up scenarios
            response_data.update(await self._handle_follow_up(user, enhanced_context, nlp_result, follow_up_check))
        else:
            # Route to appropriate handler based on NLP analysis
            if nlp_result.intent == IntentType.GREETING:
                response_data.update(self._handle_greeting(user, enhanced_context, nlp_result))
                
            elif nlp_result.intent in [IntentType.SYMPTOM_REPORT, IntentType.SYMPTOM_INQUIRY]:
                response_data.update(await self._handle_symptom_discussion(user, message, enhanced_context, include_assessment, nlp_result))
                
            elif nlp_result.intent in [IntentType.FOOD_REPORT, IntentType.FOOD_INQUIRY]:
                response_data.update(await self._handle_food_discussion(user, message, enhanced_context, nlp_result))
                
            elif nlp_result.intent in [IntentType.MEDICATION_REPORT, IntentType.MEDICATION_INQUIRY]:
                response_data.update(await self._handle_medication_discussion(user, message, enhanced_context, nlp_result))
                
            elif nlp_result.intent == IntentType.RECOMMENDATION_REQUEST:
                response_data.update(await self._handle_recommendation_request(user, enhanced_context, include_assessment, nlp_result))
                
            elif nlp_result.intent == IntentType.ASSESSMENT_REQUEST:
                response_data.update(await self._handle_assessment_request(user, enhanced_context, nlp_result))
                
            else:
                response_data.update(await self._handle_general_question(user, message, enhanced_context, nlp_result))
        
        # Enhance response with contextual insights
        response_data = self._enhance_response_with_context(response_data, contextual_insights)
        
        # Add conversation metadata
        response_data.update({
            "conversation_context": {
                "state": enhanced_context.current_state.value if hasattr(enhanced_context.current_state, 'value') else str(enhanced_context.current_state),
                "turn_count": len(conversation_context["recent_turns"]) + 1,
                "engagement_level": contextual_insights["engagement_level"]
            }
        })
        
        # Store conversation turn in memory
        self.memory.add_conversation_turn(user.id, message, response_data)
        
        return response_data

    def _get_time_of_day(self) -> str:
        """Get current time of day for personalization."""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _handle_greeting(self, user: User, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle greeting messages with dynamic templates and personalization."""
        
        # Determine appropriate tone based on sentiment and context
        sentiment = nlp_result.sentiment.value if hasattr(nlp_result.sentiment, 'value') else str(nlp_result.sentiment)
        
        if sentiment == "positive":
            tone = ResponseTone.ENTHUSIASTIC
        elif sentiment == "negative":
            tone = ResponseTone.EMPATHETIC
        else:
            tone = ResponseTone.SUPPORTIVE
        
        # Get user context for personalization
        user_context = {
            "user_name": user.name if hasattr(user, 'name') else None,
            "time_of_day": self._get_time_of_day(),
            "visit_frequency": "frequent" if len(getattr(context, 'conversation_history', [])) > 5 else "new"
        }
        
        # Generate dynamic greeting using templates
        template_response = self.templates.generate_dynamic_response(
            "greeting", 
            user_context, 
            tone
        )
        
        # Add contextual information based on user history
        additional_context = ""
        if context.recent_symptoms:
            additional_context += " I see you've been tracking symptoms recently."
        elif context.previous_assessments:
            last_assessment = context.previous_assessments[-1]
            additional_context += f" Your last assessment showed {last_assessment.severity.value} symptoms."
        
        return {
            "message": template_response["message"] + additional_context,
            "context_used": ["greeting_personalization", "sentiment_analysis", "user_history"],
            "requires_followup": True,
            "followup_questions": [
                "How are you feeling today?",
                "What would you like to focus on in our conversation?",
                "Is there anything specific about your IBS that's concerning you?"
            ],
            "quick_actions": template_response["quick_actions"],
            "tone": template_response["tone"]
        }
    
    async def _handle_symptom_discussion(self, user: User, message: str, context: ConversationContext, 
                                 include_assessment: bool, nlp_result) -> Dict[str, Any]:
        """Handle symptom-related discussions with intelligent analysis."""
        
        # Extract symptoms from NLP analysis
        symptoms = []
        severity_indicators = []
        
        for entity in nlp_result.entities:
            if entity.type == "SYMPTOM":
                symptoms.append(entity.value)
            elif entity.type == "SEVERITY":
                severity_indicators.append(entity.value)
        
        # If no symptoms detected, ask for clarification
        if not symptoms:
            return {
                "message": "I'd like to help you with your symptoms. Could you tell me more specifically what you're experiencing? For example, are you having abdominal pain, bloating, changes in bowel movements, or other digestive issues?",
                "context_used": ["nlp_analysis"],
                "requires_followup": True,
                "followup_questions": [
                    "Are you experiencing abdominal pain?",
                    "Do you have bloating or gas?",
                    "Any changes in your bowel movements?",
                    "How long have you been experiencing these symptoms?"
                ],
                "quick_actions": [
                    {"text": "Abdominal Pain", "action": "symptom_pain"},
                    {"text": "Bloating", "action": "symptom_bloating"},
                    {"text": "Bowel Changes", "action": "symptom_bowel"},
                    {"text": "Start Assessment", "action": "full_assessment"}
                ]
            }
        
        # Analyze sentiment for symptom severity context
        emotional_context = ""
        if nlp_result.sentiment.value == "negative":
            emotional_context = "I understand you're going through a difficult time with these symptoms. "
        elif nlp_result.sentiment.value == "positive":
            emotional_context = "I'm glad you're taking a proactive approach to managing your symptoms. "
        
        # Generate intelligent response based on detected symptoms
        response_parts = [emotional_context]
        context_used = ["symptoms_data", "nlp_analysis"]
        
        if "pain" in " ".join(symptoms).lower():
            response_parts.append("Abdominal pain can be challenging to manage. ")
            if any(word in message.lower() for word in ["severe", "intense", "unbearable"]):
                response_parts.append("Given the intensity you're describing, it's important to track this carefully. ")
        
        if "bloating" in " ".join(symptoms).lower():
            response_parts.append("Bloating is a common IBS symptom that can often be managed through dietary adjustments. ")
        
        # Provide context from recent symptoms if available
        if context.recent_symptoms:
            symptom_count = len(context.recent_symptoms)
            response_parts.append(f"I can see you've logged {symptom_count} symptom entries in the past month. ")
            
            # Identify patterns
            if symptom_count >= 5:
                response_parts.append("Based on your recent logs, I can help identify patterns and triggers. ")
        
        # Perform assessment if requested
        assessment = None
        recommendations = []
        
        if include_assessment:
            try:
                assessment = await self.ibs_detection.assess_ibs_severity(user)
                context_used.append("ibs_assessment")
                
                response_parts.append(f"Based on your recent data, your current IBS severity appears to be {assessment.severity.value}. ")
                
                if assessment.factors:
                    factors_text = ", ".join(assessment.factors[:3])
                    response_parts.append(f"Key contributing factors include: {factors_text}. ")
                
                # Get recommendations
                recommendations = self.recommendation_service.generate_recommendations(user, assessment)
                if recommendations:
                    response_parts.append("I have some personalized recommendations that might help. ")
                    
            except Exception as e:
                response_parts.append("I'm having trouble accessing your recent data for assessment. Please make sure you've been logging your symptoms regularly. ")
        
        # Add recommendations
        response_parts.append("Would you like me to suggest some management strategies or provide dietary recommendations?")
        
        return {
            "message": "".join(response_parts),
            "context_used": context_used,
            "ibs_assessment": assessment,
            "recommendations": recommendations[:3] if recommendations else [],
            "detected_symptoms": symptoms,
            "requires_followup": True,
            "followup_questions": [
                "How long have you been experiencing these symptoms?",
                "Have you noticed any triggers?",
                "Would you like dietary recommendations?",
                "Should we create a symptom tracking plan?"
            ],
            "quick_actions": [
                {"text": "Get Recommendations", "action": "get_recommendations"},
                {"text": "Track Symptoms", "action": "symptom_tracking"},
                {"text": "Diet Plan", "action": "diet_plan"},
                {"text": "Trigger Analysis", "action": "trigger_analysis"}
            ]
        }
    
    async def _handle_food_discussion(self, user: User, message: str, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle food and diet-related discussions."""
        
        response_parts = []
        context_used = ["food_data"]
        
        response_parts.append("Diet plays a crucial role in managing IBS symptoms. Let me share some insights based on your data.")
        
        if context.recent_foods:
            reaction_count = len(context.recent_foods)
            response_parts.append(f"You've logged {reaction_count} food reactions recently.")
            
            # Identify potential triggers
            trigger_foods = self.recommendation._analyze_food_triggers(user.id)
            if trigger_foods:
                triggers_text = ", ".join(trigger_foods[:3])
                response_parts.append(f"Foods that seem to trigger reactions for you include: {triggers_text}.")
                response_parts.append("Consider eliminating these foods temporarily to see if symptoms improve.")
        else:
            response_parts.append("I don't see much food tracking data yet. Keeping a food diary can help identify triggers.")
        
        # General diet advice
        response_parts.append("The low-FODMAP diet is often effective for IBS management. Would you like specific guidance on this approach?")
        
        return {
            "message": " ".join(response_parts),
            "context_used": context_used,
            "requires_followup": True,
            "followup_questions": [
                "Would you like me to explain the low-FODMAP diet?",
                "Are there specific foods you're concerned about?",
                "Would you like meal planning suggestions?"
            ]
        }
    
    async def _handle_medication_discussion(self, user: User, message: str, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle medication-related discussions."""
        
        response_parts = []
        context_used = ["medication_data"]
        
        if context.recent_medications:
            med_count = len(set(med.get("medication_name") for med in context.recent_medications))
            response_parts.append(f"I see you're currently tracking {med_count} different medications.")
            response_parts.append("Medication adherence is important for managing IBS effectively.")
        else:
            response_parts.append("I don't see any medication tracking data yet.")
            response_parts.append("If you're taking IBS medications, tracking their effectiveness can be very helpful.")
        
        response_parts.append("Remember, I can't provide medical advice, but I can help you track patterns and prepare questions for your healthcare provider.")
        
        return {
            "message": " ".join(response_parts),
            "context_used": context_used,
            "requires_followup": True,
            "followup_questions": [
                "Are you currently taking any IBS medications?",
                "Would you like tips on tracking medication effectiveness?",
                "Do you have questions to discuss with your doctor?"
            ]
        }
    
    async def _handle_recommendation_request(self, user: User, context: ConversationContext, 
                                     include_assessment: bool, nlp_result) -> Dict[str, Any]:
        """Handle requests for recommendations."""
        
        response_parts = []
        recommendations = []
        assessment = None
        
        try:
            # Get current assessment
            assessment = await self.ibs_detection.assess_ibs_severity(user)
            
            # Enhance assessment with ML insights
            enhanced_assessment = self.ml_integration.enhance_severity_assessment(assessment, user)
            
            # Generate ML-enhanced recommendations
            recommendations = self.ml_integration.generate_personalized_recommendations(user, enhanced_assessment)
            
            # Get flare-up risk prediction
            flareup_risk = self.ml_integration.predict_flareup_risk(user, days_ahead=7)
            
            response_parts.append(f"Based on your current IBS severity level ({enhanced_assessment.severity.value}), here are my top recommendations:")
            
            # Add flare-up risk information
            if flareup_risk["risk_level"] != "low":
                response_parts.append(f"⚠️ Flare-up risk in next 7 days: {flareup_risk['risk_level']} ({flareup_risk['risk_score']:.0%})")
                if flareup_risk["factors"]:
                    response_parts.append(f"Key risk factors: {', '.join(flareup_risk['factors'][:2])}")
            
            # Summarize top recommendations
            for i, rec in enumerate(recommendations[:3], 1):
                response_parts.append(f"{i}. {rec.title}: {rec.description}")
            
            if len(recommendations) > 3:
                response_parts.append(f"I have {len(recommendations) - 3} additional recommendations available.")
                
        except Exception as e:
            response_parts.append("I need more data to provide personalized recommendations.")
            response_parts.append("Please make sure you're regularly logging your symptoms, food reactions, and medications.")
        
        return {
            "message": " ".join(response_parts),
            "ibs_assessment": enhanced_assessment if 'enhanced_assessment' in locals() else assessment,
            "recommendations": recommendations if 'recommendations' in locals() else [],
            "flareup_prediction": flareup_risk if 'flareup_risk' in locals() else None,
            "context_used": ["assessment", "recommendations", "ml_prediction"],
            "requires_followup": True,
            "followup_questions": [
                "Would you like more details about any of these recommendations?",
                "Which area would you like to focus on first?",
                "Do you have questions about implementing these suggestions?"
            ]
        }
    
    async def _handle_progress_inquiry(self, user: User, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle inquiries about user's progress with intelligent analysis."""
        
        try:
            # Get comprehensive progress data
            progress_data = await self._get_user_progress(user.id)
            
            if not progress_data or not progress_data.get('has_data'):
                return {
                    "message": "I don't see much tracking data yet to analyze your progress. To provide meaningful insights, I'd recommend logging your symptoms, meals, and activities regularly. Would you like me to help you get started with tracking?",
                    "context_used": ["progress_inquiry", "data_availability"],
                    "requires_followup": True,
                    "followup_questions": [
                        "Would you like to start tracking your symptoms?",
                        "Should I help you set up a daily logging routine?",
                        "Do you want to log your current symptoms now?"
                    ],
                    "quick_actions": [
                        {"text": "Start Tracking", "action": "begin_tracking"},
                        {"text": "Log Symptoms", "action": "symptom_entry"},
                        {"text": "Setup Routine", "action": "tracking_setup"}
                    ]
                }
            
            # Analyze sentiment to tailor response
            response_parts = []
            if nlp_result.sentiment.value == "positive":
                response_parts.append("I'm glad you're interested in tracking your progress! ")
            elif nlp_result.sentiment.value == "negative":
                response_parts.append("I understand you might be concerned about your progress. Let me share what I've observed. ")
            else:
                response_parts.append("Let me give you an overview of your IBS management progress. ")
            
            # Symptom trends
            if progress_data.get('symptom_trend'):
                trend = progress_data['symptom_trend']
                if trend == 'improving':
                    response_parts.append("Great news! Your symptoms have been trending in a positive direction over the past month. ")
                elif trend == 'worsening':
                    response_parts.append("I've noticed your symptoms have been more challenging lately. ")
                else:
                    response_parts.append("Your symptoms have been relatively stable recently. ")
            
            # Severity changes
            if progress_data.get('severity_changes'):
                changes = progress_data['severity_changes']
                response_parts.append(f"Your average IBS severity has changed from {changes['previous']} to {changes['current']} over the past month. ")
            
            # Trigger identification
            if progress_data.get('identified_triggers'):
                triggers = progress_data['identified_triggers'][:3]  # Top 3
                response_parts.append(f"I've identified potential triggers including: {', '.join(triggers)}. ")
            
            # Successful strategies
            if progress_data.get('successful_strategies'):
                strategies = progress_data['successful_strategies'][:2]  # Top 2
                response_parts.append(f"Strategies that seem to be working well for you include: {', '.join(strategies)}. ")
            
            # Recommendations based on progress
            if progress_data.get('symptom_trend') == 'improving':
                response_parts.append("Keep up the great work! Let's continue with your current approach and maybe explore some additional wellness strategies. ")
            elif progress_data.get('symptom_trend') == 'worsening':
                response_parts.append("Let's work together to identify what might be causing this increase and adjust your management plan. ")
            else:
                response_parts.append("Your stable progress is good - let's see if we can optimize your approach for even better results. ")
            
            return {
                "message": "".join(response_parts),
                "context_used": ["progress_analysis", "trend_analysis", "nlp_analysis"],
                "progress_data": progress_data,
                "requires_followup": True,
                "followup_questions": [
                    "Would you like specific recommendations based on your progress?",
                    "Should we adjust your current management strategies?",
                    "Do you want to focus on any particular area for improvement?",
                    "Are there new symptoms or concerns you'd like to discuss?"
                ],
                "quick_actions": [
                    {"text": "Get Recommendations", "action": "progress_recommendations"},
                    {"text": "Adjust Plan", "action": "plan_adjustment"},
                    {"text": "View Trends", "action": "detailed_trends"},
                    {"text": "Set Goals", "action": "goal_setting"}
                ]
            }
            
        except Exception as e:
            print(f"Progress inquiry error: {e}")
            return {
                "message": "I'm having trouble accessing your progress data right now. In the meantime, how have you been feeling lately? Any changes in your symptoms or overall wellness?",
                "context_used": ["progress_error"],
                "requires_followup": True,
                "followup_questions": [
                    "How have your symptoms been this week?",
                    "Have you noticed any improvements?",
                    "Are there any new concerns?"
                ]
            }
    
    async def _handle_assessment_request(self, user: User, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle requests for IBS severity assessment."""
        
        try:
            assessment = await self.ibs_detection.assess_ibs_severity(user)
            
            # Enhance with ML insights
            enhanced_assessment = self.ml_integration.enhance_severity_assessment(assessment, user)
            
            # Get flare-up prediction for additional context
            flareup_risk = self.ml_integration.predict_flareup_risk(user, days_ahead=7)
            
            response_parts = [
                f"Based on your recent data, your current IBS severity is: {enhanced_assessment.severity.value.upper()}",
                f"Assessment confidence: {enhanced_assessment.confidence_score:.0%}",
                f"Symptom score: {enhanced_assessment.symptoms_score:.1f}/10",
                f"Frequency score: {enhanced_assessment.frequency_score:.1f}/10",
                f"Impact score: {enhanced_assessment.impact_score:.1f}/10"
            ]
            
            # Add ML-enhanced insights
            if flareup_risk["risk_level"] != "low":
                response_parts.append(f"🔮 ML Prediction: {flareup_risk['risk_level']} risk of flare-up in next 7 days ({flareup_risk['risk_score']:.0%})")
            
            if enhanced_assessment.factors:
                factors_text = ", ".join(enhanced_assessment.factors)
                response_parts.append(f"Key factors: {factors_text}")
            
            response_parts.append("Would you like personalized recommendations based on this assessment?")
            
            return {
                "message": " ".join(response_parts),
                "ibs_assessment": assessment,
                "context_used": ["full_assessment"],
                "requires_followup": True,
                "followup_questions": [
                    "Would you like recommendations for this severity level?",
                    "Do you want to see your severity trend over time?",
                    "Any questions about this assessment?"
                ]
            }
            
        except Exception as e:
            return {
                "message": "I need more symptom and health data to provide an accurate assessment. Please make sure you're regularly logging your symptoms, food reactions, and medications.",
                "context_used": ["error_handling"],
                "requires_followup": True,
                "followup_questions": [
                    "Would you like guidance on what data to track?",
                    "Do you need help with logging symptoms?",
                    "Any other questions I can help with?"
                ]
            }
    
    async def _handle_general_question(self, user: User, message: str, context: ConversationContext, nlp_result) -> Dict[str, Any]:
        """Handle general questions with intelligent context-aware responses."""
        
        # Analyze the question type and entities
        question_keywords = nlp_result.message.lower()
        entities = [entity.value.lower() for entity in nlp_result.entities]
        
        # IBS-related knowledge base responses
        if any(keyword in question_keywords for keyword in ["what is ibs", "irritable bowel", "ibs symptoms"]):
            return {
                "message": "IBS (Irritable Bowel Syndrome) is a common digestive disorder that affects the large intestine. It's characterized by symptoms like abdominal pain, bloating, gas, and changes in bowel movements. While the exact cause isn't known, factors like stress, diet, and gut bacteria can trigger symptoms. The good news is that IBS can be effectively managed through dietary changes, stress management, and lifestyle modifications.",
                "context_used": ["knowledge_base", "nlp_analysis"],
                "requires_followup": True,
                "followup_questions": [
                    "Are you experiencing any of these symptoms?",
                    "Would you like to learn about management strategies?",
                    "Do you want to start tracking your symptoms?"
                ],
                "quick_actions": [
                    {"text": "Symptom Check", "action": "symptom_assessment"},
                    {"text": "Management Tips", "action": "management_strategies"},
                    {"text": "Diet Guide", "action": "diet_recommendations"}
                ]
            }
        
        elif any(keyword in question_keywords for keyword in ["diet", "food", "eat", "avoid"]):
            return {
                "message": "Diet plays a crucial role in managing IBS symptoms. The FODMAP diet is often recommended, which involves avoiding certain fermentable carbohydrates that can trigger symptoms. Common trigger foods include beans, certain fruits, dairy products, and artificial sweeteners. However, everyone's triggers are different, so it's important to identify your personal trigger foods through careful tracking.",
                "context_used": ["knowledge_base", "dietary_guidance"],
                "requires_followup": True,
                "followup_questions": [
                    "Would you like specific food recommendations?",
                    "Are you interested in learning about the FODMAP diet?",
                    "Do you want help identifying your trigger foods?"
                ],
                "quick_actions": [
                    {"text": "FODMAP Guide", "action": "fodmap_guide"},
                    {"text": "Safe Foods", "action": "safe_foods"},
                    {"text": "Food Diary", "action": "food_tracking"}
                ]
            }
        
        elif any(keyword in question_keywords for keyword in ["stress", "anxiety", "mental health"]):
            return {
                "message": "Stress and IBS are closely connected through the gut-brain axis. Stress can trigger IBS symptoms, and IBS symptoms can increase stress, creating a cycle. Managing stress through techniques like deep breathing, meditation, regular exercise, and adequate sleep can significantly help reduce IBS symptoms. Some people also benefit from counseling or stress management programs.",
                "context_used": ["knowledge_base", "stress_management"],
                "requires_followup": True,
                "followup_questions": [
                    "Are you experiencing stress-related symptoms?",
                    "Would you like stress management techniques?",
                    "Do you want to learn about relaxation exercises?"
                ],
                "quick_actions": [
                    {"text": "Stress Tips", "action": "stress_management"},
                    {"text": "Relaxation", "action": "relaxation_techniques"},
                    {"text": "Mindfulness", "action": "mindfulness_guide"}
                ]
            }
        
        elif any(keyword in question_keywords for keyword in ["exercise", "physical activity", "workout"]):
            return {
                "message": "Regular, moderate exercise can be very beneficial for IBS management. It helps reduce stress, improves digestion, and can help regulate bowel movements. Low-impact activities like walking, swimming, yoga, and cycling are often well-tolerated. However, intense exercise might trigger symptoms in some people, so it's important to find what works for you.",
                "context_used": ["knowledge_base", "exercise_guidance"],
                "requires_followup": True,
                "followup_questions": [
                    "What type of exercise do you currently do?",
                    "Would you like a personalized exercise plan?",
                    "Are you interested in yoga for IBS?"
                ],
                "quick_actions": [
                    {"text": "Exercise Plan", "action": "exercise_recommendations"},
                    {"text": "Yoga Guide", "action": "yoga_for_ibs"},
                    {"text": "Activity Tracker", "action": "activity_tracking"}
                ]
            }
        
        # If no specific knowledge base match, provide intelligent general response
        else:
            # Use sentiment to tailor response
            if nlp_result.sentiment.value == "negative":
                base_response = "I understand you're looking for help, and I'm here to support you. "
            elif nlp_result.sentiment.value == "positive":
                base_response = "I'm glad you're taking an active interest in your health! "
            else:
                base_response = "That's a great question! "
            
            # Add context-aware response
            if context.recent_symptoms:
                base_response += "Based on your recent symptom tracking, I can provide personalized guidance. "
            
            base_response += "While I specialize in IBS management and wellness support, I can help you with symptom tracking, dietary guidance, stress management, and creating personalized care plans. What specific aspect of your IBS management would you like to focus on?"
            
            return {
                "message": base_response,
                "context_used": ["nlp_analysis", "sentiment_analysis", "user_context"],
                "requires_followup": True,
                "followup_questions": [
                    "Would you like to discuss your symptoms?",
                    "Are you interested in dietary recommendations?",
                    "Do you need help with stress management?",
                    "Would you like to start symptom tracking?"
                ],
                "quick_actions": [
                    {"text": "Symptom Discussion", "action": "symptom_discussion"},
                    {"text": "Diet Help", "action": "diet_guidance"},
                    {"text": "Stress Support", "action": "stress_help"},
                    {"text": "Start Tracking", "action": "begin_tracking"}
                ]
            }
    
    def _get_welcome_message(self, user: User) -> str:
        """Generate personalized welcome message."""
        name = user.first_name or "there"
        return f"Hello {name}! I'm your IBS wellness assistant. I can help you understand your symptoms, identify triggers, and provide personalized recommendations. How can I help you today?"
    
    async def _add_user_message(self, session_id: str, user_id: str, content: str) -> ChatMessage:
        """Add user message to database."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            content=content,
            message_type=MessageType.USER.value,
            sent_at=datetime.utcnow()
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def _add_assistant_message(self, session_id: str, user_id: str, content: str, metadata: Dict = None) -> ChatMessage:
        """Add assistant message to database."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            content=content,
            message_type=MessageType.ASSISTANT.value,
            message_metadata=metadata or {},
            sent_at=datetime.utcnow()
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def _add_system_message(self, session_id: str, user_id: str, content: str) -> ChatMessage:
        """Add system message to database."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            content=content,
            message_type=MessageType.SYSTEM.value,
            sent_at=datetime.utcnow()
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def _get_recent_user_data(self, user_id: str, data_type: str, days: int) -> List[Dict[str, Any]]:
        """Get recent user data for context building."""
        # This would query the appropriate tables based on data_type
        # For now, return empty list - would be implemented based on actual models
        return []
    
    async def _get_previous_assessments(self, user_id: str) -> List[IBSAssessment]:
        """Get previous IBS assessments for the user."""
        # This would query stored assessments
        # For now, return empty list
        return []
    
    async def _get_user_preferences(self, user: User) -> Dict[str, Any]:
        """Get user preferences for personalization."""
        return {
            "dietary_restrictions": [],
            "preferred_communication_style": "detailed",
            "notification_preferences": {}
        }
    
    async def _get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user progress data for analysis."""
        try:
            # This would query various data sources to build progress overview
            # For now, return a mock structure that would be populated with real data
            return {
                "has_data": True,  # Would be False if insufficient data
                "symptom_trend": "improving",  # "improving", "stable", "worsening"
                "severity_changes": {
                    "previous": "moderate",
                    "current": "mild"
                },
                "identified_triggers": ["dairy", "stress", "spicy foods"],
                "successful_strategies": ["low-FODMAP diet", "regular exercise"],
                "data_points": 45,  # Number of logged entries
                "tracking_consistency": 0.85  # Percentage of days with data
            }
        except Exception as e:
            return {"has_data": False}
    
    async def _handle_follow_up(self, user: User, context: ConversationContext, nlp_result, follow_up_check: Dict) -> Dict[str, Any]:
        """Handle follow-up conversations based on previous interactions."""
        follow_up_type = follow_up_check["type"]
        previous_context = follow_up_check["context"]
        
        if follow_up_type == "symptom_check":
            return {
                "message": f"I wanted to follow up on the {previous_context['symptom']} you mentioned earlier. How are you feeling now? Has it improved, stayed the same, or gotten worse?",
                "context_used": ["previous_symptom_discussion"],
                "requires_followup": True,
                "followup_questions": [
                    "How would you rate the intensity now (1-10)?",
                    "Have you tried any of the suggestions I mentioned?",
                    "Are there any new symptoms?"
                ],
                "quick_actions": [
                    {"text": "Much better", "action": "symptom_improvement"},
                    {"text": "About the same", "action": "symptom_stable"},
                    {"text": "Worse", "action": "symptom_worsening"},
                    {"text": "New symptoms", "action": "new_symptom_report"}
                ]
            }
        
        elif follow_up_type == "recommendation_check":
            return {
                "message": f"How did the {previous_context['recommendation_type']} recommendation work out for you? I'd love to hear about your experience.",
                "context_used": ["previous_recommendation"],
                "requires_followup": True,
                "followup_questions": [
                    "Did you notice any improvements?",
                    "Were there any challenges following the recommendation?",
                    "Would you like to adjust the approach?"
                ],
                "quick_actions": [
                    {"text": "Worked great!", "action": "recommendation_success"},
                    {"text": "Some improvement", "action": "recommendation_partial"},
                    {"text": "Didn't help", "action": "recommendation_failed"},
                    {"text": "Couldn't try it", "action": "recommendation_not_tried"}
                ]
            }
        
        elif follow_up_type == "assessment_reminder":
            return {
                "message": "It's been a while since your last symptom assessment. Would you like to do a quick check-in to track your progress?",
                "context_used": ["assessment_history"],
                "requires_followup": True,
                "followup_questions": [
                    "How have your symptoms been overall?",
                    "Any significant changes since last time?"
                ],
                "quick_actions": [
                    {"text": "Start assessment", "action": "start_assessment"},
                    {"text": "Quick update", "action": "quick_symptom_update"},
                    {"text": "Not now", "action": "defer_assessment"}
                ]
            }
        
        else:
            # General follow-up
            return {
                "message": "I wanted to check in with you. How have things been going with your IBS management?",
                "context_used": ["general_conversation_flow"],
                "requires_followup": True,
                "followup_questions": [
                    "Any new developments?",
                    "How are you feeling overall?"
                ],
                "quick_actions": [
                    {"text": "Going well", "action": "positive_update"},
                    {"text": "Some challenges", "action": "challenge_discussion"},
                    {"text": "Need help", "action": "request_assistance"}
                ]
            }

    def _enhance_response_with_context(self, response_data: Dict[str, Any], contextual_insights: Dict) -> Dict[str, Any]:
        """Enhance response with contextual insights and personalization."""
        
        # Add personalized elements based on user patterns
        if contextual_insights.get("frequent_symptoms") and contextual_insights["frequent_symptoms"]:
            response_data["personalized_note"] = f"Based on your history, I notice you often experience {', '.join(contextual_insights['frequent_symptoms'][:2])}. "
        
        # Adjust tone based on engagement level
        engagement_level = contextual_insights.get("engagement_level", "medium")
        if engagement_level == "high":
            response_data["tone_adjustment"] = "enthusiastic"
        elif engagement_level == "low":
            response_data["tone_adjustment"] = "encouraging"
        else:
            response_data["tone_adjustment"] = "supportive"
        
        # Add contextual quick actions
        if contextual_insights.get("suggested_actions"):
            if "quick_actions" not in response_data:
                response_data["quick_actions"] = []
            response_data["quick_actions"].extend(contextual_insights["suggested_actions"])
        
        # Add progress indicators if available
        if contextual_insights.get("progress_indicators"):
            response_data["progress_context"] = contextual_insights["progress_indicators"]
        
        return response_data