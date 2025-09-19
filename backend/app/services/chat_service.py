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
from app.core.logging import StructuredLogger


class ChatService:
    """Service for managing IBS chatbot conversations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ibs_detection = IBSDetectionService(db)
        self.recommendation_service = RecommendationService(db)
        self.ml_service = MLIntegrationService(db)
        
        # Conversation templates and responses
        self.greeting_messages = [
            "Hello! I'm your IBS wellness assistant. I'm here to help you understand your symptoms and provide personalized recommendations.",
            "Hi there! I can help you track your IBS patterns and suggest ways to manage your symptoms. How are you feeling today?",
            "Welcome! I'm here to support your IBS journey with personalized insights and recommendations. What would you like to discuss?"
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
            session_id=session.id,
            message_id=assistant_message.id,
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
        """Generate chatbot response based on message and context."""
        
        message_lower = message.lower()
        response_data = {
            "message": "",
            "metadata": {},
            "context_used": [],
            "confidence": 0.8,
            "requires_followup": False,
            "followup_questions": []
        }
        
        # Determine response type based on message content
        if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
            response_data.update(self._handle_greeting(user, context))
            
        elif any(word in message_lower for word in ["symptom", "pain", "bloat", "cramp", "diarrhea", "constipation"]):
            response_data.update(self._handle_symptom_discussion(user, message, context, include_assessment))
            
        elif any(word in message_lower for word in ["food", "eat", "diet", "trigger", "meal"]):
            response_data.update(self._handle_food_discussion(user, message, context))
            
        elif any(word in message_lower for word in ["medication", "medicine", "treatment", "drug"]):
            response_data.update(self._handle_medication_discussion(user, message, context))
            
        elif any(word in message_lower for word in ["recommend", "suggest", "help", "advice"]):
            response_data.update(self._handle_recommendation_request(user, context, include_assessment))
            
        elif any(word in message_lower for word in ["assess", "severity", "how bad", "rate"]):
            response_data.update(self._handle_assessment_request(user, context))
            
        else:
            response_data.update(self._handle_general_question(user, message, context))
        
        return response_data
    
    def _handle_greeting(self, user: User, context: ConversationContext) -> Dict[str, Any]:
        """Handle greeting messages."""
        import random
        
        greeting = random.choice(self.greeting_messages)
        
        # Personalize based on recent activity
        if context.recent_symptoms:
            greeting += f" I see you've been tracking your symptoms recently. How are you feeling today?"
        elif context.previous_assessments:
            last_assessment = context.previous_assessments[-1]
            greeting += f" Your last assessment showed {last_assessment.severity.value} IBS symptoms. Any changes since then?"
        else:
            greeting += " To get started, you can tell me about your current symptoms or ask for recommendations."
        
        return {
            "message": greeting,
            "context_used": ["user_history"],
            "requires_followup": True,
            "followup_questions": [
                "How are your IBS symptoms today?",
                "Would you like me to assess your current IBS severity?",
                "Are there any specific concerns you'd like to discuss?"
            ]
        }
    
    def _handle_symptom_discussion(self, user: User, message: str, context: ConversationContext, 
                                 include_assessment: bool) -> Dict[str, Any]:
        """Handle symptom-related discussions."""
        
        response_parts = []
        context_used = ["symptoms_data"]
        
        # Acknowledge the symptom discussion
        response_parts.append("I understand you're experiencing IBS symptoms. Let me help you understand what's happening.")
        
        # Provide context from recent symptoms if available
        if context.recent_symptoms:
            symptom_count = len(context.recent_symptoms)
            response_parts.append(f"I can see you've logged {symptom_count} symptom entries in the past month.")
            
            # Identify patterns
            if symptom_count >= 5:
                response_parts.append("Based on your recent logs, I can help identify patterns and triggers.")
        
        # Perform assessment if requested
        assessment = None
        recommendations = []
        
        if include_assessment:
            try:
                assessment = self.ibs_detection.assess_ibs_severity(user)
                context_used.append("ibs_assessment")
                
                response_parts.append(f"Based on your recent data, your current IBS severity appears to be {assessment.severity.value}.")
                
                if assessment.factors:
                    factors_text = ", ".join(assessment.factors[:3])
                    response_parts.append(f"Key contributing factors include: {factors_text}.")
                
                # Get recommendations
                recommendations = self.recommendation_service.generate_recommendations(user, assessment)
                if recommendations:
                    response_parts.append("I have some personalized recommendations that might help.")
                    
            except Exception as e:
                response_parts.append("I'm having trouble accessing your recent data for assessment. Please make sure you've been logging your symptoms regularly.")
        
        return {
            "message": " ".join(response_parts),
            "ibs_assessment": assessment,
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "context_used": context_used,
            "requires_followup": True,
            "followup_questions": [
                "Would you like specific recommendations for managing these symptoms?",
                "Have you noticed any particular triggers recently?",
                "How are these symptoms affecting your daily life?"
            ]
        }
    
    def _handle_food_discussion(self, user: User, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Handle food and diet-related discussions."""
        
        response_parts = []
        context_used = ["food_data"]
        
        response_parts.append("Diet plays a crucial role in managing IBS symptoms. Let me share some insights based on your data.")
        
        if context.recent_foods:
            reaction_count = len(context.recent_foods)
            response_parts.append(f"You've logged {reaction_count} food reactions recently.")
            
            # Identify potential triggers
            trigger_foods = self.recommendation_service._analyze_food_triggers(user.id)
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
    
    def _handle_medication_discussion(self, user: User, message: str, context: ConversationContext) -> Dict[str, Any]:
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
    
    def _handle_recommendation_request(self, user: User, context: ConversationContext, 
                                     include_assessment: bool) -> Dict[str, Any]:
        """Handle requests for recommendations."""
        
        response_parts = []
        recommendations = []
        assessment = None
        
        try:
            # Get current assessment
            assessment = self.ibs_detection.assess_ibs_severity(user)
            
            # Enhance assessment with ML insights
            enhanced_assessment = self.ml_service.enhance_severity_assessment(assessment, user)
            
            # Generate ML-enhanced recommendations
            recommendations = self.ml_service.generate_personalized_recommendations(user, enhanced_assessment)
            
            # Get flare-up risk prediction
            flareup_risk = self.ml_service.predict_flareup_risk(user, days_ahead=7)
            
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
    
    def _handle_assessment_request(self, user: User, context: ConversationContext) -> Dict[str, Any]:
        """Handle requests for IBS severity assessment."""
        
        try:
            assessment = self.ibs_detection.assess_ibs_severity(user)
            
            # Enhance with ML insights
            enhanced_assessment = self.ml_service.enhance_severity_assessment(assessment, user)
            
            # Get flare-up prediction for additional context
            flareup_risk = self.ml_service.predict_flareup_risk(user, days_ahead=7)
            
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
    
    def _handle_general_question(self, user: User, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Handle general questions and provide helpful responses."""
        
        response = "I'm here to help with your IBS management. I can assist with:\n\n"
        response += "• Assessing your IBS severity based on your logged data\n"
        response += "• Providing personalized diet and lifestyle recommendations\n"
        response += "• Identifying patterns in your symptoms and triggers\n"
        response += "• Tracking your progress over time\n\n"
        response += "What would you like to explore today?"
        
        return {
            "message": response,
            "context_used": ["general_help"],
            "requires_followup": True,
            "followup_questions": [
                "Would you like me to assess your current IBS severity?",
                "Are you interested in diet recommendations?",
                "Do you want to discuss your symptoms?"
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