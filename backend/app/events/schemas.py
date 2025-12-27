"""Pydantic schemas for Dapr Pub/Sub events.

Implements: 009-dapr-pubsub-events spec - Event Catalog
All events follow CloudEvents 1.0 specification format.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Task Events (Topic: tasks)
# ============================================================================

class TaskCreatedEvent(BaseModel):
    """Event published when a new task is created.

    Topic: tasks
    Trigger: POST /api/{user_id}/tasks
    """
    task_id: int
    user_id: str
    title: str
    description: Optional[str] = None
    priority: str  # "low", "medium", "high"
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurring_interval: Optional[str] = None  # "daily", "weekly", "monthly"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskUpdatedEvent(BaseModel):
    """Event published when a task is updated.

    Topic: tasks
    Trigger: PATCH /api/{user_id}/tasks/{task_id}
    """
    task_id: int
    user_id: str
    changed_fields: List[str]  # List of field names that changed
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskCompletedEvent(BaseModel):
    """Event published when a task's completion status is toggled.

    Topic: tasks
    Trigger: PATCH /api/{user_id}/tasks/{task_id} with completed field
    Handler Actions: If is_recurring=true, create next task instance
    """
    task_id: int
    user_id: str
    completed: bool  # New completion state
    is_recurring: bool = False
    recurring_interval: Optional[str] = None
    due_date: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskDeletedEvent(BaseModel):
    """Event published when a task is deleted.

    Topic: tasks
    Trigger: DELETE /api/{user_id}/tasks/{task_id}
    Handler Actions: Cancel any scheduled reminders
    """
    task_id: int
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Reminder Events (Topic: reminders)
# ============================================================================

class ReminderScheduledEvent(BaseModel):
    """Event published when a reminder is scheduled for a task.

    Topic: reminders
    Trigger: Event handler (on task.created/task.updated with due_date)
    """
    task_id: int
    user_id: str
    remind_at: datetime  # When the reminder should fire
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReminderTriggeredEvent(BaseModel):
    """Event published when a reminder fires.

    Topic: reminders
    Trigger: Dapr Jobs scheduled event
    Handler Actions: Create in-app notification
    """
    task_id: int
    user_id: str
    task_title: str
    due_date: datetime
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# CloudEvent Wrapper
# ============================================================================

class CloudEvent(BaseModel):
    """CloudEvents 1.0 specification wrapper.

    All events are published in this format via Dapr Pub/Sub.
    """
    specversion: str = "1.0"
    type: str  # e.g., "task.created", "task.completed"
    source: str = "todo-backend"
    id: str  # UUID
    time: datetime
    partitionkey: str  # user_id for Kafka partitioning
    data: dict  # Event payload
