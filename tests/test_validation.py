"""
Unit tests for the todo application validation module.
"""
import pytest
from src.validation import (
    validate_task_title,
    validate_task_description,
    validate_task_id,
    validate_menu_choice,
    validate_confirmation,
    is_valid_confirmation_for_deletion
)


def test_validate_task_title_success():
    """Test successful task title validation."""
    # Valid title
    is_valid, error_msg = validate_task_title("Valid Title")
    assert is_valid is True
    assert error_msg == ""

    # Minimum length
    is_valid, error_msg = validate_task_title("A")
    assert is_valid is True
    assert error_msg == ""

    # Maximum length
    is_valid, error_msg = validate_task_title("A" * 200)
    assert is_valid is True
    assert error_msg == ""


def test_validate_task_title_failure():
    """Test task title validation failures."""
    # Empty title
    is_valid, error_msg = validate_task_title("")
    assert is_valid is False
    assert error_msg == "Title cannot be empty"

    # Whitespace-only title
    is_valid, error_msg = validate_task_title("   ")
    assert is_valid is False
    assert error_msg == "Title cannot be empty"

    # Title too long
    is_valid, error_msg = validate_task_title("A" * 201)
    assert is_valid is False
    assert error_msg == "Title must be 1-200 characters"


def test_validate_task_description_success():
    """Test successful task description validation."""
    # Empty description
    is_valid, error_msg = validate_task_description("")
    assert is_valid is True
    assert error_msg == ""

    # Maximum length
    is_valid, error_msg = validate_task_description("A" * 1000)
    assert is_valid is True
    assert error_msg == ""


def test_validate_task_description_failure():
    """Test task description validation failures."""
    # Description too long
    is_valid, error_msg = validate_task_description("A" * 1001)
    assert is_valid is False
    assert error_msg == "Description must be 1000 characters or less"


def test_validate_task_id_success():
    """Test successful task ID validation."""
    # Valid positive integer as string
    is_valid, error_msg = validate_task_id("1")
    assert is_valid is True
    assert error_msg == ""

    # Valid positive integer
    is_valid, error_msg = validate_task_id(1)
    assert is_valid is True
    assert error_msg == ""

    # Valid larger integer
    is_valid, error_msg = validate_task_id("999")
    assert is_valid is True
    assert error_msg == ""


def test_validate_task_id_failure():
    """Test task ID validation failures."""
    # Zero
    is_valid, error_msg = validate_task_id("0")
    assert is_valid is False
    assert error_msg == "Task ID must be a positive integer"

    # Negative number
    is_valid, error_msg = validate_task_id("-1")
    assert is_valid is False
    assert error_msg == "Task ID must be a positive integer"

    # Non-numeric string
    is_valid, error_msg = validate_task_id("invalid")
    assert is_valid is False
    assert error_msg == "Please enter a valid task ID"

    # Float
    is_valid, error_msg = validate_task_id("1.5")
    assert is_valid is False
    assert error_msg == "Please enter a valid task ID"


def test_validate_menu_choice_success():
    """Test successful menu choice validation."""
    # Valid choices
    for choice in ["1", "2", "3", "4", "5", "6"]:
        is_valid, error_msg = validate_menu_choice(choice)
        assert is_valid is True
        assert error_msg == ""


def test_validate_menu_choice_failure():
    """Test menu choice validation failures."""
    # Below range
    is_valid, error_msg = validate_menu_choice("0")
    assert is_valid is False
    assert error_msg == "Please enter a number between 1 and 6"

    # Above range
    is_valid, error_msg = validate_menu_choice("7")
    assert is_valid is False
    assert error_msg == "Please enter a number between 1 and 6"

    # Non-numeric
    is_valid, error_msg = validate_menu_choice("invalid")
    assert is_valid is False
    assert error_msg == "Please enter a valid number"


def test_validate_confirmation_success():
    """Test successful confirmation validation."""
    # Valid yes responses
    for response in ["y", "Y", "yes", "YES", "Yes", "  y  ", "  yes  "]:
        is_valid, error_msg = validate_confirmation(response)
        assert is_valid is True
        assert error_msg == ""

    # Valid no responses
    for response in ["n", "N", "no", "NO", "No", "  n  ", "  no  "]:
        is_valid, error_msg = validate_confirmation(response)
        assert is_valid is True
        assert error_msg == ""


def test_validate_confirmation_failure():
    """Test confirmation validation failures."""
    # Invalid responses
    invalid_responses = ["maybe", "ok", "sure", "1", "0", "yep", "nope"]

    for response in invalid_responses:
        is_valid, error_msg = validate_confirmation(response)
        assert is_valid is False
        assert error_msg == "Please enter Y for yes or N for no"


def test_is_valid_confirmation_for_deletion():
    """Test the deletion confirmation check function."""
    # Valid deletion confirmations
    for response in ["y", "Y", "yes", "YES", "Yes", "  y  ", "  yes  "]:
        result = is_valid_confirmation_for_deletion(response)
        assert result is True

    # Invalid deletion confirmations
    invalid_responses = ["n", "N", "no", "NO", "No", "maybe", "ok", "sure"]

    for response in invalid_responses:
        result = is_valid_confirmation_for_deletion(response)
        assert result is False