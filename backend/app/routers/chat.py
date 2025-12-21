"""Chat API endpoints for AI-powered task management assistant.

Implements: Spec requirement 002-ai-chatbot chat-endpoint.md
All endpoints enforce strict user isolation - conversations can only be accessed
by their owner. Authentication via JWT is required for all operations.
Rate limited to 20 requests per minute per user.
"""
import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth import verify_jwt
from app.database import get_session
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ToolCallInfo
from app.ai.agent import create_agent, run_agent, set_context, clear_context
from app.ai.mcp_server import get_mcp_tools, execute_mcp_tool

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
        # Get MCP tools (Model Context Protocol) - already in OpenAI format
        mcp_tools = get_mcp_tools()

        # Create agent with user context and MCP tools
        agent_config = create_agent(user_id=user_id, tools=mcp_tools)

        # Convert conversation history to the format expected by the agent
        history_for_agent = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]

        # Create MCP tool executor that uses the current session
        async def tool_executor(tool_name: str, args: dict) -> dict:
            return await execute_mcp_tool(tool_name, args, session)

        # Run the agent
        result = await run_agent(
            agent_config=agent_config,
            user_message=message,
            conversation_history=history_for_agent,
            tool_executor=tool_executor
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
        # Clear context on error
        clear_context()
        return (
            "I'm sorry, I encountered an error processing your request. "
            "Please try again, or use the task buttons in the dashboard.",
            []
        )
    finally:
        # Always clear context after request
        clear_context()


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

    Processing Flow:
    1. Validate JWT and user_id match
    2. Check rate limit (20/minute per user)
    3. Get or create conversation
    4. Save user message to database
    5. Fetch conversation history for context
    6. Process with AI agent
    7. Save assistant response to database
    8. Update conversation timestamp
    9. Return response

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - All database queries filtered by authenticated_user
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

    try:
        # Step 2: Get or create conversation
        conversation = await _get_or_create_conversation(
            chat_request.conversation_id,
            authenticated_user,
            session
        )

        # Step 3: Save user message
        await _save_message(
            conversation_id=conversation.id,
            user_id=authenticated_user,
            role="user",
            content=chat_request.message,
            tool_calls=None,
            session=session
        )

        # Step 4: Fetch conversation history for context
        history = await _fetch_conversation_history(
            conversation_id=conversation.id,
            user_id=authenticated_user,
            session=session
        )

        # Step 5: Process with AI agent
        reply, tool_calls = await _process_with_agent(
            message=chat_request.message,
            user_id=authenticated_user,
            conversation_history=history,
            session=session
        )

        # Step 6: Save assistant response
        await _save_message(
            conversation_id=conversation.id,
            user_id=authenticated_user,
            role="assistant",
            content=reply,
            tool_calls=tool_calls if tool_calls else None,
            session=session
        )

        # Step 7: Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        # Step 8: Commit transaction (handled by get_session dependency)
        await session.flush()

        # Step 9: Build and return response
        timestamp = datetime.utcnow()
        return ChatResponse(
            reply=reply,
            conversation_id=conversation.id,
            tool_calls=tool_calls,
            timestamp=timestamp
        )

    except HTTPException:
        # Re-raise HTTP exceptions (400, 403, 404)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        logger.error(f"Error processing chat for user {authenticated_user}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message. Please try again."
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
