"""MCP tool implementations using OpenAI Agents SDK.

These tools use the proper @function_tool decorator and RunContextWrapper
for accessing user_id and database session from agent context.
"""
import json
from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from agents import function_tool, RunContextWrapper
from dataclasses import dataclass

from app.models import Task


# Context dataclass for passing user_id and db session to tools
@dataclass
class TodoContext:
    """Context passed to all MCP tools containing user_id and database session."""
    user_id: str
    session: AsyncSession


@function_tool
async def add_task(
    ctx: RunContextWrapper[TodoContext],
    title: str,
    description: Optional[str] = None
) -> str:
    """Add a new task for the user.

    Args:
        title: Task title (1-200 characters, required)
        description: Optional task description (max 1000 characters)

    Returns:
        JSON string with success/error status and task details
    """
    user_id = ctx.context.user_id
    session = ctx.context.session

    # Validation
    if not title or not title.strip():
        return json.dumps({"success": False, "error": "Title cannot be empty"})

    title = title.strip()
    if len(title) > 200:
        return json.dumps({"success": False, "error": "Title must be 1-200 characters"})

    if description and len(description) > 1000:
        return json.dumps({"success": False, "error": "Description must be under 1000 characters"})

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

        result = {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
        }
        return json.dumps(result)
    except Exception as e:
        await session.rollback()
        return json.dumps({"success": False, "error": "Failed to create task"})


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[TodoContext],
    filter: str = "all"
) -> str:
    """List all tasks for the user.

    Args:
        filter: Filter by status - 'all', 'active', or 'completed'

    Returns:
        JSON string with task list or error
    """
    user_id = ctx.context.user_id
    session = ctx.context.session

    # Validate filter
    valid_filters = ["all", "active", "completed"]
    if filter not in valid_filters:
        return json.dumps({
            "success": False,
            "error": f"Invalid filter. Must be one of: {', '.join(valid_filters)}"
        })

    try:
        query = select(Task).where(Task.user_id == user_id)

        if filter == "active":
            query = query.where(Task.completed == False)
        elif filter == "completed":
            query = query.where(Task.completed == True)

        query = query.order_by(Task.created_at.desc())

        result = await session.execute(query)
        tasks = result.scalars().all()

        response = {
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
        return json.dumps(response)
    except Exception as e:
        return json.dumps({"success": False, "error": "Failed to retrieve tasks"})


@function_tool
async def complete_task(
    ctx: RunContextWrapper[TodoContext],
    task_id: int
) -> str:
    """Mark a task as complete.

    Args:
        task_id: ID of the task to complete

    Returns:
        JSON string with success/error status
    """
    user_id = ctx.context.user_id
    session = ctx.context.session

    if not isinstance(task_id, int) or task_id <= 0:
        return json.dumps({"success": False, "error": "Invalid task ID"})

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({"success": False, "error": f"Task {task_id} not found"})

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

        return json.dumps(response)
    except Exception as e:
        await session.rollback()
        return json.dumps({"success": False, "error": "Failed to complete task"})


@function_tool
async def delete_task(
    ctx: RunContextWrapper[TodoContext],
    task_id: int
) -> str:
    """Delete a task permanently.

    Args:
        task_id: ID of the task to delete

    Returns:
        JSON string with success/error status
    """
    user_id = ctx.context.user_id
    session = ctx.context.session

    if not isinstance(task_id, int) or task_id <= 0:
        return json.dumps({"success": False, "error": "Invalid task ID"})

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({"success": False, "error": f"Task {task_id} not found"})

        title = task.title
        await session.delete(task)
        await session.commit()

        response = {
            "success": True,
            "task_id": task_id,
            "title": title,
            "message": "Task deleted successfully"
        }
        return json.dumps(response)
    except Exception as e:
        await session.rollback()
        return json.dumps({"success": False, "error": "Failed to delete task"})


@function_tool
async def update_task(
    ctx: RunContextWrapper[TodoContext],
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Update a task's title or description.

    Args:
        task_id: ID of the task to update
        title: New title (optional, 1-200 characters)
        description: New description (optional, max 1000 characters)

    Returns:
        JSON string with success/error status
    """
    user_id = ctx.context.user_id
    session = ctx.context.session

    if not isinstance(task_id, int) or task_id <= 0:
        return json.dumps({"success": False, "error": "Invalid task ID"})

    if title is None and description is None:
        return json.dumps({
            "success": False,
            "error": "Must provide at least one field to update (title or description)"
        })

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            return json.dumps({"success": False, "error": "Title cannot be empty"})
        if len(title) > 200:
            return json.dumps({"success": False, "error": "Title must be 1-200 characters"})

    # Validate description if provided
    if description is not None and len(description) > 1000:
        return json.dumps({"success": False, "error": "Description must be under 1000 characters"})

    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({"success": False, "error": f"Task {task_id} not found"})

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        response = {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
        return json.dumps(response)
    except Exception as e:
        await session.rollback()
        return json.dumps({"success": False, "error": "Failed to update task"})


# Export all tools
ALL_TOOLS = [add_task, list_tasks, complete_task, delete_task, update_task]
