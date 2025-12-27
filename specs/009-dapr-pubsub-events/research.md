# Research: Dapr Pub/Sub Event System

**Feature**: 009-dapr-pubsub-events
**Date**: 2025-12-25
**Status**: Complete

## Research Questions

### 1. Kafka Deployment Strategy

**Decision**: Strimzi Operator on Kubernetes

**Rationale**:
- Kubernetes-native Kafka deployment
- Declarative topic management
- Automatic rolling upgrades
- Free and open source
- Works on any cloud provider

**Alternatives Considered**:
- Managed Kafka (Confluent Cloud): Expensive for small projects
- Redpanda: Good alternative, but less mature operator
- RabbitMQ: Not ideal for event streaming patterns

### 2. Dapr Pub/Sub Component Name

**Decision**: `kafka-pubsub`

**Rationale**:
- Descriptive name indicating broker type
- Follows Dapr naming conventions
- Easy to identify in multi-component setups

### 3. Event Format

**Decision**: CloudEvents 1.0 specification

**Rationale**:
- Industry standard for event format
- Built-in support in Dapr
- Includes metadata (type, source, time, id)
- Extensible for custom attributes

**Format**:
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "evt-uuid",
  "time": "2025-12-25T10:00:00Z",
  "partitionkey": "user-abc123",
  "data": {...}
}
```

### 4. Partition Key Strategy

**Decision**: user_id as partition key

**Rationale**:
- Ensures all events for a user go to same partition
- Maintains event ordering per user
- Critical for recurring task logic
- Aligns with user isolation principle

**Implementation**:
```python
event = {
    "partitionkey": user_id,  # Dapr uses this for Kafka
    "data": {...}
}
```

### 5. Retry Policy Configuration

**Decision**: 3 retries with exponential backoff (1s, 2s, 4s)

**Rationale**:
- Balances reliability with resource usage
- Exponential backoff prevents thundering herd
- Dead letter queue after 3 failures
- Industry standard approach

### 5a. Dead Letter Queue Handling

**Decision**: Alert-only (generate alert for ops team, manual review required)

**Rationale**:
- Simplest approach for hackathon project
- Provides visibility into failed events
- No complex automated recovery logic
- Prevents masking underlying issues
- Manual review allows for root cause analysis

**Implementation**:
- Events reaching DLQ trigger an alert (log + optional webhook)
- Ops team reviews failed events manually
- No automated retry from DLQ
- DLQ retention: 30 days for investigation

**Dapr Subscription Config**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: tasks
  route: /api/events/tasks
  deadLetterTopic: tasks-dlq
  bulkSubscribe:
    enabled: false
```

### 6. Idempotency Strategy

**Decision**: Idempotency key + state check

**Rationale**:
- Events may be delivered multiple times
- Handlers must produce same result on duplicate
- Use event ID + database state to detect duplicates

**Implementation**:
```python
async def handle_task_completed(event: dict):
    task_id = event["task_id"]
    event_id = event["id"]

    # Check if already processed
    task = await get_task(task_id)
    if task.last_event_id == event_id:
        return  # Already processed

    # Process and update last_event_id
    await create_next_recurring_instance(task)
    await update_task(task_id, last_event_id=event_id)
```

### 7. Fire-and-Forget Pattern

**Decision**: Event publishing doesn't block user requests

**Rationale**:
- User experience not affected by event system
- Task CRUD succeeds even if Kafka unavailable
- Events are best-effort notification
- Aligns with FR-004 requirement

**Implementation**:
```python
# In tasks router
async def create_task(...):
    # 1. Save task to database
    task = await save_task(...)

    # 2. Publish event (fire-and-forget)
    try:
        await publish_event("tasks", "task.created", task.dict(), user_id)
    except Exception as e:
        logger.warning(f"Failed to publish task.created event: {e}")
        # Don't raise - task creation succeeded

    return task
```

### 8. Reminder Notification Delivery

**Decision**: In-app notification only

**Rationale**:
- Simplest to implement
- No external services needed (email/SMS)
- User sees notification on next login/refresh
- Can be extended to email later

**Implementation**:
- reminder.triggered event creates notification record
- Frontend polls for notifications
- Display badge/banner for due tasks

### 9. Topic Configuration

**Decision**: Two topics - `tasks` and `reminders`

**Topics**:
| Topic | Events | Purpose |
|-------|--------|---------|
| tasks | task.* | Task CRUD events |
| reminders | reminder.* | Reminder scheduling/triggers |

**Kafka Topic Config**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: tasks
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
```

### 10. Recurring Task Logic

**Decision**: Event-driven next instance creation

**Flow**:
1. User completes recurring task
2. `task.completed` event published
3. Handler checks `is_recurring` and `recurring_interval`
4. If recurring, create next task with new due_date
5. New task creation triggers `task.created` event

**Interval Calculation**:
```python
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def calculate_next_due_date(current_due: datetime, interval: str) -> datetime:
    if interval == "daily":
        return current_due + timedelta(days=1)
    elif interval == "weekly":
        return current_due + timedelta(weeks=1)
    elif interval == "monthly":
        return current_due + relativedelta(months=1)
```

## Technology Decisions Summary

| Area | Decision |
|------|----------|
| Message Broker | Kafka via Strimzi |
| Dapr Component | kafka-pubsub |
| Event Format | CloudEvents 1.0 |
| Partition Key | user_id |
| Retry Policy | 3x exponential (1s, 2s, 4s) |
| DLQ Handling | Alert-only (manual review) |
| Idempotency | Event ID + state check |
| Publishing | Fire-and-forget |
| Notifications | In-app only |
| Topics | tasks, reminders |

## References

- [Dapr Pub/Sub Building Block](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Dapr Kafka Component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Strimzi Operator](https://strimzi.io/)
- [Idempotency Patterns](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-message-idempotency/)
