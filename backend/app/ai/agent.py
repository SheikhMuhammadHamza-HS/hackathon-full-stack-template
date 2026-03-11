"""Agent implementation using proper OpenAI Agents SDK.

Uses Agent, Runner, and @function_tool decorated tools following
the official OpenAI Agents SDK patterns from skills documentation.
"""
import json
import os
from typing import Dict, Any, List
from agents import Agent, Runner
from sqlmodel.ext.asyncio.session import AsyncSession

from app.ai.instructions import SYSTEM_INSTRUCTIONS, AGENT_MODEL, AGENT_NAME
from app.ai.tools import ALL_TOOLS, TodoContext


def create_todo_agent() -> Agent:
    """Create TodoBot agent with MCP tools using OpenAI Agents SDK.

    Returns:
        Configured Agent instance with tools and instructions
    """
    agent = Agent(
        name=AGENT_NAME,
        instructions=SYSTEM_INSTRUCTIONS,
        model=AGENT_MODEL,
        tools=ALL_TOOLS  # @function_tool decorated tools from agents_sdk.py
    )
    return agent


async def run_agent(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    session: AsyncSession,
    user_id: str
) -> Dict[str, Any]:
    """Run agent using OpenAI Agents SDK Runner.

    Args:
        user_message: User's input message
        conversation_history: Previous messages [{role, content}, ...]
        session: Database session for tool execution
        user_id: Authenticated user ID from JWT

    Returns:
        Dict with 'reply' (str) and 'tool_calls' (list)
    """
    # Create context for tools to access
    context = TodoContext(user_id=user_id, session=session)

    # Create agent
    agent = create_todo_agent()

    # The conversation_history already contains the latest user message (added in chat.py)
    # We should use the user_message as the primary input for the Runner,
    # and use the previous messages as context.
    
    # Run agent using OpenAI Agents SDK Runner
    # If history is provided, we pass it as the context/previous messages
    result = await Runner.run(agent, user_message, context=context)

    # Extract tool calls from result
    tool_calls = []

    # Check if result has messages with tool calls
    if hasattr(result, 'messages') and result.messages:
        for message in result.messages:
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tc in message.tool_calls:
                    # Extract tool call details
                    tool_name = tc.function.name if hasattr(tc, 'function') else getattr(tc, 'name', 'unknown')
                    tool_args = {}

                    if hasattr(tc, 'function') and hasattr(tc.function, 'arguments'):
                        try:
                            tool_args = json.loads(tc.function.arguments)
                        except:
                            tool_args = {}

                    # Tool result is embedded in the response
                    tool_calls.append({
                        "tool": tool_name,
                        "parameters": tool_args,
                        "result": {}  # Result already processed by Runner
                    })

    return {
        "reply": result.final_output or "I processed your request.",
        "tool_calls": tool_calls
    }
