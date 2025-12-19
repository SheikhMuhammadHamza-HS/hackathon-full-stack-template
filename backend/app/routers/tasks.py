"""Task CRUD API endpoints with user isolation.

Implements: Spec requirement T062-T070 for task management
All endpoints enforce strict user isolation - tasks can only be accessed
by their owner. Authentication via JWT is required for all operations.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth import verify_jwt
from app.database import get_session
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

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
    session: AsyncSession = Depends(get_session)
):
    """
    List all tasks for the authenticated user.

    Implements: T062 - GET /api/{user_id}/tasks

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Returns only tasks owned by authenticated user

    Args:
        user_id: User ID from URL path
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        List[TaskResponse]: List of user's tasks ordered by creation date

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Query tasks filtered by authenticated_user (NOT url user_id)
        result = await session.execute(
            select(Task)
            .where(Task.user_id == authenticated_user)
            .order_by(Task.created_at.desc())
        )
        tasks = result.scalars().all()
        return tasks

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

    Implements: T063 - POST /api/{user_id}/tasks

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Task is created with authenticated_user as owner

    Args:
        user_id: User ID from URL path
        task_data: Task creation data (title, description)
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        TaskResponse: The created task

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 400: Invalid task data
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Create task with authenticated_user as owner
        task = Task(
            user_id=authenticated_user,  # Use JWT user_id, not URL user_id
            title=task_data.title,
            description=task_data.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    except Exception as e:
        # Log error server-side, return generic message
        print(f"Database error in create_task: {e}")
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

    Implements: T064 - PATCH /api/{user_id}/tasks/{task_id}

    Security:
    - Requires valid JWT token
    - Validates user_id matches authenticated user
    - Only updates tasks owned by authenticated user

    Args:
        user_id: User ID from URL path
        task_id: Task ID to update
        task_data: Fields to update (title, description, completed)
        authenticated_user: User ID extracted from JWT
        session: Database session

    Returns:
        TaskResponse: The updated task

    Raises:
        HTTPException 401: Invalid or missing JWT token
        HTTPException 403: user_id doesn't match authenticated user
        HTTPException 404: Task not found or doesn't belong to user
        HTTPException 400: Invalid task data
        HTTPException 500: Database error
    """
    # Validate user_id matches JWT user_id
    await _validate_user_access(user_id, authenticated_user)

    try:
        # Get task and verify ownership
        task = await _get_user_task(task_id, authenticated_user, session)

        # Update only provided fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed

        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        print(f"Database error in update_task: {e}")
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

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        print(f"Database error in delete_task: {e}")
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

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        raise
    except Exception as e:
        # Log error server-side, return generic message
        print(f"Database error in toggle_task_completion: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle task completion"
        )
