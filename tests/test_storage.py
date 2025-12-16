"""
Unit tests for the todo application storage module.
"""
import pytest
from src.storage import (
    add_task_to_storage,
    get_task_by_id,
    get_all_tasks,
    update_task_in_storage,
    delete_task_from_storage,
    toggle_task_completion,
    tasks
)


def setup_function():
    """Clear the in-memory storage before each test."""
    tasks.clear()


def test_add_task_to_storage():
    """Test adding a task to storage."""
    title = "Test Task"
    description = "Test Description"

    result = add_task_to_storage(title, description)

    assert result["title"] == title
    assert result["description"] == description
    assert result["completed"] == False
    assert result["id"] == 1
    assert "created_at" in result
    assert len(tasks) == 1


def test_add_multiple_tasks():
    """Test adding multiple tasks to storage."""
    # Add first task
    task1 = add_task_to_storage("Task 1", "Description 1")
    assert task1["id"] == 1

    # Add second task
    task2 = add_task_to_storage("Task 2", "Description 2")
    assert task2["id"] == 2

    # Verify both tasks exist
    assert len(tasks) == 2


def test_get_task_by_id_success():
    """Test getting a task by ID."""
    # Add a task
    created_task = add_task_to_storage("Test Task", "Test Description")
    task_id = created_task["id"]

    # Retrieve the task
    retrieved_task = get_task_by_id(task_id)

    assert retrieved_task is not None
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Test Task"
    assert retrieved_task["description"] == "Test Description"


def test_get_task_by_id_not_found():
    """Test getting a non-existent task by ID."""
    result = get_task_by_id(999)

    assert result is None


def test_get_all_tasks():
    """Test getting all tasks."""
    # Add multiple tasks
    task1 = add_task_to_storage("Task 1", "Description 1")
    task2 = add_task_to_storage("Task 2", "Description 2")

    all_tasks = get_all_tasks()

    assert len(all_tasks) == 2
    # Tasks should be sorted by creation date (newest first)
    assert all_tasks[0]["id"] == task2["id"]
    assert all_tasks[1]["id"] == task1["id"]


def test_get_all_tasks_empty():
    """Test getting all tasks when storage is empty."""
    all_tasks = get_all_tasks()

    assert len(all_tasks) == 0


def test_update_task_in_storage_success():
    """Test successful task update in storage."""
    # Add a task
    original_task = add_task_to_storage("Original Title", "Original Description")
    task_id = original_task["id"]

    # Update the task
    success = update_task_in_storage(task_id, "Updated Title", "Updated Description")

    assert success is True

    # Verify the update
    updated_task = get_task_by_id(task_id)
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"


def test_update_task_in_storage_partial():
    """Test updating only title or description in storage."""
    # Add a task
    original_task = add_task_to_storage("Original Title", "Original Description")
    task_id = original_task["id"]

    # Update only the title
    success = update_task_in_storage(task_id, title="Updated Title")

    assert success is True

    # Verify the update
    updated_task = get_task_by_id(task_id)
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Original Description"


def test_update_task_in_storage_not_found():
    """Test updating a non-existent task in storage."""
    success = update_task_in_storage(999, "New Title", "New Description")

    assert success is False


def test_delete_task_from_storage_success():
    """Test successful task deletion from storage."""
    # Add a task
    original_task = add_task_to_storage("Test Title", "Test Description")
    task_id = original_task["id"]

    # Verify task exists
    assert get_task_by_id(task_id) is not None

    # Delete the task
    success = delete_task_from_storage(task_id)

    assert success is True

    # Verify task no longer exists
    assert get_task_by_id(task_id) is None
    assert len(tasks) == 0


def test_delete_task_from_storage_not_found():
    """Test deleting a non-existent task from storage."""
    initial_count = len(tasks)
    success = delete_task_from_storage(999)

    assert success is False
    assert len(tasks) == initial_count


def test_toggle_task_completion_success():
    """Test successful completion toggle in storage."""
    # Add a task
    original_task = add_task_to_storage("Test Title", "Test Description")
    task_id = original_task["id"]

    # Initially, task should be incomplete
    assert original_task["completed"] is False

    # Toggle completion
    success = toggle_task_completion(task_id)

    assert success is True

    # Verify the toggle
    toggled_task = get_task_by_id(task_id)
    assert toggled_task["completed"] is False


def test_toggle_task_completion_not_found():
    """Test toggling completion of a non-existent task in storage."""
    success = toggle_task_completion(999)

    assert success is False