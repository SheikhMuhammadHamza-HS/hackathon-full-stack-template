"""MCP Server for Todo Task Management Tools.

Implements Model Context Protocol (MCP) server with 5 tools:
- add_task: Create new tasks
- list_tasks: Retrieve user's tasks
- complete_task: Mark tasks as complete
- delete_task: Remove tasks
- update_task: Modify task details

All tools enforce user isolation by reading user_id from context.
"""
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel.ext.asyncio.session import AsyncSession

from app.ai.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)

# Create MCP server
mcp_server = Server("todo-tasks-server")


@mcp_server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available MCP tools for task management.

    Returns:
        List of Tool objects with schemas for OpenAI function calling
    """
    return [
        Tool(
            name="add_task",
            description="Add a new task for the user. Use this when the user wants to create, add, or remember a new task or todo item.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the task (max 1000 characters)"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for the user. Use this when the user wants to see, view, or check their tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "enum": ["all", "active", "completed"],
                        "description": "Filter tasks by status. 'all' shows everything, 'active' shows incomplete tasks, 'completed' shows done tasks."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as complete. Use this when the user says they finished, completed, or are done with a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task permanently. Use this when the user wants to remove, delete, or get rid of a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's title or description. Use this when the user wants to change, modify, or edit a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (max 1000 characters)"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any],
    session: AsyncSession
) -> List[TextContent]:
    """Execute MCP tool by name.

    Args:
        name: Tool name (add_task, list_tasks, etc.)
        arguments: Tool parameters
        session: Database session for tool execution

    Returns:
        List of TextContent with tool execution result

    Raises:
        ValueError: If tool name is unknown
    """
    import json

    # Map tool names to functions
    tool_functions = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task
    }

    if name not in tool_functions:
        raise ValueError(f"Unknown tool: {name}")

    # Execute tool
    tool_func = tool_functions[name]
    result = await tool_func(session, **arguments)

    # Return result as TextContent
    return [
        TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
    ]


def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get MCP tools in OpenAI function calling format.

    Returns:
        List of tool definitions compatible with OpenAI API
    """
    # Define tools directly without async complications
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task for the user. Use this when the user wants to create, add, or remember a new task or todo item.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the task (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description for the task (max 1000 characters)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user. Use this when the user wants to see, view, or check their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "enum": ["all", "active", "completed"],
                            "description": "Filter tasks by status. 'all' shows everything, 'active' shows incomplete tasks, 'completed' shows done tasks."
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete. Use this when the user says they finished, completed, or are done with a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently. Use this when the user wants to remove, delete, or get rid of a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title or description. Use this when the user wants to change, modify, or edit a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task (max 1000 characters)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]


async def execute_mcp_tool(
    name: str,
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """Execute MCP tool and return parsed result.

    Args:
        name: Tool name
        arguments: Tool parameters
        session: Database session

    Returns:
        Parsed tool result as dictionary
    """
    import json

    # Execute tool
    result = await handle_call_tool(name, arguments, session)

    # Parse JSON result from TextContent
    if result and len(result) > 0:
        return json.loads(result[0].text)

    return {"success": False, "error": "No result returned"}
