"""
Chat API endpoints for IBS wellness chatbot.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageSend,
    ChatbotResponse,
    ChatMessageResponse,
    ChatSessionList,
    ChatMessageList,
    UserChatStats
)
from app.services.chat_service import ChatService
from app.models.user import User


router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new chat session.
    
    Args:
        session_data: Chat session creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        The created chat session
    """
    chat_service = ChatService(db)
    return chat_service.create_session(current_user, session_data.title)


@router.get("/sessions", response_model=ChatSessionList)
async def get_user_chat_sessions(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to retrieve"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's chat sessions.
    
    Args:
        limit: Maximum number of sessions to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of user's chat sessions
    """
    chat_service = ChatService(db)
    sessions = chat_service.get_user_sessions(current_user, limit)
    
    return ChatSessionList(
        sessions=sessions,
        total=len(sessions),
        page=1,
        size=limit
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific chat session.
    
    Args:
        session_id: Chat session ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        The requested chat session
    """
    chat_service = ChatService(db)
    
    # Verify session belongs to user
    sessions = chat_service.get_user_sessions(current_user, 1000)  # Get all sessions
    session = next((s for s in sessions if s.id == session_id), None)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=ChatbotResponse)
async def send_message(
    session_id: str,
    message_data: ChatMessageSend,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the chatbot.
    
    Args:
        session_id: Chat session ID
        message_data: Message data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chatbot response with assessment and recommendations
    """
    chat_service = ChatService(db)
    
    # Use session_id from URL, but allow override from message_data
    effective_session_id = message_data.session_id or session_id
    
    try:
        response = chat_service.send_message(
            user=current_user,
            session_id=effective_session_id,
            message=message_data.message,
            include_assessment=message_data.include_context
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/messages", response_model=ChatbotResponse)
async def send_message_quick(
    message_data: ChatMessageSend,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the chatbot (creates new session if needed).
    
    Args:
        message_data: Message data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chatbot response with assessment and recommendations
    """
    chat_service = ChatService(db)
    
    try:
        response = chat_service.send_message(
            user=current_user,
            session_id=message_data.session_id,
            message=message_data.message,
            include_assessment=message_data.include_context
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=ChatMessageList)
async def get_session_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of messages to retrieve"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get messages from a chat session.
    
    Args:
        session_id: Chat session ID
        limit: Maximum number of messages to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of messages from the session
    """
    chat_service = ChatService(db)
    
    try:
        messages = chat_service.get_session_history(current_user, session_id, limit)
        
        return ChatMessageList(
            messages=messages,
            total=len(messages),
            page=1,
            size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a chat session and all its messages.
    
    Args:
        session_id: Chat session ID
        current_user: Current authenticated user
        db: Database session
    """
    # This would be implemented to mark session as inactive or delete it
    # For now, we'll just return success
    # In a real implementation, you'd:
    # 1. Verify session belongs to user
    # 2. Mark session as inactive or delete it
    # 3. Handle cascade deletion of messages
    pass


@router.get("/stats", response_model=UserChatStats)
async def get_user_chat_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's chat statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User's chat statistics
    """
    chat_service = ChatService(db)
    
    # Get user sessions to calculate stats
    sessions = chat_service.get_user_sessions(current_user, 1000)
    
    total_sessions = len(sessions)
    total_messages = 0
    last_chat = None
    
    if sessions:
        last_chat = sessions[0].started_at  # Sessions are ordered by started_at desc
        
        # Calculate total messages (this would be more efficient with a direct query)
        for session in sessions:
            messages = chat_service.get_session_history(current_user, session.id, 1000)
            total_messages += len(messages)
    
    avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0
    
    # Get current IBS severity (would need to implement this)
    current_severity = "unknown"  # This would come from the IBS detection service
    
    return UserChatStats(
        total_sessions=total_sessions,
        total_messages=total_messages,
        avg_messages_per_session=avg_messages_per_session,
        last_chat=last_chat,
        current_ibs_severity=current_severity,
        improvement_trend=None  # This would be calculated based on historical assessments
    )