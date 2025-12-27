"""Unit tests for event handlers.

Implements: 009-053 Create test_event_handlers.py with handler unit tests
Implements: 009-054 Test idempotency - process same event twice, verify single action
Tests event handling, idempotency, circular trigger prevention, and circuit breaker.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone

from app.events.handlers import (
    handle_task_created,
    handle_task_updated,
    handle_task_completed,
    handle_task_deleted,
    handle_reminder_scheduled,
    handle_reminder_triggered,
    calculate_next_due_date,
    CircuitBreaker,
    get_circuit_breaker,
    with_circuit_breaker,
    _is_event_processed,
    _mark_event_processed,
    _is_handler_generated,
    _validate_event_data,
    log_dlq_alert,
    HANDLER_SOURCE,
    BACKEND_SOURCE,
    _processed_events,
)


class TestCalculateNextDueDate:
    """Tests for recurring task due date calculation."""

    def test_daily_interval(self):
        """Test daily recurring interval adds 1 day."""
        current = datetime(2025, 1, 15, 10, 0, 0)
        next_due = calculate_next_due_date(current, "daily")
        assert next_due == datetime(2025, 1, 16, 10, 0, 0)

    def test_weekly_interval(self):
        """Test weekly recurring interval adds 7 days."""
        current = datetime(2025, 1, 15, 10, 0, 0)
        next_due = calculate_next_due_date(current, "weekly")
        assert next_due == datetime(2025, 1, 22, 10, 0, 0)

    def test_monthly_interval(self):
        """Test monthly recurring interval adds 1 month."""
        current = datetime(2025, 1, 15, 10, 0, 0)
        next_due = calculate_next_due_date(current, "monthly")
        assert next_due == datetime(2025, 2, 15, 10, 0, 0)

    def test_monthly_interval_end_of_month(self):
        """Test monthly interval handles month end dates."""
        current = datetime(2025, 1, 31, 10, 0, 0)
        next_due = calculate_next_due_date(current, "monthly")
        # February doesn't have 31 days, dateutil handles this
        assert next_due.month == 2

    def test_unknown_interval_defaults_to_daily(self):
        """Test unknown interval defaults to daily."""
        current = datetime(2025, 1, 15, 10, 0, 0)
        next_due = calculate_next_due_date(current, "unknown")
        assert next_due == datetime(2025, 1, 16, 10, 0, 0)


class TestIdempotency:
    """Tests for event processing idempotency.

    Implements: 009-054 Test idempotency - process same event twice
    """

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    def test_event_not_processed_initially(self):
        """Test new event is not marked as processed."""
        assert not _is_event_processed("new-event-id")

    def test_mark_event_processed(self):
        """Test event can be marked as processed."""
        _mark_event_processed("test-event-1")
        assert _is_event_processed("test-event-1")

    def test_processed_event_detected(self):
        """Test duplicate event is detected."""
        _mark_event_processed("duplicate-event")
        assert _is_event_processed("duplicate-event")

    @pytest.mark.asyncio
    async def test_handler_skips_duplicate_event(self):
        """Test handler skips already processed events."""
        event_id = "task-created-123"
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "title": "Test Task"
        }

        # Process first time
        with patch("app.events.handlers.publish_event", new_callable=AsyncMock):
            result1 = await handle_task_created(event_data, event_id)
            assert result1["status"] == "ok"

        # Process second time - should skip
        result2 = await handle_task_created(event_data, event_id)
        assert result2["status"] == "skipped"
        assert result2["reason"] == "duplicate"

    @pytest.mark.asyncio
    async def test_idempotency_all_handlers(self):
        """Test all handlers implement idempotency."""
        handlers = [
            (handle_task_created, {"task_id": 1, "user_id": "u1"}),
            (handle_task_updated, {"task_id": 1, "user_id": "u1", "changed_fields": []}),
            (handle_task_completed, {"task_id": 1, "user_id": "u1", "completed": True}),
            (handle_task_deleted, {"task_id": 1, "user_id": "u1"}),
            (handle_reminder_scheduled, {"task_id": 1, "remind_at": "2025-01-15T10:00:00Z"}),
            (handle_reminder_triggered, {"task_id": 1, "user_id": "u1", "task_title": "Test", "due_date": "2025-01-15"}),
        ]

        for handler, data in handlers:
            event_id = f"idempotency-test-{handler.__name__}"

            with patch("app.events.handlers.publish_event", new_callable=AsyncMock):
                # First call
                result1 = await handler(data, event_id)

                # Second call should skip
                result2 = await handler(data, event_id)

                assert result2["status"] == "skipped", f"{handler.__name__} failed idempotency"
                assert result2["reason"] == "duplicate"


class TestCircularTriggerPrevention:
    """Tests for preventing circular event triggers."""

    def test_handler_source_detected(self):
        """Test handler-generated events are detected."""
        assert _is_handler_generated(HANDLER_SOURCE)
        assert _is_handler_generated("handler")

    def test_backend_source_not_handler(self):
        """Test backend source is not detected as handler."""
        assert not _is_handler_generated(BACKEND_SOURCE)
        assert not _is_handler_generated("todo-backend")

    def test_other_sources_not_handler(self):
        """Test other sources are not detected as handler."""
        assert not _is_handler_generated("external-service")
        assert not _is_handler_generated("frontend")


class TestEventValidation:
    """Tests for event data validation."""

    def test_validate_with_all_fields(self):
        """Test validation passes with all required fields."""
        data = {"task_id": 1, "user_id": "user123"}
        assert _validate_event_data(data, ["task_id", "user_id"])

    def test_validate_missing_field(self):
        """Test validation fails with missing field."""
        data = {"task_id": 1}
        assert not _validate_event_data(data, ["task_id", "user_id"])

    def test_validate_empty_required_list(self):
        """Test validation passes with no required fields."""
        data = {}
        assert _validate_event_data(data, [])


class TestDLQAlertLogging:
    """Tests for dead letter queue alert logging."""

    def test_log_dlq_alert(self, caplog):
        """Test DLQ alert is logged with correct format."""
        import logging
        caplog.set_level(logging.ERROR)

        log_dlq_alert(
            event_id="dlq-event-123",
            event_type="task.created",
            error_message="Processing failed after retries"
        )

        assert "DLQ ALERT" in caplog.text
        assert "dlq-event-123" in caplog.text
        assert "task.created" in caplog.text
        assert "Manual review required" in caplog.text


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""

    def test_initial_state_is_closed(self):
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(name="test")
        assert cb.state == CircuitBreaker.CLOSED
        assert cb.failure_count == 0

    def test_stays_closed_under_threshold(self):
        """Test circuit stays closed below failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, name="test")

        cb.record_failure()
        assert cb.state == CircuitBreaker.CLOSED
        assert cb.failure_count == 1

        cb.record_failure()
        assert cb.state == CircuitBreaker.CLOSED
        assert cb.failure_count == 2

    def test_opens_at_threshold(self):
        """Test circuit opens at failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, name="test")

        for _ in range(3):
            cb.record_failure()

        assert cb.state == CircuitBreaker.OPEN
        assert cb.is_open()

    def test_success_resets_failure_count(self):
        """Test success resets failure count in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3, name="test")

        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 2

        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitBreaker.CLOSED

    def test_half_open_after_timeout(self):
        """Test circuit enters HALF_OPEN after reset timeout."""
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.001, name="test")

        cb.record_failure()
        assert cb.state == CircuitBreaker.OPEN

        # Wait for reset timeout
        import time
        time.sleep(0.01)

        # Should allow request (enters HALF_OPEN)
        assert not cb.is_open()
        assert cb.state == CircuitBreaker.HALF_OPEN

    def test_half_open_success_closes_circuit(self):
        """Test success in HALF_OPEN state closes circuit."""
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.001, name="test")

        cb.record_failure()
        import time
        time.sleep(0.01)

        # Trigger half-open check
        cb.is_open()
        assert cb.state == CircuitBreaker.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitBreaker.CLOSED
        assert cb.failure_count == 0

    def test_half_open_failure_opens_circuit(self):
        """Test failure in HALF_OPEN state reopens circuit."""
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.001, name="test")

        cb.record_failure()
        import time
        time.sleep(0.01)

        # Trigger half-open check
        cb.is_open()
        assert cb.state == CircuitBreaker.HALF_OPEN

        cb.record_failure()
        assert cb.state == CircuitBreaker.OPEN

    def test_get_circuit_breaker_creates_singleton(self):
        """Test get_circuit_breaker creates/reuses instances by name."""
        cb1 = get_circuit_breaker("service-a")
        cb2 = get_circuit_breaker("service-a")
        cb3 = get_circuit_breaker("service-b")

        assert cb1 is cb2
        assert cb1 is not cb3

    @pytest.mark.asyncio
    async def test_decorator_allows_call_when_closed(self):
        """Test decorator allows calls when circuit is closed."""
        @with_circuit_breaker("test-decorator-closed")
        async def test_func():
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_decorator_blocks_call_when_open(self):
        """Test decorator blocks calls when circuit is open."""
        breaker = get_circuit_breaker("test-decorator-open")
        # Force circuit open
        for _ in range(5):
            breaker.record_failure()

        @with_circuit_breaker("test-decorator-open")
        async def test_func():
            return "success"

        result = await test_func()
        assert result is None  # Call blocked

    @pytest.mark.asyncio
    async def test_decorator_records_success(self):
        """Test decorator records success."""
        breaker_name = "test-decorator-success"

        @with_circuit_breaker(breaker_name)
        async def test_func():
            return "success"

        await test_func()

        breaker = get_circuit_breaker(breaker_name)
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_decorator_records_failure(self):
        """Test decorator records failure and re-raises exception."""
        breaker_name = "test-decorator-failure"

        @with_circuit_breaker(breaker_name)
        async def test_func():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            await test_func()

        breaker = get_circuit_breaker(breaker_name)
        assert breaker.failure_count == 1


class TestHandleTaskCreated:
    """Tests for task.created event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_handles_task_without_due_date(self):
        """Test handler processes task without due date."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "title": "No Due Date Task"
        }

        with patch("app.events.handlers.publish_event", new_callable=AsyncMock) as mock_publish:
            result = await handle_task_created(event_data, "event-1")

        assert result["status"] == "ok"
        assert "reminder_scheduled" not in result.get("actions", [])
        mock_publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedules_reminder_for_future_due_date(self):
        """Test handler schedules reminder for task with future due date."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "title": "Future Task",
            "due_date": future_date
        }

        with patch("app.events.handlers.publish_event", new_callable=AsyncMock) as mock_publish:
            mock_publish.return_value = True
            result = await handle_task_created(event_data, "event-2")

        assert result["status"] == "ok"
        assert "reminder_scheduled" in result["actions"]
        mock_publish.assert_called_once()

        # Verify reminder event uses handler source
        call_args = mock_publish.call_args
        assert call_args.kwargs["source"] == HANDLER_SOURCE

    @pytest.mark.asyncio
    async def test_no_reminder_for_past_due_date(self):
        """Test handler doesn't schedule reminder for past due date."""
        past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "due_date": past_date
        }

        with patch("app.events.handlers.publish_event", new_callable=AsyncMock) as mock_publish:
            result = await handle_task_created(event_data, "event-3")

        assert result["status"] == "ok"
        assert "reminder_scheduled" not in result.get("actions", [])


class TestHandleTaskUpdated:
    """Tests for task.updated event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_reschedules_reminder_on_due_date_change(self):
        """Test handler reschedules reminder when due_date changes."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "changed_fields": ["due_date"],
            "due_date": future_date
        }

        with patch("app.events.handlers.publish_event", new_callable=AsyncMock) as mock_publish:
            mock_publish.return_value = True
            result = await handle_task_updated(event_data, "event-update-1")

        assert result["status"] == "ok"
        assert "reminder_rescheduled" in result["actions"]
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_action_for_non_due_date_changes(self):
        """Test handler takes no action for non-due_date changes."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "changed_fields": ["title", "priority"]
        }

        with patch("app.events.handlers.publish_event", new_callable=AsyncMock) as mock_publish:
            result = await handle_task_updated(event_data, "event-update-2")

        assert result["status"] == "ok"
        assert len(result.get("actions", [])) == 0
        mock_publish.assert_not_called()


class TestHandleTaskCompleted:
    """Tests for task.completed event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_no_action_for_non_recurring_task(self):
        """Test handler takes no action for non-recurring task."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "completed": True,
            "is_recurring": False
        }

        result = await handle_task_completed(event_data, "event-complete-1")

        assert result["status"] == "ok"
        assert "recurring_instance_created" not in result.get("actions", [])

    @pytest.mark.asyncio
    async def test_no_action_for_uncomplete(self):
        """Test handler takes no action when task is uncompleted."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "completed": False,
            "is_recurring": True,
            "recurring_interval": "daily"
        }

        result = await handle_task_completed(event_data, "event-uncomplete-1")

        assert result["status"] == "ok"
        assert "recurring_instance_created" not in result.get("actions", [])

    @pytest.mark.asyncio
    async def test_requires_session_for_recurring_task(self):
        """Test recurring task creation requires database session."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "completed": True,
            "is_recurring": True,
            "recurring_interval": "daily",
            "due_date": "2025-01-15T10:00:00Z"
        }

        # Without session, should not create recurring instance
        result = await handle_task_completed(event_data, "event-recurring-no-session")

        assert result["status"] == "ok"
        assert "recurring_instance_created" not in result.get("actions", [])


class TestHandleTaskDeleted:
    """Tests for task.deleted event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_cancels_reminders(self):
        """Test handler cancels reminders for deleted task."""
        event_data = {
            "task_id": 1,
            "user_id": "user123"
        }

        result = await handle_task_deleted(event_data, "event-delete-1")

        assert result["status"] == "ok"
        assert "reminders_cancelled" in result["actions"]


class TestHandleReminderScheduled:
    """Tests for reminder.scheduled event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_schedules_job(self):
        """Test handler schedules Dapr job."""
        event_data = {
            "task_id": 1,
            "remind_at": "2025-01-20T10:00:00Z"
        }

        result = await handle_reminder_scheduled(event_data, "event-remind-1")

        assert result["status"] == "ok"
        assert "job_scheduled" in result["actions"]


class TestHandleReminderTriggered:
    """Tests for reminder.triggered event handler."""

    def setup_method(self):
        """Clear processed events before each test."""
        _processed_events.clear()

    @pytest.mark.asyncio
    async def test_creates_notification(self):
        """Test handler creates in-app notification."""
        event_data = {
            "task_id": 1,
            "user_id": "user123",
            "task_title": "Important Task",
            "due_date": "2025-01-15T10:00:00Z"
        }

        result = await handle_reminder_triggered(event_data, "event-trigger-1")

        assert result["status"] == "ok"
        assert "notification_created" in result["actions"]
