"""MCP tool implementations for AI chatbot.

These tools are thin wrappers around existing CRUD functions.
Tools read user_id from agent context (not parameters) for security.
All tools return structured dicts (not raise exceptions).
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Task
from app.ai.agent import get_context


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
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


async def add_task(session: AsyncSession, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Add a new task for the authenticated user.

    Args:
        session: Database session
        title: Task title (1-200 characters, required)
        description: Task description (optional, max 1000 characters)

    Returns:
        Success: {"success": True, "task": {...}}
        Error: {"success": False, "error": "error message"}
    """
    user_id = get_context("user_id")

    if not user_id:
        return {"success": False, "error": "User not authenticated"}

    # Validation
    if not title or not title.strip():
        return {"success": False, "error": "Title cannot be empty"}

    title = title.strip()
    if len(title) > 200:
        return {"success": False, "error": "Title must be 1-200 characters"}

    if description and len(description) > 1000:
        return {"success": False, "error": "Description must be under 1000 characters"}

    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description.strip() if description else None,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
        }
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": "Failed to create task"}


async def list_tasks(session: AsyncSession, filter: str = "all") -> Dict[str, Any]:
    """Retrieve user's tasks, optionally filtered by completion status.

    Args:
        session: Database session
        filter: "all", "active", or "completed"

    Returns:
        Success: {"success": True, "tasks": [...], "count": N, "filter": "..."}
        Error: {"success": False, "error": "error message"}
    """
    user_id = get_context("user_id")

    if not user_id:
        return {"success": False, "error": "User not authenticated"}

    # Validate filter
    valid_filters = ["all", "active", "completed"]
    if filter not in valid_filters:
        return {"success": False, "error": f"Invalid filter. Must be one of: {', '.join(valid_filters)}"}

    try:
        query = select(Task).where(Task.user_id == user_id)

        if filter == "active":
            query = query.where(Task.completed == False)
        elif filter == "completed":
            query = query.where(Task.completed == True)

        query = query.order_by(Task.created_at.desc())

        result = await session.execute(query)
        tasks = result.scalars().all()

        return {
            "success": True,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat()
                }
                for t in tasks
            ],
            "count": len(tasks),
            "filter": filter
        }
    except Exception as e:
        return {"success": False, "error": "Failed to retrieve tasks"}


async def complete_task(session: AsyncSession, task_id: int) -> Dict[str, Any]:
    """Mark a task as complete.

    Args:
        session: Database session
        task_id: Task ID to mark as complete

    Returns:
        Success: {"success": True, "task": {...}}
        Error: {"success": False, "error": "error message"}
    """
    user_id = get_context("user_id")

    if not user_id:
        return {"success": False, "error": "User not authenticated"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        was_complete = task.completed
        task.completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        response = {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }

        if was_complete:
            response["message"] = "Task was already complete"

        return response
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": "Failed to complete task"}


async def delete_task(session: AsyncSession, task_id: int) -> Dict[str, Any]:
    """Delete a task permanently.

    Args:
        session: Database session
        task_id: Task ID to delete

    Returns:
        Success: {"success": True, "task_id": N, "title": "...", "message": "..."}
        Error: {"success": False, "error": "error message"}
    """
    user_id = get_context("user_id")

    if not user_id:
        return {"success": False, "error": "User not authenticated"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        title = task.title
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "task_id": task_id,
            "title": title,
            "message": "Task deleted successfully"
        }
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": "Failed to delete task"}


async def update_task(
    session: AsyncSession,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Update a task's title and/or description.

    Args:
        session: Database session
        task_id: Task ID to update
        title: New title (optional, 1-200 characters)
        description: New description (optional, max 1000 characters)

    Returns:
        Success: {"success": True, "task": {...}}
        Error: {"success": False, "error": "error message"}
    """
    user_id = get_context("user_id")

    if not user_id:
        return {"success": False, "error": "User not authenticated"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    if title is None and description is None:
        return {"success": False, "error": "Must provide at least one field to update (title or description)"}

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            return {"success": False, "error": "Title cannot be empty"}
        if len(title) > 200:
            return {"success": False, "error": "Title must be 1-200 characters"}

    # Validate description if provided
    if description is not None and len(description) > 1000:
        return {"success": False, "error": "Description must be under 1000 characters"}

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": "Failed to update task"}


# Tool executor function for the agent
async def execute_tool(session: AsyncSession, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP tool by name.

    Args:
        session: Database session
        tool_name: Name of the tool to execute
        args: Tool arguments

    Returns:
        Tool result dictionary
    """
    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task
    }

    tool_func = tool_map.get(tool_name)
    if not tool_func:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    return await tool_func(session, **args)
