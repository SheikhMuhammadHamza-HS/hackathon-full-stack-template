"""Event system module for Dapr Pub/Sub integration.

Implements: 009-dapr-pubsub-events spec
Provides event publishing and subscription handling for task operations.
"""
from app.events.publisher import publish_event, EventPublisher
from app.events.schemas import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    ReminderScheduledEvent,
    ReminderTriggeredEvent
)
from app.events.handlers import (
    CircuitBreaker,
    get_circuit_breaker,
    with_circuit_breaker
)

__all__ = [
    "publish_event",
    "EventPublisher",
    "TaskCreatedEvent",
    "TaskUpdatedEvent",
    "TaskCompletedEvent",
    "TaskDeletedEvent",
    "ReminderScheduledEvent",
    "ReminderTriggeredEvent",
    "CircuitBreaker",
    "get_circuit_breaker",
    "with_circuit_breaker"
]
