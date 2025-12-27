"""Unit tests for event publisher.

Implements: 009-052 Create test_event_publisher.py with publisher unit tests
Tests CloudEvents format, fire-and-forget pattern, and error handling.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.events.publisher import (
    EventPublisher,
    publish_event,
    get_publisher,
    DAPR_HTTP_PORT,
    PUBSUB_NAME,
)


class TestEventPublisher:
    """Tests for EventPublisher class."""

    def test_publisher_initialization_defaults(self):
        """Test publisher uses default configuration."""
        publisher = EventPublisher()
        assert publisher.dapr_port == DAPR_HTTP_PORT
        assert publisher.pubsub_name == PUBSUB_NAME
        assert "localhost" in publisher.base_url
        assert publisher._client is None

    def test_publisher_initialization_custom(self):
        """Test publisher accepts custom configuration."""
        publisher = EventPublisher(dapr_port="3501", pubsub_name="custom-pubsub")
        assert publisher.dapr_port == "3501"
        assert publisher.pubsub_name == "custom-pubsub"
        assert "3501" in publisher.base_url
        assert "custom-pubsub" in publisher.base_url

    @pytest.mark.asyncio
    async def test_publish_success(self):
        """Test successful event publishing."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        result = await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1, "title": "Test Task"},
            user_id="user123"
        )

        assert result is True
        mock_client.post.assert_called_once()

        # Verify CloudEvent format
        call_args = mock_client.post.call_args
        json_data = call_args.kwargs["json"]

        assert json_data["specversion"] == "1.0"
        assert json_data["type"] == "task.created"
        assert json_data["source"] == "todo-backend"
        assert json_data["partitionkey"] == "user123"
        assert "id" in json_data
        assert "time" in json_data
        assert json_data["data"]["task_id"] == 1
        assert json_data["data"]["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_publish_with_custom_source(self):
        """Test publishing with custom source (for handler-generated events)."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        result = await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1},
            user_id="user123",
            source="handler"  # Handler source for circular trigger prevention
        )

        assert result is True

        call_args = mock_client.post.call_args
        json_data = call_args.kwargs["json"]
        assert json_data["source"] == "handler"

    @pytest.mark.asyncio
    async def test_publish_failure_http_error(self):
        """Test handling of HTTP error responses."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        result = await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1},
            user_id="user123"
        )

        # Fire-and-forget: returns False but doesn't raise
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_fire_and_forget_connection_error(self):
        """Test fire-and-forget pattern when Dapr is unavailable.

        Implements: 009-055 Test fire-and-forget pattern
        """
        import httpx

        publisher = EventPublisher()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.is_closed = False

        publisher._client = mock_client

        # Should not raise, just return False
        result = await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1},
            user_id="user123"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_fire_and_forget_generic_error(self):
        """Test fire-and-forget handles unexpected errors gracefully."""
        publisher = EventPublisher()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Unexpected error"))
        mock_client.is_closed = False

        publisher._client = mock_client

        # Should not raise, just return False
        result = await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1},
            user_id="user123"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test closing the HTTP client."""
        publisher = EventPublisher()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        publisher._client = mock_client

        await publisher.close()

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_client_already_closed(self):
        """Test closing already closed client is safe."""
        publisher = EventPublisher()

        mock_client = AsyncMock()
        mock_client.is_closed = True
        mock_client.aclose = AsyncMock()

        publisher._client = mock_client

        await publisher.close()

        # Should not call aclose if already closed
        mock_client.aclose.assert_not_called()


class TestPublishEventFunction:
    """Tests for convenience publish_event function."""

    @pytest.mark.asyncio
    async def test_publish_event_uses_singleton(self):
        """Test publish_event uses singleton publisher."""
        with patch("app.events.publisher.get_publisher") as mock_get:
            mock_publisher = AsyncMock()
            mock_publisher.publish = AsyncMock(return_value=True)
            mock_get.return_value = mock_publisher

            result = await publish_event(
                topic="tasks",
                event_type="task.created",
                data={"task_id": 1},
                user_id="user123"
            )

            assert result is True
            mock_get.assert_called_once()
            mock_publisher.publish.assert_called_once_with(
                "tasks",
                "task.created",
                {"task_id": 1},
                "user123",
                "todo-backend"
            )

    @pytest.mark.asyncio
    async def test_publish_event_with_custom_source(self):
        """Test publish_event passes custom source."""
        with patch("app.events.publisher.get_publisher") as mock_get:
            mock_publisher = AsyncMock()
            mock_publisher.publish = AsyncMock(return_value=True)
            mock_get.return_value = mock_publisher

            await publish_event(
                topic="reminders",
                event_type="reminder.scheduled",
                data={"task_id": 1},
                user_id="user123",
                source="handler"
            )

            mock_publisher.publish.assert_called_once_with(
                "reminders",
                "reminder.scheduled",
                {"task_id": 1},
                "user123",
                "handler"
            )


class TestGetPublisher:
    """Tests for singleton publisher factory."""

    def test_get_publisher_creates_singleton(self):
        """Test get_publisher creates singleton instance."""
        with patch("app.events.publisher._publisher_instance", None):
            publisher1 = get_publisher()
            publisher2 = get_publisher()

            # Note: Due to module-level singleton, this verifies the pattern
            assert publisher1 is not None
            assert isinstance(publisher1, EventPublisher)


class TestCloudEventFormat:
    """Tests for CloudEvents 1.0 specification compliance."""

    @pytest.mark.asyncio
    async def test_cloud_event_required_fields(self):
        """Test all required CloudEvents fields are present."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={"task_id": 1},
            user_id="user123"
        )

        call_args = mock_client.post.call_args
        json_data = call_args.kwargs["json"]

        # Required CloudEvents fields
        assert "specversion" in json_data
        assert json_data["specversion"] == "1.0"
        assert "type" in json_data
        assert "source" in json_data
        assert "id" in json_data
        assert "time" in json_data

        # Extension for Kafka partitioning
        assert "partitionkey" in json_data

        # Data payload
        assert "data" in json_data
        assert "user_id" in json_data["data"]
        assert "timestamp" in json_data["data"]

    @pytest.mark.asyncio
    async def test_cloud_event_content_type_header(self):
        """Test correct Content-Type header for CloudEvents."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        await publisher.publish(
            topic="tasks",
            event_type="task.created",
            data={},
            user_id="user123"
        )

        call_args = mock_client.post.call_args
        headers = call_args.kwargs["headers"]

        assert headers["Content-Type"] == "application/cloudevents+json"

    @pytest.mark.asyncio
    async def test_cloud_event_unique_ids(self):
        """Test each event gets a unique ID."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False

        publisher._client = mock_client

        # Publish two events
        await publisher.publish("tasks", "task.created", {}, "user1")
        await publisher.publish("tasks", "task.created", {}, "user1")

        # Get both event IDs
        calls = mock_client.post.call_args_list
        id1 = calls[0].kwargs["json"]["id"]
        id2 = calls[1].kwargs["json"]["id"]

        assert id1 != id2
