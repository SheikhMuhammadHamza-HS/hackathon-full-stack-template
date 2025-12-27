# Subscription Handlers: Dapr Pub/Sub Events

**Feature**: 009-dapr-pubsub-events
**Date**: 2025-12-25

## Dapr Subscription Endpoint

### GET /dapr/subscribe

Returns list of topic subscriptions for Dapr to configure.

**Response 200 OK**:
```json
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

---

## Event Handlers

### POST /api/events/tasks

Handles all task-related events.

**Request** (CloudEvent from Dapr):
```json
{
  "specversion": "1.0",
  "type": "task.completed",
  "source": "todo-backend",
  "id": "evt-abc123",
  "time": "2025-12-25T10:00:00Z",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "is_recurring": true,
    "recurring_interval": "daily",
    "due_date": "2025-12-26T18:00:00Z"
  }
}
```

**Response 200 OK** (Success - event processed):
```json
{
  "status": "ok"
}
```

**Response 500 Internal Server Error** (Retry):
```json
{
  "status": "error",
  "message": "Processing failed"
}
```

**Handler Logic**:
```python
@router.post("/api/events/tasks")
async def handle_task_event(request: Request):
    event = await request.json()
    event_type = event.get("type")
    data = event.get("data", {})

    try:
        if event_type == "task.created":
            await handle_task_created(data)
        elif event_type == "task.updated":
            await handle_task_updated(data)
        elif event_type == "task.completed":
            await handle_task_completed(data)
        elif event_type == "task.deleted":
            await handle_task_deleted(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Event processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### POST /api/events/reminders

Handles reminder-related events.

**Request** (CloudEvent from Dapr):
```json
{
  "specversion": "1.0",
  "type": "reminder.triggered",
  "source": "todo-backend",
  "id": "evt-def456",
  "time": "2025-12-25T18:00:00Z",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "task_title": "Buy groceries",
    "due_date": "2025-12-26T18:00:00Z"
  }
}
```

**Response 200 OK**:
```json
{
  "status": "ok"
}
```

**Handler Logic**:
```python
@router.post("/api/events/reminders")
async def handle_reminder_event(request: Request):
    event = await request.json()
    event_type = event.get("type")
    data = event.get("data", {})

    try:
        if event_type == "reminder.scheduled":
            await handle_reminder_scheduled(data)
        elif event_type == "reminder.triggered":
            await handle_reminder_triggered(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Event processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Handler Implementations

### handle_task_created

```python
async def handle_task_created(data: dict):
    """Handle task.created event - schedule reminder if due_date set"""
    task_id = data["task_id"]
    user_id = data["user_id"]
    due_date = data.get("due_date")

    if due_date:
        # Schedule reminder 24 hours before due
        remind_at = datetime.fromisoformat(due_date) - timedelta(hours=24)
        if remind_at > datetime.utcnow():
            await publish_event("reminders", "reminder.scheduled", {
                "task_id": task_id,
                "user_id": user_id,
                "remind_at": remind_at.isoformat()
            }, user_id)
```

### handle_task_completed

```python
async def handle_task_completed(data: dict):
    """Handle task.completed event - create next recurring instance"""
    task_id = data["task_id"]
    user_id = data["user_id"]
    is_recurring = data.get("is_recurring", False)
    interval = data.get("recurring_interval")
    due_date = data.get("due_date")
    completed = data.get("completed", False)

    # Only process if task was marked complete (not uncomplete)
    if not completed:
        return

    # Create next instance for recurring tasks
    if is_recurring and interval and due_date:
        next_due = calculate_next_due_date(
            datetime.fromisoformat(due_date),
            interval
        )

        # Get original task data
        task = await get_task(task_id, user_id)
        if task:
            # Create new task instance
            new_task = await create_task(
                user_id=user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags,
                due_date=next_due,
                is_recurring=True,
                recurring_interval=interval
            )
            logger.info(f"Created next recurring instance: {new_task.id}")
```

### handle_task_deleted

```python
async def handle_task_deleted(data: dict):
    """Handle task.deleted event - cancel pending reminders"""
    task_id = data["task_id"]
    user_id = data["user_id"]

    # Cancel any scheduled reminders via Dapr Jobs API
    try:
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"http://localhost:3500/v1.0/jobs/reminder-{task_id}"
            )
    except Exception as e:
        logger.warning(f"Failed to cancel reminder: {e}")
```

### handle_reminder_triggered

```python
async def handle_reminder_triggered(data: dict):
    """Handle reminder.triggered event - create in-app notification"""
    task_id = data["task_id"]
    user_id = data["user_id"]
    task_title = data["task_title"]
    due_date = data["due_date"]

    # Create notification record (for in-app display)
    await create_notification(
        user_id=user_id,
        type="task_reminder",
        title=f"Task due soon: {task_title}",
        message=f"Your task is due on {due_date}",
        data={"task_id": task_id}
    )
    logger.info(f"Created reminder notification for task {task_id}")
```

---

## Idempotency

All handlers MUST be idempotent (safe to process duplicate events).

**Pattern**:
```python
async def handle_task_completed(data: dict):
    task_id = data["task_id"]
    event_id = data.get("event_id")  # CloudEvent id

    # Check if already processed
    processed = await check_processed_event(event_id)
    if processed:
        logger.info(f"Event {event_id} already processed, skipping")
        return

    # Process event
    await process_recurring_task(data)

    # Mark as processed
    await mark_event_processed(event_id)
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Handler throws exception | Return 500, Dapr retries |
| Database unavailable | Return 500, retry |
| Task not found | Log warning, return 200 (ack) |
| Invalid event data | Log error, return 200 (ack - don't retry bad data) |
| After 3 retries | Move to dead letter queue |

---

## Retry Configuration

Configured in Dapr component:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: todo-resiliency
spec:
  policies:
    retries:
      pubsubRetry:
        policy: exponential
        maxInterval: 4s
        maxRetries: 3
  targets:
    components:
      kafka-pubsub:
        inbound:
          retry: pubsubRetry
```
