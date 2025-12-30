"""Chat API endpoints for AI-powered task management assistant.

Implements: Spec requirement 002-ai-chatbot chat-endpoint.md
Phase V Enhancement: Uses Dapr State Store for conversation history (008-dapr-state-chatbot)

All endpoints enforce strict user isolation - conversations can only be accessed
by their owner. Authentication via JWT is required for all operations.
Rate limited to 20 requests per minute per user.

State Management:
- Primary: Dapr State Store (chat:{user_id}:{conversation_id})
- Fallback: Degraded mode (chat continues without history persistence)
"""
import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth import verify_jwt
from app.database import get_session
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ToolCallInfo
# Use proper OpenAI Agents SDK (Agent, Runner, @function_tool)
from app.ai.agent import run_agent
# Phase V: Dapr State Store integration
from app.services.state_store import (
    DaprStateStore,
    get_state_store,
    create_empty_conversation_state,
    add_message_to_state,
    get_recent_messages
)

# Configure logging
logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key - use user_id from state if available."""
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    return get_remote_address(request)


# Create limiter - will be linked to app state
limiter = Limiter(key_func=get_rate_limit_key)

router = APIRouter()


async def _validate_user_access(user_id: str, authenticated_user: str) -> None:
    """
    Validate that the URL user_id matches the authenticated user from JWT.

    Args:
        user_id: User ID from URL path parameter
        authenticated_user: User ID extracted from JWT token

    Raises:
        HTTPException 403: If user_id does not match authenticated_user
    """
    if user_id != authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )


async def _get_or_create_conversation(
    conversation_id: Optional[int],
    authenticated_user: str,
    session: AsyncSession
) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        conversation_id: Existing conversation ID (or None to create new)
        authenticated_user: User ID from JWT token
        session: Database session

    Returns:
        Conversation: The existing or newly created conversation

    Raises:
        HTTPException 400: If conversation_id provided but not found or doesn't belong to user
    """
    if conversation_id is not None:
        # Fetch existing conversation and verify ownership
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == authenticated_user
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conversation {conversation_id} not found"
            )

        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=authenticated_user,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        await session.flush()  # Get the ID without committing
        return conversation


async def _save_message(
    conversation_id: int,
    user_id: str,
    role: str,
    content: str,
    tool_calls: Optional[List[ToolCallInfo]],
    session: AsyncSession
) -> Message:
    """
    Save a message to the database.

    Args:
        conversation_id: ID of the conversation
        user_id: User ID (from JWT)
        role: Message role ('user' or 'assistant')
        content: Message text content
        tool_calls: List of tool call info (for assistant messages)
        session: Database session

    Returns:
        Message: The saved message
    """
    # Serialize tool_calls to JSON string if present
    tool_calls_json = None
    if tool_calls:
        tool_calls_json = json.dumps([tc.model_dump() for tc in tool_calls])

    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls_json,
        created_at=datetime.utcnow()
    )
    session.add(message)
    return message


async def _fetch_conversation_history(
    conversation_id: int,
    user_id: str,
    session: AsyncSession,
    limit: int = 50
) -> List[Message]:
    """
    Fetch recent messages from a conversation for context.
    LEGACY: Used for backward compatibility with database storage.

    Args:
        conversation_id: ID of the conversation
        user_id: User ID (for security filtering)
        session: Database session
        limit: Maximum number of messages to fetch (default 50)

    Returns:
        List[Message]: Messages in chronological order
    """
    result = await session.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ============================================================================
# Phase V: Dapr State Store Functions (008-dapr-state-chatbot)
# ============================================================================

async def _get_or_create_dapr_conversation(
    conversation_id: Optional[str],
    user_id: str,
    state_store: DaprStateStore
) -> tuple[str, Dict[str, Any], bool]:
    """
    Get existing conversation state from Dapr or create a new one.

    Args:
        conversation_id: Existing conversation ID (or None to create new)
        user_id: User ID from JWT token
        state_store: DaprStateStore instance

    Returns:
        Tuple of (conversation_id, state_dict, is_new)
    """
    if conversation_id:
        # Validate state key format and ownership
        state_key = DaprStateStore.generate_state_key(user_id, conversation_id)
        if not DaprStateStore.validate_state_key(state_key, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - invalid conversation key"
            )

        # Try to get existing state
        state = await state_store.get_state(state_key)
        if state:
            return conversation_id, state, False
        else:
            # State not found - create new with provided ID
            state = create_empty_conversation_state(user_id, conversation_id)
            return conversation_id, state, True
    else:
        # Generate new conversation ID
        new_conv_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        state = create_empty_conversation_state(user_id, new_conv_id)
        return new_conv_id, state, True


async def _save_dapr_state(
    user_id: str,
    conversation_id: str,
    state: Dict[str, Any],
    state_store: DaprStateStore
) -> bool:
    """
    Save conversation state to Dapr State Store.

    Args:
        user_id: User ID for state key
        conversation_id: Conversation ID for state key
        state: Conversation state to save
        state_store: DaprStateStore instance

    Returns:
        True if save successful
    """
    state_key = DaprStateStore.generate_state_key(user_id, conversation_id)
    return await state_store.save_state(state_key, state)


def _state_messages_to_history(state: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Convert state messages to agent history format.

    Args:
        state: Conversation state with messages

    Returns:
        List of {role, content} dicts for agent
    """
    messages = get_recent_messages(state)
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
    ]


async def _process_with_agent_v2(
    message: str,
    user_id: str,
    conversation_history: List[Dict[str, str]],
    session: AsyncSession
) -> tuple[str, List[ToolCallInfo]]:
    """
    Process message with AI agent using dict-based history (Phase V).

    Args:
        message: User's input message
        user_id: Authenticated user's ID (for context)
        conversation_history: Previous messages as [{role, content}, ...]
        session: Database session for tool execution

    Returns:
        tuple: (reply text, list of tool calls)
    """
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not configured - returning fallback response")
        return (
            "I'm currently unable to process your request because the AI service is not configured. "
            "Please ask the administrator to set up the OPENAI_API_KEY.",
            []
        )

    try:
        # Run agent using proper OpenAI Agents SDK
        result = await run_agent(
            user_message=message,
            conversation_history=conversation_history,
            session=session,
            user_id=user_id
        )

        # Convert tool calls to ToolCallInfo objects
        tool_calls = [
            ToolCallInfo(
                tool=tc["tool"],
                parameters=tc["parameters"],
                result=tc["result"]
            )
            for tc in result.get("tool_calls", [])
        ]

        return result["reply"], tool_calls

    except Exception as e:
        import traceback
        logger.error(f"Agent processing error for user {user_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return (
            "I'm sorry, I encountered an error processing your request. "
            "Please try again, or use the task buttons in the dashboard.",
            []
        )


async def _process_with_agent(
    message: str,
    user_id: str,
    conversation_history: List[Message],
    session: AsyncSession
) -> tuple[str, List[ToolCallInfo]]:
    """
    Process message with AI agent using OpenAI API.

    Args:
        message: User's input message
        user_id: Authenticated user's ID (for context)
        conversation_history: Previous messages for context
        session: Database session for tool execution

    Returns:
        tuple: (reply text, list of tool calls)
    """
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not configured - returning fallback response")
        return (
            "I'm currently unable to process your request because the AI service is not configured. "
            "Please ask the administrator to set up the OPENAI_API_KEY.",
            []
        )

    try:
        # Convert conversation history to simple format
        history_for_agent = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]

        # Run agent using proper OpenAI Agents SDK (Agent, Runner, @function_tool)
        result = await run_agent(
            user_message=message,
            conversation_history=history_for_agent,
            session=session,
            user_id=user_id
        )

        # Convert tool calls to ToolCallInfo objects
        tool_calls = [
            ToolCallInfo(
                tool=tc["tool"],
                parameters=tc["parameters"],
                result=tc["result"]
            )
            for tc in result.get("tool_calls", [])
        ]

        return result["reply"], tool_calls

    except Exception as e:
        import traceback
        logger.error(f"Agent processing error for user {user_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"[AGENT ERROR] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return (
            "I'm sorry, I encountered an error processing your request. "
            "Please try again, or use the task buttons in the dashboard.",
            []
        )


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    user_id: str,
    chat_request: ChatRequest,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Process a chat message from the user.

    Implements: POST /api/{user_id}/chat from chat-endpoint.md spec
    Phase V Enhancement: Uses Dapr State Store for conversation history

    Processing Flow (Phase V - Dapr State Store):
    1. Validate JWT and user_id match
    2. Get or create conversation state from Dapr
    3. Add user message to state
    4. Process with AI agent using state history
    5. Add assistant response to state
    6. Save updated state to Dapr
    7. Return response (with degraded mode warning if applicable)

    Fallback (Degraded Mode):
    - If Dapr unavailable, chat continues without history persistence
    - Warning is logged but not exposed to user in response

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - State key includes user_id for isolation
    - Rate limited to 20 requests/minute per user

    Args:
        request: FastAPI request object (for rate limiting)
        user_id: User ID from URL path
        chat_request: Chat request with message and optional conversation_id
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        ChatResponse: AI assistant's response with conversation metadata

    Raises:
        HTTPException 400: Invalid input or conversation not found
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 429: Rate limit exceeded
        HTTPException 500: Server or AI processing error
    """
    # Set user_id on request state for rate limiter key function
    request.state.user_id = authenticated_user

    # Step 1: Validate user_id matches JWT
    await _validate_user_access(user_id, authenticated_user)

    # Get Dapr State Store instance
    state_store = get_state_store()
    
    # ------------------------------------------------------------------------
    # Dual-Write Strategy: SQL (Primary) + Dapr (Secondary/Cache)
    # We prioritize SQL to ensure persistence in environments without Dapr
    # ------------------------------------------------------------------------

    try:
        # Step 2: Handle Conversation ID (SQL Primary)
        conversation_id_int = chat_request.conversation_id
        
        # Get or create conversation in SQL Database
        conversation = await _get_or_create_conversation(
            conversation_id_int,
            authenticated_user,
            session
        )
        conversation_id_int = conversation.id
        conv_id_str = str(conversation_id_int)
        
        # Try to get Dapr state (Secondary)
        # We don't fail if this fails, just proceed with empty state if needed
        try:
            _, state, _ = await _get_or_create_dapr_conversation(
                conv_id_str, authenticated_user, state_store
            )
        except Exception as e:
            logger.warning(f"Dapr state retrieval failed: {e}")
            # Fallback to creating a fresh state object based on SQL ID
            state = create_empty_conversation_state(authenticated_user, conv_id_str)

        # Step 3: Save User Message (SQL + Dapr)
        # SQL Save
        await _save_message(
            conversation_id=conversation_id_int,
            user_id=authenticated_user,
            role="user",
            content=chat_request.message,
            tool_calls=None,
            session=session
        )
        
        # Dapr State update
        state = add_message_to_state(state, "user", chat_request.message)

        # Step 4: Get history for Agent
        # We use state history if available (context window management), 
        # otherwise we could fetch from SQL if Dapr state was empty/failed
        history_for_agent = _state_messages_to_history(state)
        
        # If Dapr state was empty (e.g. Dapr down), history might be empty
        # In a robust system, we would fetch recent SQL messages here to repopulate context
        # For now, we proceed.

        # Step 5: Process with AI agent
        reply, tool_calls = await _process_with_agent_v2(
            message=chat_request.message,
            user_id=authenticated_user,
            conversation_history=history_for_agent,
            session=session
        )

        # Step 6: Save Assistant Response (SQL + Dapr)
        # SQL Save
        await _save_message(
            conversation_id=conversation_id_int,
            user_id=authenticated_user,
            role="assistant",
            content=reply,
            tool_calls=tool_calls,
            session=session
        )
        
        # Commit SQL changes
        await session.commit()

        # Dapr State update
        tool_calls_dict = [
            {"tool": tc.tool, "parameters": tc.parameters, "result": tc.result}
            for tc in tool_calls
        ] if tool_calls else None
        state = add_message_to_state(state, "assistant", reply, tool_calls_dict)

        # Step 7: Save updated state to Dapr (fire-and-forget / best effort)
        try:
            await _save_dapr_state(
                authenticated_user,
                conv_id_str,
                state,
                state_store
            )
        except Exception as e:
            logger.warning(f"Failed to save state to Dapr: {e}")
            # We don't care deeply because SQL is our source of truth now

        # Step 8: Build and return response
        timestamp = datetime.utcnow()

        return ChatResponse(
            reply=reply,
            conversation_id=conversation_id_int,
            tool_calls=tool_calls,
            timestamp=timestamp
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error processing chat: {e}")
        logger.error(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message."
        )


@router.get("/{user_id}/conversations", response_model=List[dict])
async def list_conversations(
    user_id: str,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    List all conversations for the authenticated user.

    Args:
        user_id: User ID from URL path
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        List of conversation metadata (id, created_at, updated_at)

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT
    await _validate_user_access(user_id, authenticated_user)

    try:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == authenticated_user)
            .order_by(Conversation.updated_at.desc())
            .limit(20)
        )
        conversations = result.scalars().all()

        return [
            {
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]

    except Exception as e:
        logger.error(f"Error listing conversations for user {authenticated_user}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Get messages for a specific conversation.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID to fetch messages for
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        List of messages with role, content, tool_calls, and timestamp

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Conversation not found
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Verify conversation exists and belongs to user
        conv_result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == authenticated_user
            )
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Fetch messages
        messages = await _fetch_conversation_history(
            conversation_id=conversation_id,
            user_id=authenticated_user,
            session=session
        )

        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching messages for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: int,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a conversation and all its messages.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID to delete
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Conversation not found
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Verify conversation exists and belongs to user
        conv_result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == authenticated_user
            )
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete all messages in the conversation first
        await session.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        from sqlalchemy import delete
        await session.execute(
            delete(Message).where(Message.conversation_id == conversation_id)
        )

        # Delete the conversation
        await session.delete(conversation)
        await session.commit()

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )
