# Implementation Plan: Dapr Pub/Sub Event System

**Branch**: `009-dapr-pubsub-events` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-dapr-pubsub-events/spec.md`

## Summary

Implement event-driven architecture using Dapr Pub/Sub for task operations. Task CRUD operations will publish domain events that trigger automated workflows like recurring task scheduling and reminders. Services communicate asynchronously through Kafka-backed Pub/Sub, enabling loose coupling and scalability.

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript/Node.js 20+ (Frontend)
**Primary Dependencies**: FastAPI, httpx, Pydantic, CloudEvents
**Message Broker**: Kafka (via Strimzi Operator or managed service)
**Dapr Component**: kafka-pubsub
**Testing**: pytest, pytest-asyncio
**Target Platform**: Kubernetes (Cloud - DigitalOcean DOKS/Azure AKS/GKE)
**Project Type**: Web application (Backend API)
**Performance Goals**: Events published <100ms, 1000 events/minute, handler processing <500ms
**Constraints**: 3 retries with exponential backoff, user_id as partition key
**Scale/Scope**: Multi-user, event-driven workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Spec-Driven Development | ✅ PASS | Event schemas documented in spec |
| VIII. User Isolation | ✅ PASS | user_id in all event payloads |
| XXII. Event-Driven Architecture | ✅ PASS | Core implementation of this principle |
| XXIII. Sidecar Pattern with Dapr | ✅ PASS | All pub/sub via Dapr HTTP API |
| XXIV. Infrastructure Independence | ✅ PASS | No direct Kafka client, uses Dapr |
| XXVI. Advanced Task Management | ✅ PASS | Recurring tasks via events |

**Gate Result**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/009-dapr-pubsub-events/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── event-catalog.md
│   └── subscription-handlers.md
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── events/                     # NEW: Event system
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic event models
│   │   ├── publisher.py            # Event publishing utilities
│   │   └── handlers.py             # Event subscription handlers
│   ├── routers/
│   │   ├── tasks.py                # MODIFY: Add event publishing
│   │   └── events.py               # NEW: Dapr subscription endpoint
│   └── services/
│       └── recurring_tasks.py      # NEW: Recurring task logic
├── tests/
│   ├── test_event_publisher.py     # NEW
│   └── test_event_handlers.py      # NEW

k8s/
├── dapr-components/
│   └── kafka-pubsub.yaml           # NEW: Kafka Pub/Sub component
├── kafka/
│   └── strimzi/                    # Kafka deployment manifests
│       ├── kafka-cluster.yaml
│       └── kafka-topics.yaml
```

**Structure Decision**: Web application with new events module. Event handlers in `backend/app/events/`. Kafka configuration in `k8s/kafka/`.

## Architecture

### Event Flow Diagram

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User      │     │    Backend      │     │   Dapr Sidecar  │
│   Action    │────▶│    (FastAPI)    │────▶│   (localhost)   │
└─────────────┘     └─────────────────┘     └────────┬────────┘
                                                     │
                                                     ▼
                           ┌─────────────────────────────────────┐
                           │           Kafka (Strimzi)           │
                           │                                     │
                           │  Topics: tasks, reminders           │
                           └─────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
          │ Recurring Task  │   │   Reminder      │   │   Analytics     │
          │    Handler      │   │   Handler       │   │   Handler       │
          └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Event Publishing Pattern

```python
# backend/app/events/publisher.py
import httpx
import os
from datetime import datetime

DAPR_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event_type: str, data: dict, user_id: str):
    """Publish event via Dapr Pub/Sub"""
    event = {
        "specversion": "1.0",
        "type": event_type,
        "source": "todo-backend",
        "id": str(uuid.uuid4()),
        "time": datetime.utcnow().isoformat() + "Z",
        "partitionkey": user_id,  # Kafka partition key
        "data": {
            "user_id": user_id,
            **data
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"http://localhost:{DAPR_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event,
                headers={"Content-Type": "application/cloudevents+json"}
            )
        except Exception as e:
            # Fire-and-forget: log but don't fail user request
            logger.error(f"Failed to publish event: {e}")
```

### Event Subscription Pattern

```python
# backend/app/routers/events.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """Register Dapr subscriptions"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "tasks",
            "route": "/api/events/tasks"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/api/events/reminders"
        }
    ]

@router.post("/api/events/tasks")
async def handle_task_event(event: CloudEvent):
    """Process task events (idempotent)"""
    if event.type == "task.completed":
        await handle_task_completed(event.data)
    return {"status": "ok"}
```

## Event Catalog

| Event Type | Topic | Trigger | Publisher |
|------------|-------|---------|-----------|
| task.created | tasks | POST /tasks | tasks.py |
| task.updated | tasks | PATCH /tasks/{id} | tasks.py |
| task.completed | tasks | Toggle complete | tasks.py |
| task.deleted | tasks | DELETE /tasks/{id} | tasks.py |
| reminder.scheduled | reminders | Subscriber | handlers.py |
| reminder.triggered | reminders | Dapr Jobs | handlers.py |

## Retry Policy

| Parameter | Value |
|-----------|-------|
| Max Retries | 3 |
| Initial Delay | 1 second |
| Backoff Multiplier | 2x |
| Max Delay | 4 seconds |
| Dead Letter | After 3 failures |
| DLQ Handling | Alert-only (manual review) |
| DLQ Retention | 30 days |

## Complexity Tracking

No constitution violations. All changes align with Phase V principles.

## Dependencies

- Dapr runtime with Pub/Sub component
- Kafka (Strimzi Operator or managed)
- Advanced Task Fields (007) implemented
- Dapr State Store (008) for stateful handlers

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Event publishing fails | Fire-and-forget pattern, log errors |
| Handler processing fails | 3 retries with exponential backoff |
| Kafka unavailable | Events queued in Dapr, retry on recovery |
| Duplicate events | Idempotent handlers |
| Infinite event loops | Prevent recursive event triggers |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Deploy Kafka via Strimzi
3. Configure Dapr Pub/Sub component
4. Implement event publisher
5. Add event publishing to task CRUD
6. Implement recurring task handler
7. Test end-to-end event flow
