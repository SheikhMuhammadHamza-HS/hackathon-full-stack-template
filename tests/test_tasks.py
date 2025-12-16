"""
Unit tests for the todo application tasks module.
"""
import pytest
from src.tasks import create_task, get_task, get_all_tasks_formatted, update_task, delete_task, toggle_completion
from src.storage import tasks


def setup_function():
    """Clear the in-memory storage before each test."""
    tasks.clear()


def test_create_task_success():
    """Test successful task creation."""
    title = "Test Task"
    description = "Test Description"

    result = create_task(title, description)

    assert result["title"] == title
    assert result["description"] == description
    assert result["completed"] == False
    assert result["id"] == 1
    assert "created_at" in result


def test_create_task_without_description():
    """Test creating a task without description."""
    title = "Test Task"

    result = create_task(title)

    assert result["title"] == title
    assert result["description"] == ""
    assert result["id"] == 1


def test_create_task_invalid_title():
    """Test creating a task with invalid title."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_task("")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_task("   ")

    with pytest.raises(ValueError, match="Title must be 1-200 characters"):
        create_task("a" * 201)


def test_create_task_invalid_description():
    """Test creating a task with invalid description."""
    with pytest.raises(ValueError, match="Description must be 1000 characters or less"):
        create_task("Test", "a" * 1001)


def test_get_task_success():
    """Test getting a task by ID."""
    # Create a task first
    created_task = create_task("Test Task", "Test Description")
    task_id = created_task["id"]

    # Retrieve the task
    retrieved_task = get_task(task_id)

    assert retrieved_task is not None
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Test Task"
    assert retrieved_task["description"] == "Test Description"


def test_get_task_not_found():
    """Test getting a non-existent task."""
    result = get_task(999)

    assert result is None


def test_get_task_invalid_id():
    """Test getting a task with invalid ID."""
    with pytest.raises(ValueError, match="Task ID must be a positive integer"):
        get_task(-1)

    with pytest.raises(ValueError, match="Please enter a valid task ID"):
        get_task("invalid")


def test_get_all_tasks_formatted():
    """Test getting all tasks."""
    # Create multiple tasks
    task1 = create_task("Task 1", "Description 1")
    task2 = create_task("Task 2", "Description 2")

    all_tasks = get_all_tasks_formatted()

    assert len(all_tasks) == 2
    # Tasks should be sorted by creation date (newest first)
    assert all_tasks[0]["id"] == task2["id"]
    assert all_tasks[1]["id"] == task1["id"]


def test_update_task_success():
    """Test successful task update."""
    # Create a task
    original_task = create_task("Original Title", "Original Description")
    task_id = original_task["id"]

    # Update the task
    success = update_task(task_id, "Updated Title", "Updated Description")

    assert success is True

    # Verify the update
    updated_task = get_task(task_id)
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"


def test_update_task_partial():
    """Test updating only title or description."""
    # Create a task
    original_task = create_task("Original Title", "Original Description")
    task_id = original_task["id"]

    # Update only the title
    success = update_task(task_id, title="Updated Title")

    assert success is True

    # Verify the update
    updated_task = get_task(task_id)
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Original Description"


def test_update_task_not_found():
    """Test updating a non-existent task."""
    success = update_task(999, "New Title", "New Description")

    assert success is False


def test_update_task_invalid_id():
    """Test updating a task with invalid ID."""
    with pytest.raises(ValueError, match="Task ID must be a positive integer"):
        update_task(-1, "New Title")


def test_update_task_invalid_inputs():
    """Test updating a task with invalid inputs."""
    # Create a task
    original_task = create_task("Original Title", "Original Description")
    task_id = original_task["id"]

    with pytest.raises(ValueError, match="Title cannot be empty"):
        update_task(task_id, "")

    with pytest.raises(ValueError, match="Title must be 1-200 characters"):
        update_task(task_id, "a" * 201)


def test_delete_task_success():
    """Test successful task deletion."""
    # Create a task
    original_task = create_task("Test Title", "Test Description")
    task_id = original_task["id"]

    # Verify task exists
    assert get_task(task_id) is not None

    # Delete the task
    success = delete_task(task_id)

    assert success is True

    # Verify task no longer exists
    assert get_task(task_id) is None


def test_delete_task_not_found():
    """Test deleting a non-existent task."""
    success = delete_task(999)

    assert success is False


def test_delete_task_invalid_id():
    """Test deleting a task with invalid ID."""
    with pytest.raises(ValueError, match="Task ID must be a positive integer"):
        delete_task(-1)


def test_toggle_completion_success():
    """Test successful completion toggle."""
    # Create a task
    original_task = create_task("Test Title", "Test Description")
    task_id = original_task["id"]

    # Initially, task should be incomplete
    assert original_task["completed"] is False

    # Toggle completion
    success = toggle_completion(task_id)

    assert success is True

    # Verify the toggle
    toggled_task = get_task(task_id)
    assert toggled_task["completed"] is False


def test_toggle_completion_not_found():
    """Test toggling completion of a non-existent task."""
    success = toggle_completion(999)

    assert success is False


def test_toggle_completion_invalid_id():
    """Test toggling completion with invalid ID."""
    with pytest.raises(ValueError, match="Task ID must be a positive integer"):
        toggle_completion(-1)