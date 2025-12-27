# Event Catalog: Dapr Pub/Sub Events

**Feature**: 009-dapr-pubsub-events
**Date**: 2025-12-25

## Event Types

### task.created

Published when a new task is created.

**Topic**: `tasks`
**Trigger**: POST /api/{user_id}/tasks
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "evt-abc123",
  "time": "2025-12-25T10:00:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "title": "Buy groceries",
    "description": "Get milk and eggs",
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_date": "2025-12-26T18:00:00Z",
    "is_recurring": false,
    "recurring_interval": null,
    "timestamp": "2025-12-25T10:00:00Z"
  }
}
```

---

### task.updated

Published when a task is updated.

**Topic**: `tasks`
**Trigger**: PATCH /api/{user_id}/tasks/{task_id}
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "task.updated",
  "source": "todo-backend",
  "id": "evt-def456",
  "time": "2025-12-25T10:05:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "changed_fields": ["priority", "due_date"],
    "priority": "medium",
    "due_date": "2025-12-27T18:00:00Z",
    "timestamp": "2025-12-25T10:05:00Z"
  }
}
```

---

### task.completed

Published when a task's completion status is toggled.

**Topic**: `tasks`
**Trigger**: POST /api/{user_id}/tasks/{task_id}/complete
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "task.completed",
  "source": "todo-backend",
  "id": "evt-ghi789",
  "time": "2025-12-25T10:10:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "completed": true,
    "is_recurring": true,
    "recurring_interval": "daily",
    "due_date": "2025-12-26T18:00:00Z",
    "timestamp": "2025-12-25T10:10:00Z"
  }
}
```

**Handler Actions**:
- If `is_recurring=true`: Create next task instance with new due_date

---

### task.deleted

Published when a task is deleted.

**Topic**: `tasks`
**Trigger**: DELETE /api/{user_id}/tasks/{task_id}
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "task.deleted",
  "source": "todo-backend",
  "id": "evt-jkl012",
  "time": "2025-12-25T10:15:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "timestamp": "2025-12-25T10:15:00Z"
  }
}
```

**Handler Actions**:
- Cancel any scheduled reminders for this task

---

### reminder.scheduled

Published when a reminder is scheduled for a task.

**Topic**: `reminders`
**Trigger**: Event handler (on task.created/task.updated with due_date)
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "reminder.scheduled",
  "source": "todo-backend",
  "id": "evt-mno345",
  "time": "2025-12-25T10:00:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "remind_at": "2025-12-25T18:00:00Z",
    "timestamp": "2025-12-25T10:00:00Z"
  }
}
```

---

### reminder.triggered

Published when a reminder fires (via Dapr Jobs API).

**Topic**: `reminders`
**Trigger**: Dapr Jobs scheduled event
**Partition Key**: user_id

```json
{
  "specversion": "1.0",
  "type": "reminder.triggered",
  "source": "todo-backend",
  "id": "evt-pqr678",
  "time": "2025-12-25T18:00:00Z",
  "partitionkey": "user-xyz789",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "task_title": "Buy groceries",
    "due_date": "2025-12-26T18:00:00Z",
    "timestamp": "2025-12-25T18:00:00Z"
  }
}
```

**Handler Actions**:
- Create in-app notification for user

---

## Event Schema (Pydantic Models)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional, List

class TaskCreatedEvent(BaseModel):
    task_id: int
    user_id: str
    title: str
    description: Optional[str]
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    is_recurring: bool
    recurring_interval: Optional[str]
    timestamp: datetime

class TaskUpdatedEvent(BaseModel):
    task_id: int
    user_id: str
    changed_fields: List[str]
    priority: Optional[str]
    due_date: Optional[datetime]
    timestamp: datetime

class TaskCompletedEvent(BaseModel):
    task_id: int
    user_id: str
    completed: bool
    is_recurring: bool
    recurring_interval: Optional[str]
    due_date: Optional[datetime]
    timestamp: datetime

class TaskDeletedEvent(BaseModel):
    task_id: int
    user_id: str
    timestamp: datetime

class ReminderScheduledEvent(BaseModel):
    task_id: int
    user_id: str
    remind_at: datetime
    timestamp: datetime

class ReminderTriggeredEvent(BaseModel):
    task_id: int
    user_id: str
    task_title: str
    due_date: datetime
    timestamp: datetime
```

---

## Topics Configuration

### tasks

| Property | Value |
|----------|-------|
| Partitions | 3 |
| Replication Factor | 1 (dev) / 3 (prod) |
| Retention | 7 days |
| Partition Key | user_id |

### reminders

| Property | Value |
|----------|-------|
| Partitions | 3 |
| Replication Factor | 1 (dev) / 3 (prod) |
| Retention | 7 days |
| Partition Key | user_id |

### tasks-dlq (Dead Letter Queue)

| Property | Value |
|----------|-------|
| Partitions | 1 |
| Replication Factor | 1 |
| Retention | 30 days |

---

## Publishing via Dapr

```bash
# Publish event
POST http://localhost:3500/v1.0/publish/kafka-pubsub/tasks
Content-Type: application/cloudevents+json

{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  ...
}
```

---

## Subscribing via Dapr

```python
# GET /dapr/subscribe
[
    {
        "pubsubname": "kafka-pubsub",
        "topic": "tasks",
        "route": "/api/events/tasks",
        "metadata": {
            "deadLetterTopic": "tasks-dlq"
        }
    },
    {
        "pubsubname": "kafka-pubsub",
        "topic": "reminders",
        "route": "/api/events/reminders"
    }
]
```
