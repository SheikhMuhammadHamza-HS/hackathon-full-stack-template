"""
Input validation functions for the todo application.

This module provides functions to validate user inputs
according to the specification requirements.
"""

from typing import Union


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Validate task title according to specification.

    Args:
        title: The task title to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Title cannot be empty"

    if len(title) < 1 or len(title) > 200:
        return False, "Title must be 1-200 characters"

    return True, ""


def validate_task_description(description: str) -> tuple[bool, str]:
    """
    Validate task description according to specification.

    Args:
        description: The task description to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(description) > 1000:
        return False, "Description must be 1000 characters or less"

    return True, ""


def validate_task_id(task_id: Union[str, int]) -> tuple[bool, str]:
    """
    Validate task ID according to specification.

    Args:
        task_id: The task ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        task_id_int = int(task_id)
        if task_id_int <= 0:
            return False, "Task ID must be a positive integer"
        return True, ""
    except (ValueError, TypeError):
        return False, "Please enter a valid task ID"


def validate_menu_choice(choice: str) -> tuple[bool, str]:
    """
    Validate menu choice according to specification.

    Args:
        choice: The menu choice to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        choice_int = int(choice)
        if choice_int < 1 or choice_int > 6:
            return False, "Please enter a number between 1 and 6"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"


def validate_confirmation(confirmation: str) -> tuple[bool, str]:
    """
    Validate confirmation input (Y/N) according to specification.

    Args:
        confirmation: The confirmation input to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    confirmation = confirmation.strip().lower()
    if confirmation not in ['y', 'n', 'yes', 'no']:
        return False, "Please enter Y for yes or N for no"
    return True, ""


def is_valid_confirmation_for_deletion(confirmation: str) -> bool:
    """
    Check if confirmation is valid for deletion (Y/Yes).

    Args:
        confirmation: The confirmation input

    Returns:
        True if confirmation is for deletion, False otherwise
    """
    confirmation = confirmation.strip().lower()
    return confirmation in ['y', 'yes']