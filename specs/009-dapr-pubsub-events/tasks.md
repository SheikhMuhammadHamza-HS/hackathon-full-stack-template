# Implementation Tasks: Dapr Pub/Sub Event System

**Feature**: 009-dapr-pubsub-events
**Generated**: 2025-12-25 | **Updated**: 2025-12-27
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup & Infrastructure

- [x] [009-001] [P0] [Setup] Install Strimzi Operator in kafka namespace via `kubectl apply -f https://strimzi.io/install/latest`
- [x] [009-002] [P0] [Setup] Create Kafka cluster manifest at `k8s/kafka/strimzi/kafka-cluster.yaml`
- [x] [009-003] [P0] [Setup] Create Kafka topics manifest at `k8s/kafka/strimzi/kafka-topics.yaml` (tasks, reminders, tasks-dlq)
- [x] [009-004] [P0] [Setup] Create Dapr Pub/Sub component at `k8s/dapr-components/kafka-pubsub.yaml`
- [x] [009-005] [P0] [Setup] Deploy Kafka cluster and verify with `kubectl get kafka -n kafka`
- [ ] [009-006] [P0] [Setup] Verify Dapr Pub/Sub component with `dapr components -k -n todo-app`

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] [009-007] [P1] [Foundation] Create `backend/app/events/__init__.py` package
- [x] [009-008] [P1] [Foundation] Create `backend/app/events/schemas.py` with Pydantic event models (TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent, ReminderScheduledEvent, ReminderTriggeredEvent)
- [x] [009-009] [P1] [Foundation] Create `backend/app/events/publisher.py` with `publish_event(topic, event_type, data, user_id)` function
- [x] [009-010] [P1] [Foundation] Implement CloudEvents 1.0 format in publisher (specversion, type, source, id, time, partitionkey)
- [x] [009-011] [P1] [Foundation] Add fire-and-forget error handling in publisher (log but don't fail user request)
- [x] [009-012] [P1] [Foundation] Create `backend/app/routers/events.py` with subscription endpoint `/dapr/subscribe`
- [x] [009-013] [P1] [Foundation] Register events router in `backend/app/main.py`

---

## Phase 3: User Story 1 - Task Events for Automation (P1)

> When users perform task operations, corresponding events are published to enable automated workflows.

- [x] [009-014] [P1] [Story1] Add `task.created` event publishing to POST /api/{user_id}/tasks in `backend/app/routers/tasks.py`
- [x] [009-015] [P1] [Story1] Add `task.updated` event publishing to PATCH /api/{user_id}/tasks/{task_id}
- [x] [009-016] [P1] [Story1] Add `task.completed` event publishing to POST /api/{user_id}/tasks/{task_id}/complete
- [x] [009-017] [P1] [Story1] Add `task.deleted` event publishing to DELETE /api/{user_id}/tasks/{task_id}
- [x] [009-018] [P1] [Story1] Include user_id as partition key in all events for ordering
- [ ] [009-019] [P1] [Story1] Test: Create task, verify `task.created` event published to Kafka

---

## Phase 4: User Story 2 - Recurring Task Auto-Generation (P1)

> When a recurring task is completed, the system automatically creates the next instance based on the interval.

- [x] [009-020] [P1] [Story2] Create `backend/app/events/handlers.py` with event handler functions
- [x] [009-021] [P1] [Story2] Implement POST `/api/events/tasks` endpoint for receiving task events from Dapr
- [x] [009-022] [P1] [Story2] Create `backend/app/services/recurring_tasks.py` with recurring task logic (in handlers.py)
- [x] [009-023] [P1] [Story2] Implement `handle_task_completed()` to check is_recurring flag
- [x] [009-024] [P1] [Story2] Implement `calculate_next_due_date(current_due, interval)` for daily/weekly/monthly
- [x] [009-025] [P1] [Story2] Create next task instance preserving title, description, priority, tags, is_recurring, recurring_interval
- [x] [009-026] [P1] [Story2] Implement idempotency check using event ID to prevent duplicate task creation
- [ ] [009-027] [P1] [Story2] Test: Complete daily recurring task, verify next instance created with due_date +1 day

---

## Phase 5: User Story 3 - Due Date Reminder Scheduling (P2)

> When a task with due date is created or updated, reminder events are scheduled.

- [ ] [009-028] [P2] [Story3] Implement `handle_task_created()` to schedule reminder for tasks with due_date
- [ ] [009-029] [P2] [Story3] Schedule reminder 24 hours before due date (if due date is >24h away)
- [ ] [009-030] [P2] [Story3] Publish `reminder.scheduled` event to reminders topic
- [ ] [009-031] [P2] [Story3] Implement POST `/api/events/reminders` endpoint for reminder events
- [ ] [009-032] [P2] [Story3] Implement `handle_reminder_triggered()` to create in-app notification
- [ ] [009-033] [P2] [Story3] Create Notification model and database table for in-app notifications
- [ ] [009-034] [P2] [Story3] Create Alembic migration for notifications table with indexes
- [ ] [009-035] [P2] [Story3] Cancel reminders when task completed or deleted (via Dapr Jobs API delete)
- [ ] [009-036] [P2] [Story3] Test: Create task with due_date, verify reminder scheduled

---

## Phase 6: User Story 4 - Event-Driven Analytics (P3)

> Task events are captured for analytics and reporting purposes.

- [ ] [009-037] [P3] [Story4] Add event logging with timestamp, user_id, event_type to all handlers
- [ ] [009-038] [P3] [Story4] Create ProcessedEvent table for idempotency tracking
- [ ] [009-039] [P3] [Story4] Create Alembic migration for processed_events table
- [ ] [009-040] [P3] [Story4] Implement event ID storage to prevent duplicate processing

---

## Phase 7: Error Handling & Resilience

- [x] [009-041] [P1] [Edge] Configure dead letter topic (tasks-dlq) in subscription metadata
- [x] [009-042] [P1] [Edge] Implement retry logic: 3 retries with exponential backoff (1s, 2s, 4s)
- [x] [009-043] [P1] [Edge] Return 200 OK for successfully processed events
- [x] [009-044] [P1] [Edge] Return 500 for transient failures (triggers Dapr retry)
- [x] [009-045] [P1] [Edge] Handle malformed event data gracefully - log and acknowledge (return 200)
- [x] [009-046] [P1] [Edge] Prevent circular event triggers (task.created from handler shouldn't trigger handler)
- [x] [009-047] [P1] [Edge] Add circuit breaker for external service calls in handlers
- [x] [009-048] [P1] [Edge] Implement DLQ alert logging (alert-only, no auto-retry from DLQ)

---

## Phase 8: Dapr Resiliency Configuration

- [x] [009-049] [P1] [Config] Create Dapr resiliency policy at `k8s/dapr-components/resiliency.yaml`
- [x] [009-050] [P1] [Config] Configure pubsubRetry policy: exponential backoff, maxRetries: 3, maxInterval: 4s
- [x] [009-051] [P1] [Config] Apply resiliency to kafka-pubsub component for inbound messages

---

## Phase 9: Testing

- [x] [009-052] [P1] [Test] Create `backend/tests/test_event_publisher.py` with publisher unit tests
- [x] [009-053] [P1] [Test] Create `backend/tests/test_event_handlers.py` with handler unit tests
- [x] [009-054] [P1] [Test] Test idempotency - process same event twice, verify single task created
- [x] [009-055] [P1] [Test] Test fire-and-forget - mock Dapr unavailable, verify task CRUD still succeeds
- [ ] [009-056] [P2] [Test] Integration test: Full event flow from task create to recurring instance

---

## Phase 10: Documentation & Deployment

- [ ] [009-057] [P2] [Docs] Document event catalog with all event types and payloads
- [ ] [009-058] [P2] [Docs] Update quickstart.md with local Kafka setup (docker-compose)
- [ ] [009-059] [P2] [Docs] Document subscription handler endpoints
- [ ] [009-060] [P2] [Deploy] Add Dapr annotations to backend deployment (dapr.io/enabled, app-id, app-port)
- [ ] [009-061] [P2] [Deploy] Create docker-compose.kafka.yml for local development

---

## Summary

| Phase | Tasks | Priority |
|-------|-------|----------|
| Setup & Infrastructure | 6 | P0 |
| Foundation | 7 | P1 |
| Story 1 - Task Events | 6 | P1 |
| Story 2 - Recurring Tasks | 8 | P1 |
| Story 3 - Reminders | 9 | P2 |
| Story 4 - Analytics | 4 | P3 |
| Error Handling | 8 | P1 |
| Resiliency Config | 3 | P1 |
| Testing | 5 | P1-P2 |
| Docs & Deploy | 5 | P2 |
| **Total** | **61** | |

### Clarifications Applied (2025-12-27)

- **DLQ Handling**: Alert-only (generate alert for ops team, manual review required)

---

## Acceptance Checklist

- [ ] All P1 tasks completed and tested
- [ ] Events published within 100ms of operation completion
- [ ] Recurring task next instance created within 60 seconds of completion
- [ ] 3 retries with exponential backoff before dead letter queue
- [ ] Handlers are idempotent (duplicate events produce same result)
- [ ] Fire-and-forget pattern - task operations succeed even if Kafka unavailable
- [ ] user_id as partition key ensures per-user event ordering
