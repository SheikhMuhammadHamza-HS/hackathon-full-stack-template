# Data Model: Dapr Pub/Sub Event System

**Feature**: 009-dapr-pubsub-events
**Date**: 2025-12-25

## Event Entities

### CloudEvent (Base)

All events follow CloudEvents 1.0 specification.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| specversion | string | Yes | CloudEvents version ("1.0") |
| type | string | Yes | Event type (e.g., "task.created") |
| source | string | Yes | Event source ("todo-backend") |
| id | string | Yes | Unique event ID (UUID) |
| time | datetime | Yes | Event timestamp (ISO 8601) |
| partitionkey | string | Yes | Kafka partition key (user_id) |
| data | object | Yes | Event payload |

---

### TaskEvent (Abstract)

Base for all task-related events.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Task identifier |
| user_id | string | Yes | User who owns the task |
| timestamp | datetime | Yes | Event timestamp |

---

### TaskCreatedEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Created task ID |
| user_id | string | Yes | Owner user ID |
| title | string | Yes | Task title |
| description | string | No | Task description |
| priority | string | Yes | "low", "medium", "high" |
| tags | string[] | Yes | Task tags (may be empty) |
| due_date | datetime | No | Task due date |
| is_recurring | bool | Yes | Recurring flag |
| recurring_interval | string | No | "daily", "weekly", "monthly" |
| timestamp | datetime | Yes | Creation timestamp |

---

### TaskUpdatedEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Updated task ID |
| user_id | string | Yes | Owner user ID |
| changed_fields | string[] | Yes | List of updated field names |
| priority | string | No | New priority (if changed) |
| due_date | datetime | No | New due date (if changed) |
| timestamp | datetime | Yes | Update timestamp |

---

### TaskCompletedEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Completed task ID |
| user_id | string | Yes | Owner user ID |
| completed | bool | Yes | New completion state |
| is_recurring | bool | Yes | Recurring flag |
| recurring_interval | string | No | Interval if recurring |
| due_date | datetime | No | Due date for next instance |
| timestamp | datetime | Yes | Completion timestamp |

---

### TaskDeletedEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Deleted task ID |
| user_id | string | Yes | Owner user ID |
| timestamp | datetime | Yes | Deletion timestamp |

---

### ReminderScheduledEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Related task ID |
| user_id | string | Yes | Owner user ID |
| remind_at | datetime | Yes | Scheduled reminder time |
| timestamp | datetime | Yes | Scheduling timestamp |

---

### ReminderTriggeredEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | int | Yes | Related task ID |
| user_id | string | Yes | Owner user ID |
| task_title | string | Yes | Task title for notification |
| due_date | datetime | Yes | Task due date |
| timestamp | datetime | Yes | Trigger timestamp |

---

## Supporting Entities

### Notification (Database)

In-app notifications created by reminder handler.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | int | No | Primary key |
| user_id | string | No | FK to users |
| type | string | No | "task_reminder" |
| title | string | No | Notification title |
| message | text | No | Notification body |
| data | jsonb | Yes | Extra data (task_id) |
| read | bool | No | Read status (default false) |
| created_at | timestamp | No | Creation timestamp |

**Indexes**:
- (user_id, read) - For fetching unread notifications
- (user_id, created_at DESC) - For listing recent notifications

---

### ProcessedEvent (Database)

Tracks processed events for idempotency.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| event_id | string | No | Primary key (CloudEvent id) |
| event_type | string | No | Event type |
| processed_at | timestamp | No | Processing timestamp |

**Index**: Primary key on event_id

**Cleanup**: Delete events older than 7 days (matches Kafka retention)

---

## Kafka Topics

### tasks

| Property | Value | Description |
|----------|-------|-------------|
| Partitions | 3 | Parallelism |
| Replication | 1 (dev) / 3 (prod) | Durability |
| Retention | 604800000ms (7 days) | Debug window |
| Cleanup Policy | delete | Standard cleanup |

### reminders

| Property | Value | Description |
|----------|-------|-------------|
| Partitions | 3 | Parallelism |
| Replication | 1 (dev) / 3 (prod) | Durability |
| Retention | 604800000ms (7 days) | Debug window |
| Cleanup Policy | delete | Standard cleanup |

### tasks-dlq

| Property | Value | Description |
|----------|-------|-------------|
| Partitions | 1 | Single partition for DLQ |
| Replication | 1 | Basic durability |
| Retention | 2592000000ms (30 days) | Extended for investigation |
| Cleanup Policy | delete | Standard cleanup |

---

## Dapr Components

### kafka-pubsub Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap.kafka:9092"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-backend"
  - name: maxMessageBytes
    value: "1048576"  # 1MB
```

---

## Relationships

```
User (1) ──────────── (*) Task ──────────── (*) TaskEvent
                        │
                        └──────────────── (*) Notification
                                                │
                                                └── ReminderTriggeredEvent
```

**Event Flow**:
```
Task CRUD ──▶ TaskEvent ──▶ Kafka ──▶ Handler ──▶ Side Effects
                                         │
                                         ├── Create Recurring Task
                                         ├── Schedule Reminder
                                         └── Create Notification
```

---

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| All Events | user_id | Must match task owner |
| All Events | timestamp | Must be valid ISO 8601 |
| TaskCreatedEvent | priority | Must be "low", "medium", or "high" |
| TaskCreatedEvent | recurring_interval | Required if is_recurring=true |
| ReminderScheduledEvent | remind_at | Must be future timestamp |

---

## Migration: Add Notifications Table

```python
"""add_notifications_table

Revision ID: xxx
"""

def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('read', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )
    op.create_index('idx_notifications_user_read', 'notifications', ['user_id', 'read'])
    op.create_index('idx_notifications_user_created', 'notifications', ['user_id', 'created_at'])

    op.create_table(
        'processed_events',
        sa.Column('event_id', sa.String(50), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('processed_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )

def downgrade():
    op.drop_table('processed_events')
    op.drop_table('notifications')
```
