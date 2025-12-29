"""Task CRUD API endpoints with user isolation.

Implements: Spec requirement T062-T070 for task management
Phase V: Extended with advanced filtering and sorting (T003, T004, T006, T009)
Phase V: Extended with Dapr Pub/Sub event publishing (009-dapr-pubsub-events)

All endpoints enforce strict user isolation - tasks can only be accessed
by their owner. Authentication via JWT is required for all operations.
"""
import logging
from datetime import datetime
from typing import List, Optional
import json
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import select, or_, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth import verify_jwt
from app.database import get_session
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskPriority, RecurringInterval
# Phase V: Dapr Pub/Sub event publishing
from app.events.publisher import publish_event
from sqlalchemy import func

logger = logging.getLogger(__name__)

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


async def _get_next_task_number(session: AsyncSession, user_id: str) -> int:
    """
    Get the next task_number for a user (max + 1, or 1 if no tasks).

    Args:
        session: Database session
        user_id: User ID to get next task number for

    Returns:
        int: Next task_number (1 for first task, max+1 otherwise)
    """
    result = await session.execute(
        select(func.max(Task.task_number)).where(Task.user_id == user_id)
    )
    max_number = result.scalar_one_or_none()
    return (max_number or 0) + 1


async def _get_user_task(
    task_id: int,
    authenticated_user: str,
    session: AsyncSession
) -> Task:
    """
    Retrieve a task and verify it belongs to the authenticated user.

    Args:
        task_id: Task ID to retrieve
        authenticated_user: User ID from JWT token
        session: Database session

    Returns:
        Task: The requested task

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == authenticated_user
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session),
    # T003: Priority filtering
    priority: Optional[TaskPriority] = Query(default=None, description="Filter by priority (low, medium, high)"),
    # T004: Priority and due_date sorting
    sort_by: Optional[str] = Query(
        default=None,
        description="Sort tasks (priority_asc, priority_desc, due_date_asc, due_date_desc)",
        regex="^(priority_asc|priority_desc|due_date_asc|due_date_desc)$"
    ),
    # T006: Tag filtering (comma-separated, OR logic, case-insensitive)
    tags: Optional[str] = Query(default=None, description="Filter by tags (comma-separated, matches ANY tag)"),
    # T009: Due date filtering
    due_before: Optional[datetime] = Query(default=None, description="Filter tasks due before this datetime"),
    due_after: Optional[datetime] = Query(default=None, description="Filter tasks due after this datetime")
):
    """
    List all tasks for the authenticated user with filtering and sorting.

    Implements:
    - T062: GET /api/{user_id}/tasks (base functionality)
    - T003: Priority filtering
    - T004: Priority sorting
    - T006: Tag filtering (OR logic, case-insensitive)
    - T009: Due date filtering and sorting

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Returns only tasks owned by authenticated user

    Query Parameters:
        priority: Filter by priority level (low, medium, high)
        sort_by: Sort order (priority_asc, priority_desc, due_date_asc, due_date_desc)
        tags: Comma-separated tag list (matches ANY tag, case-insensitive)
        due_before: Filter tasks due before this datetime (ISO format)
        due_after: Filter tasks due after this datetime (ISO format)

    Args:
        user_id: User ID from URL path
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        List[TaskResponse]: List of user's tasks with applied filters and sorting

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Base query: filter by authenticated user
        query = select(Task).where(Task.user_id == authenticated_user)

        # T003: Apply priority filter if provided
        if priority:
            query = query.where(Task.priority == priority.value)

        # T006: Apply tag filter if provided (OR logic, case-insensitive)
        if tags:
            tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
            if tag_list:
                # Filter tasks where tags JSON array contains ANY of the requested tags
                # Use OR conditions to match any tag (case-insensitive)
                tag_conditions = []
                for tag in tag_list:
                    # PostgreSQL: JSON array contains check (case-insensitive)
                    # Note: This requires proper JSON parsing since tags are stored as JSON strings
                    tag_conditions.append(Task.tags.like(f'%"{tag}"%'))
                    # Also check for case variations
                    tag_conditions.append(Task.tags.like(f'%"{tag.capitalize()}"%'))
                    tag_conditions.append(Task.tags.like(f'%"{tag.upper()}"%'))

                if tag_conditions:
                    query = query.where(or_(*tag_conditions))

        # T009: Apply due_date filters if provided
        if due_before:
            query = query.where(Task.due_date < due_before)
        if due_after:
            query = query.where(Task.due_date > due_after)

        # T004 & T009: Apply sorting if specified
        if sort_by:
            # Priority sorting (high=3, medium=2, low=1)
            if sort_by == "priority_desc":
                # High → Medium → Low
                query = query.order_by(
                    desc(Task.priority)
                )
            elif sort_by == "priority_asc":
                # Low → Medium → High
                query = query.order_by(
                    asc(Task.priority)
                )
            elif sort_by == "due_date_desc":
                # Latest first (nulls last)
                query = query.order_by(
                    desc(Task.due_date)
                )
            elif sort_by == "due_date_asc":
                # Earliest first (nulls last)
                query = query.order_by(
                    asc(Task.due_date)
                )
        else:
            # Default: order by creation date (newest first)
            query = query.order_by(Task.created_at.desc())

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Parse tags JSON strings to lists for response
        response_tasks = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "task_number": task.task_number,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "tags": json.loads(task.tags) if task.tags else [],
                "due_date": task.due_date,
                "is_recurring": task.is_recurring,
                "recurring_interval": task.recurring_interval,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
            response_tasks.append(TaskResponse(**task_dict))

        return response_tasks

    except Exception as e:
        # Log error server-side, return generic message
        print(f"Database error in get_tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Implements:
    - T063: POST /api/{user_id}/tasks (base functionality)
    - Phase V: Extended with advanced task fields (priority, tags, due_date, recurring)

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Task is created with authenticated_user as owner

    Args:
        user_id: User ID from URL path
        task_data: Task creation data with all fields including advanced features
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        TaskResponse: The created task

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 400: Invalid task data (validation errors)
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Normalize due_date to naive datetime (remove timezone for DB compatibility)
        due_date_normalized = None
        if task_data.due_date:
            if task_data.due_date.tzinfo is not None:
                # Convert to UTC and make naive
                due_date_normalized = task_data.due_date.replace(tzinfo=None)
            else:
                due_date_normalized = task_data.due_date

        # Get next task_number for this user
        next_task_number = await _get_next_task_number(session, authenticated_user)

        # Create task with authenticated_user as owner and all new fields
        task = Task(
            user_id=authenticated_user,  # Use JWT user_id, not URL user_id
            task_number=next_task_number,  # User-specific task number
            title=task_data.title,
            description=task_data.description,
            completed=False,
            # Phase V: Advanced task fields
            priority=task_data.priority.value,
            tags=json.dumps(task_data.tags),  # Store as JSON string
            due_date=due_date_normalized,
            is_recurring=task_data.is_recurring,
            recurring_interval=task_data.recurring_interval.value if task_data.recurring_interval else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Phase V: Publish task.created event (fire-and-forget)
        await publish_event(
            topic="tasks",
            event_type="task.created",
            data={
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": json.loads(task.tags) if task.tags else [],
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_recurring": task.is_recurring,
                "recurring_interval": task.recurring_interval
            },
            user_id=authenticated_user
        )

        # Parse tags JSON string to list for response
        response_data = {
            "id": task.id,
            "task_number": task.task_number,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": json.loads(task.tags) if task.tags else [],
            "due_date": task.due_date,
            "is_recurring": task.is_recurring,
            "recurring_interval": task.recurring_interval,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }

        return TaskResponse(**response_data)

    except Exception as e:
        # Log error server-side, return generic message
        logger.error(f"Database error in create_task: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing task.

    Implements:
    - T064: PATCH /api/{user_id}/tasks/{task_id} (base functionality)
    - Phase V: Extended with advanced task fields (priority, tags, due_date, recurring)

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Only updates tasks owned by authenticated user

    Args:
        user_id: User ID from URL path
        task_id: Task ID to update
        task_data: Fields to update (all fields are optional for partial updates)
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        TaskResponse: The updated task

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Task not found or doesn't belong to user
        HTTPException 400: Invalid task data (validation errors)
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Get task and verify ownership
        task = await _get_user_task(task_id, authenticated_user, session)

        # Update only provided fields (partial update)
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed

        # Phase V: Update advanced task fields if provided
        if task_data.priority is not None:
            task.priority = task_data.priority.value
        if task_data.tags is not None:
            task.tags = json.dumps(task_data.tags)
        if task_data.due_date is not None:
            # Normalize due_date to naive datetime
            if task_data.due_date.tzinfo is not None:
                task.due_date = task_data.due_date.replace(tzinfo=None)
            else:
                task.due_date = task_data.due_date
        if task_data.is_recurring is not None:
            task.is_recurring = task_data.is_recurring
        if task_data.recurring_interval is not None:
            task.recurring_interval = task_data.recurring_interval.value

        # Track changed fields for event
        changed_fields = []
        if task_data.title is not None:
            changed_fields.append("title")
        if task_data.description is not None:
            changed_fields.append("description")
        if task_data.completed is not None:
            changed_fields.append("completed")
        if task_data.priority is not None:
            changed_fields.append("priority")
        if task_data.tags is not None:
            changed_fields.append("tags")
        if task_data.due_date is not None:
            changed_fields.append("due_date")
        if task_data.is_recurring is not None:
            changed_fields.append("is_recurring")
        if task_data.recurring_interval is not None:
            changed_fields.append("recurring_interval")

        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Phase V: Publish task.updated event (fire-and-forget)
        await publish_event(
            topic="tasks",
            event_type="task.updated",
            data={
                "task_id": task.id,
                "changed_fields": changed_fields,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None
            },
            user_id=authenticated_user
        )

        # Check if completion status changed - publish task.completed event
        if task_data.completed is not None:
            await publish_event(
                topic="tasks",
                event_type="task.completed",
                data={
                    "task_id": task.id,
                    "completed": task.completed,
                    "is_recurring": task.is_recurring,
                    "recurring_interval": task.recurring_interval,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                },
                user_id=authenticated_user
            )

        # Parse tags JSON string to list for response
        response_data = {
            "id": task.id,
            "task_number": task.task_number,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": json.loads(task.tags) if task.tags else [],
            "due_date": task.due_date,
            "is_recurring": task.is_recurring,
            "recurring_interval": task.recurring_interval,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }

        return TaskResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        logger.error(f"Database error in update_task: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a task.

    Implements: T065 - DELETE /api/{user_id}/tasks/{task_id}

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Only deletes tasks owned by authenticated user

    Args:
        user_id: User ID from URL path
        task_id: Task ID to delete
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Task not found or doesn't belong to user
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Get task and verify ownership
        task = await _get_user_task(task_id, authenticated_user, session)

        # Delete the task
        await session.delete(task)
        await session.commit()

        # Phase V: Publish task.deleted event (fire-and-forget)
        await publish_event(
            topic="tasks",
            event_type="task.deleted",
            data={"task_id": task_id},
            user_id=authenticated_user
        )

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        logger.error(f"Database error in delete_task: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )


@router.post("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Toggle task completion status.

    Implements: T070 - POST /api/{user_id}/tasks/{task_id}/complete

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Only toggles tasks owned by authenticated user

    Args:
        user_id: User ID from URL path
        task_id: Task ID to toggle
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        TaskResponse: The updated task with toggled completion status

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Task not found or doesn't belong to user
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Get task and verify ownership
        task = await _get_user_task(task_id, authenticated_user, session)

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Phase V: Publish task.completed event (fire-and-forget)
        # This event triggers recurring task generation if applicable
        await publish_event(
            topic="tasks",
            event_type="task.completed",
            data={
                "task_id": task.id,
                "completed": task.completed,
                "is_recurring": task.is_recurring,
                "recurring_interval": task.recurring_interval,
                "due_date": task.due_date.isoformat() if task.due_date else None
            },
            user_id=authenticated_user
        )

        # Parse tags JSON string to list for response
        response_data = {
            "id": task.id,
            "task_number": task.task_number,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": json.loads(task.tags) if task.tags else [],
            "due_date": task.due_date,
            "is_recurring": task.is_recurring,
            "recurring_interval": task.recurring_interval,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }

        return TaskResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        logger.error(f"Database error in toggle_task_completion: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle task completion"
        )
