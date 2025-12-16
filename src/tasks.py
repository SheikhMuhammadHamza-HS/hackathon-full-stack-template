"""
Task CRUD operations for the todo application.

This module provides functions to perform CRUD operations
on tasks, using the storage and validation modules.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from .storage import (
    add_task_to_storage,
    get_task_by_id,
    get_all_tasks,
    update_task_in_storage,
    delete_task_from_storage,
    toggle_task_completion
)
from .validation import (
    validate_task_title,
    validate_task_description,
    validate_task_id
)


def create_task(title: str, description: str = "") -> Dict[str, Union[int, str, bool]]:
    """
    Create a new task after validating inputs.

    Args:
        title: The task title (1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        The created task dictionary

    Raises:
        ValueError: If validation fails
    """
    # Validate title
    is_valid, error_msg = validate_task_title(title)
    if not is_valid:
        raise ValueError(error_msg)

    # Validate description
    is_valid, error_msg = validate_task_description(description)
    if not is_valid:
        raise ValueError(error_msg)

    # Create task in storage
    return add_task_to_storage(title, description)


def get_task(task_id: int) -> Optional[Dict[str, Union[int, str, bool]]]:
    """
    Get a task by its ID.

    Args:
        task_id: The ID of the task to retrieve

    Returns:
        The task dictionary if found, None otherwise
    """
    # Validate task ID
    is_valid, error_msg = validate_task_id(task_id)
    if not is_valid:
        raise ValueError(error_msg)

    return get_task_by_id(task_id)


def get_all_tasks_formatted() -> List[Dict[str, Union[int, str, bool]]]:
    """
    Get all tasks formatted for display.

    Returns:
        List of all tasks sorted by creation date (newest first)
    """
    return get_all_tasks()


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> bool:
    """
    Update an existing task after validating inputs.

    Args:
        task_id: The ID of the task to update
        title: New title (if provided)
        description: New description (if provided)

    Returns:
        True if task was updated, False if task not found

    Raises:
        ValueError: If validation fails
    """
    # Validate task ID
    is_valid, error_msg = validate_task_id(task_id)
    if not is_valid:
        raise ValueError(error_msg)

    # Validate title if provided
    if title is not None:
        is_valid, error_msg = validate_task_title(title)
        if not is_valid:
            raise ValueError(error_msg)

    # Validate description if provided
    if description is not None:
        is_valid, error_msg = validate_task_description(description)
        if not is_valid:
            raise ValueError(error_msg)

    return update_task_in_storage(task_id, title, description)


def delete_task(task_id: int) -> bool:
    """
    Delete a task after validating the ID.

    Args:
        task_id: The ID of the task to delete

    Returns:
        True if task was deleted, False if task not found

    Raises:
        ValueError: If validation fails
    """
    # Validate task ID
    is_valid, error_msg = validate_task_id(task_id)
    if not is_valid:
        raise ValueError(error_msg)

    return delete_task_from_storage(task_id)


def toggle_completion(task_id: int) -> bool:
    """
    Toggle the completion status of a task after validating the ID.

    Args:
        task_id: The ID of the task to toggle

    Returns:
        True if task status was toggled, False if task not found

    Raises:
        ValueError: If validation fails
    """
    # Validate task ID
    is_valid, error_msg = validate_task_id(task_id)
    if not is_valid:
        raise ValueError(error_msg)

    return toggle_task_completion(task_id)


def format_task_for_display(task: Dict[str, Union[int, str, bool]]) -> str:
    """
    Format a task for display in the console.

    Args:
        task: The task dictionary to format

    Returns:
        Formatted string representation of the task
    """
    status = "✓" if task["completed"] else "✗"
    created_at = task["created_at"]
    # Convert ISO format to readable format if needed
    if "T" in created_at:
        # Parse ISO format and convert to readable format
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If parsing fails, use the original string
            pass

    return f"{task['id']:>3} | {task['title']:<20} | {status:<6} | {created_at}"


def format_tasks_list(tasks_list: List[Dict[str, Union[int, str, bool]]]) -> str:
    """
    Format a list of tasks for display in the console.

    Args:
        tasks_list: List of task dictionaries to format

    Returns:
        Formatted string representation of the task list
    """
    if not tasks_list:
        return "No tasks found. Add your first task!"

    result = "All Tasks:\n"
    result += f"Total: {len(tasks_list)}\n"
    result += f"{'ID':<4} | {'Title':<20} | {'Status':<6} | {'Created'}\n"
    result += f"{'-'*4:<4} | {'-'*20:<20} | {'-'*6:<6} | {'-'*18}\n"

    for task in tasks_list:
        result += format_task_for_display(task) + "\n"

    return result