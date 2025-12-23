"""Agent factory for creating AI chatbot instances.

Creates stateless agents per-request with user context injection.
"""
import json
import os
from typing import List, Dict, Any, Optional, Callable
from openai import AsyncOpenAI

from app.ai.instructions import SYSTEM_INSTRUCTIONS, AGENT_MODEL


# Global context storage for the current request
_request_context: Dict[str, Any] = {}


def set_context(key: str, value: Any) -> None:
    """Set a value in the request context.

    Args:
        key: Context key (e.g., 'user_id')
        value: Value to store
    """
    _request_context[key] = value


def get_context(key: str) -> Any:
    """Get a value from the request context.

    Args:
        key: Context key to retrieve

    Returns:
        The stored value or None if not found
    """
    return _request_context.get(key)


def clear_context() -> None:
    """Clear all request context (call after request completes)."""
    _request_context.clear()


def create_agent(user_id: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create an agent configuration for processing chat messages.

    This function sets up the agent context and returns configuration
    that can be used with OpenAI's chat completions API.

    Args:
        user_id: Authenticated user's ID (from JWT)
        tools: List of tool definitions for the agent

    Returns:
        Agent configuration dict with client, model, instructions, and tools
    """
    # Set user context for tools to access
    set_context("user_id", user_id)

    # Create async OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return {
        "client": client,
        "model": AGENT_MODEL,
        "instructions": SYSTEM_INSTRUCTIONS,
        "tools": tools,
        "user_id": user_id
    }


async def run_agent(
    agent_config: Dict[str, Any],
    user_message: str,
    conversation_history: List[Dict[str, str]],
    tool_executor: Callable
) -> Dict[str, Any]:
    """Run the agent with a user message and return the response.

    Args:
        agent_config: Configuration from create_agent()
        user_message: The user's input message
        conversation_history: List of previous messages [{role, content}, ...]
        tool_executor: Async function to execute tools

    Returns:
        Dict with 'reply' (str) and 'tool_calls' (list)
    """
    client = agent_config["client"]

    # Build messages array
    messages = [
        {"role": "system", "content": agent_config["instructions"]}
    ]

    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI with tools (async)
    response = await client.chat.completions.create(
        model=agent_config["model"],
        messages=messages,
        tools=agent_config["tools"] if agent_config["tools"] else None,
        tool_choice="auto" if agent_config["tools"] else None
    )

    assistant_message = response.choices[0].message
    tool_calls_made = []

    # Handle tool calls if any
    if assistant_message.tool_calls:
        # Process each tool call
        tool_messages = []
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            # Execute the tool
            args_dict = json.loads(tool_args)
            tool_result = await tool_executor(tool_name, args_dict)

            tool_calls_made.append({
                "tool": tool_name,
                "parameters": args_dict,
                "result": tool_result
            })

            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

        # Get final response after tool execution
        messages.append(assistant_message.model_dump())
        messages.extend(tool_messages)

        final_response = await client.chat.completions.create(
            model=agent_config["model"],
            messages=messages
        )

        reply = final_response.choices[0].message.content
    else:
        reply = assistant_message.content

    return {
        "reply": reply or "I processed your request.",
        "tool_calls": tool_calls_made
    }
