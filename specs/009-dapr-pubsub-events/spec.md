# Feature Specification: Dapr Pub/Sub Event System

**Feature Branch**: `009-dapr-pubsub-events`
**Created**: 2025-12-25
**Status**: Draft
**Phase**: V (Cloud Deployment & Event-Driven Architecture)
**Input**: Implement event-driven architecture with Dapr Pub/Sub for task operations, including event publishing on task CRUD and subscription handlers for automated workflows.

## Clarifications

### Session 2025-12-25

- Q: When subscriber fails to process an event, how many retries before dead letter queue? → A: 3 retries with exponential backoff (1s, 2s, 4s), then dead letter
- Q: What should be used as Kafka partition key for event ordering? → A: user_id (all user's events in same partition)
- Q: How should reminder notifications be delivered to users? → A: In-app notification only (shown on next login/refresh)
- Q: What should be the Dapr Pub/Sub component name? → A: `kafka-pubsub`

### Session 2025-12-27

- Q: What action should be taken when events reach the dead letter queue? → A: Alert-only (generate alert for ops team, manual review required)

## Overview

Transform the Todo application from a request-response architecture to an event-driven system using Dapr Pub/Sub. Task operations (create, update, delete, complete) will publish domain events that can trigger automated workflows like recurring task scheduling, reminders, and analytics.

## User Scenarios & Testing

### User Story 1 - Task Events for Automation (Priority: P1)

When users perform task operations, corresponding events are published to enable automated workflows without changing user experience.

**Why P1**: Foundation for all event-driven features (recurring tasks, reminders, analytics).

**Independent Test**: Create a task, verify `task.created` event is published to the message broker.

**Acceptance Scenarios**:
1. **Given** user creates a task, **When** task is saved, **Then** `task.created` event published with task data
2. **Given** user marks task complete, **When** status changes, **Then** `task.completed` event published
3. **Given** user deletes a task, **When** deletion confirmed, **Then** `task.deleted` event published
4. **Given** user updates task fields, **When** changes saved, **Then** `task.updated` event published with changed fields
5. **Given** event publishing fails, **When** broker unavailable, **Then** task operation still succeeds (fire-and-forget pattern)

---

### User Story 2 - Recurring Task Auto-Generation (Priority: P1)

When a recurring task is completed, the system automatically creates the next instance based on the interval.

**Why P1**: Core recurring task functionality depends on event subscription.

**Independent Test**: Complete a daily recurring task, verify next instance is created with due date +1 day.

**Acceptance Scenarios**:
1. **Given** daily recurring task completed, **When** `task.completed` event processed, **Then** new task created with due_date +1 day
2. **Given** weekly recurring task completed, **When** event processed, **Then** new task created with due_date +7 days
3. **Given** monthly recurring task completed, **When** event processed, **Then** new task created with due_date +1 month
4. **Given** non-recurring task completed, **When** event processed, **Then** no new task created
5. **Given** recurring task deleted, **When** `task.deleted` event processed, **Then** scheduled future instances cancelled

---

### User Story 3 - Due Date Reminder Scheduling (Priority: P2)

When a task with due date is created or updated, reminder events are scheduled based on configurable rules.

**Why P2**: Enhances user experience but not critical for core functionality.

**Independent Test**: Create task with due date, verify reminder job is scheduled.

**Acceptance Scenarios**:
1. **Given** task created with due_date, **When** `task.created` event processed, **Then** reminder scheduled for 24 hours before due (in-app notification)
2. **Given** task due_date updated, **When** `task.updated` event processed, **Then** old reminder cancelled, new one scheduled
3. **Given** task completed before due, **When** `task.completed` event processed, **Then** pending reminders cancelled
4. **Given** task deleted, **When** `task.deleted` event processed, **Then** all associated reminders cancelled
5. **Given** reminder triggered, **When** user logs in or refreshes, **Then** in-app notification displayed

---

### User Story 4 - Event-Driven Analytics (Priority: P3)

Task events are captured for analytics and reporting purposes.

**Why P3**: Nice-to-have feature for insights, not core functionality.

**Independent Test**: Publish 100 task events, verify event store receives all events.

**Acceptance Scenarios**:
1. **Given** any task event, **When** published, **Then** event logged with timestamp and user_id
2. **Given** analytics subscriber, **When** events received, **Then** aggregate counters updated
3. **Given** event replay needed, **When** requested, **Then** events can be replayed from store

---

### Edge Cases

- Subscriber temporarily unavailable: Events queued in message broker, 3 retries with exponential backoff (1s, 2s, 4s), then dead letter queue with alert for manual review
- Duplicate event delivery: Handlers are idempotent (same event processed twice = same result)
- Event ordering: Events for same user processed in order (user_id as partition key)
- Large event payload: Task data limited to essential fields in event
- Event schema version mismatch: Backward compatible evolution
- Circular event triggers: Prevent infinite loops (e.g., update triggers update)

## Requirements

### Functional Requirements

- **FR-001**: System MUST publish events on task create, update, complete, and delete
- **FR-002**: System MUST use Dapr Pub/Sub for event publishing
- **FR-003**: System MUST include user_id, task_id, and timestamp in all events
- **FR-004**: System MUST NOT block task operations if event publishing fails
- **FR-005**: System MUST subscribe to `task.completed` for recurring task handling
- **FR-006**: System MUST generate next recurring instance within 60 seconds of completion
- **FR-007**: System MUST preserve task fields in recurring instance (except completed/due_date)
- **FR-008**: System MUST subscribe to events for reminder scheduling
- **FR-009**: System MUST cancel reminders when task deleted or completed
- **FR-010**: System MUST ensure event handlers are idempotent
- **FR-011**: System MUST support configurable event topics
- **FR-012**: System MUST maintain per-user event isolation (user can only trigger own events)

### Event Catalog

| Event Type | Topic | Trigger | Payload |
|------------|-------|---------|---------|
| task.created | `tasks` | POST /tasks | task_id, user_id, title, priority, due_date, is_recurring, recurring_interval, timestamp |
| task.updated | `tasks` | PATCH /tasks/{id} | task_id, user_id, changed_fields, timestamp |
| task.completed | `tasks` | Toggle complete | task_id, user_id, is_recurring, recurring_interval, due_date, timestamp |
| task.deleted | `tasks` | DELETE /tasks/{id} | task_id, user_id, timestamp |
| reminder.scheduled | `reminders` | Subscriber | task_id, user_id, remind_at, timestamp |
| reminder.triggered | `reminders` | Scheduled job | task_id, user_id, timestamp |

### Key Entities

- **Domain Event**: Immutable record of something that happened in the system
- **Event Publisher**: Component that emits events after successful operations
- **Event Subscriber**: Component that reacts to events and triggers workflows
- **Event Topic**: Named channel for grouping related events

## Success Criteria

### Measurable Outcomes

- **SC-001**: Events published within 100ms of operation completion
- **SC-002**: 99.9% event delivery success rate
- **SC-003**: Recurring task next instance created within 60 seconds of completion
- **SC-004**: Zero lost events during normal operation
- **SC-005**: System handles 1000 events per minute without degradation
- **SC-006**: Event handlers process messages within 500ms average
- **SC-007**: Subscribers recover from temporary failures within 30 seconds

## Assumptions

- Kafka (via Strimzi) is the message broker
- Dapr Pub/Sub component is configured
- At-least-once delivery semantics acceptable
- Event handlers are designed to be idempotent
- Message ordering per partition (user_id as partition key ensures per-user ordering)
- Event retention of 7 days minimum

## Dependencies

- Phase V Dapr installation on Kubernetes
- Kafka deployment via Strimzi Operator
- Advanced Task Fields (007) implementation
- Dapr State Store (008) for stateful subscribers

## Out of Scope

- Complex event processing (CEP)
- Event sourcing (full system state from events)
- Cross-service saga patterns
- Dead letter queue UI
- Event schema registry
- Custom event routing rules

## Dapr Integration Patterns

### Pub/Sub Operations

| Operation | Dapr HTTP Route | Purpose |
|-----------|-----------------|---------|
| Publish Event | `POST http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}` | Emit domain events |
| Subscribe | `POST /dapr/subscribe` (app endpoint) | Register event handlers |

### Event Publishing Example

```
POST http://localhost:3500/v1.0/publish/kafka-pubsub/tasks
Content-Type: application/cloudevents+json

{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "evt-abc123",
  "time": "2025-12-25T10:00:00Z",
  "data": {
    "task_id": 42,
    "user_id": "user-xyz789",
    "title": "Buy groceries",
    "priority": "high",
    "due_date": "2025-12-26T18:00:00Z",
    "is_recurring": false
  }
}
```

### Subscription Handler Endpoint

```
POST /api/events/task-completed
Content-Type: application/cloudevents+json

# App receives event from Dapr
# Returns 200 OK to acknowledge
# Returns 5xx to trigger retry
```

## Validation Rules

| Field | Validation | Error Response |
|-------|------------|----------------|
| event.type | Must be valid event type from catalog | 400 Bad Request |
| event.data.user_id | Must match authenticated user | 403 Forbidden |
| event.data.task_id | Must be valid existing task | Event logged, no action |
| event.time | Valid ISO 8601 timestamp | 400 Bad Request |
| topic | Must be configured topic | 400 Bad Request |

## Constitution Alignment

- Principle XXII: Event-Driven Architecture (Dapr Pub/Sub)
- Principle XXIII: Dapr Components (Pub/Sub with Kafka)
- Principle VIII: User Isolation (user_id in events)
- Principle XV: Twelve-Factor App (decoupled services via events)
- Principle XXVI: Advanced Task Management (recurring tasks)
