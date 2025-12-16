"""
In-memory storage management for todo tasks.

This module provides functions for managing tasks in memory,
including creating, retrieving, updating, and deleting tasks.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

# Global in-memory storage for tasks
tasks: List[Dict[str, Union[int, str, bool]]] = []


def get_next_id() -> int:
    """Generate the next unique task ID."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def add_task_to_storage(title: str, description: str = "") -> Dict[str, Union[int, str, bool]]:
    """
    Add a new task to the in-memory storage.

    Args:
        title: The task title (1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        The created task dictionary
    """
    task_id = get_next_id()
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    return task


def get_task_by_id(task_id: int) -> Optional[Dict[str, Union[int, str, bool]]]:
    """
    Retrieve a task by its ID.

    Args:
        task_id: The ID of the task to retrieve

    Returns:
        The task dictionary if found, None otherwise
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def get_all_tasks() -> List[Dict[str, Union[int, str, bool]]]:
    """
    Retrieve all tasks, sorted by creation date (newest first).

    Returns:
        List of all tasks sorted by creation date
    """
    return sorted(tasks, key=lambda x: x["created_at"], reverse=True)


def update_task_in_storage(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> bool:
    """
    Update an existing task in storage.

    Args:
        task_id: The ID of the task to update
        title: New title (if provided)
        description: New description (if provided)

    Returns:
        True if task was updated, False if task not found
    """
    task = get_task_by_id(task_id)
    if not task:
        return False

    if title is not None:
        task["title"] = title
    if description is not None:
        task["description"] = description

    return True


def delete_task_from_storage(task_id: int) -> bool:
    """
    Delete a task from storage.

    Args:
        task_id: The ID of the task to delete

    Returns:
        True if task was deleted, False if task not found
    """
    global tasks
    initial_length = len(tasks)
    tasks = [task for task in tasks if task["id"] != task_id]
    return len(tasks) != initial_length


def toggle_task_completion(task_id: int) -> bool:
    """
    Toggle the completion status of a task.

    Args:
        task_id: The ID of the task to toggle

    Returns:
        True if task status was toggled, False if task not found
    """
    task = get_task_by_id(task_id)
    if not task:
        return False

    task["completed"] = not task["completed"]
    return True