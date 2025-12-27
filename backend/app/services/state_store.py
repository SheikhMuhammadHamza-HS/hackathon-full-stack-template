"""Dapr State Store service for conversation history management.

Implements: 008-dapr-state-chatbot spec
Uses Dapr State Store API instead of direct SQL queries for conversation state.

State Key Pattern: chat:{user_id}:{conversation_id}
"""
import logging
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

import httpx

logger = logging.getLogger(__name__)

# Configuration from environment
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE_NAME", "statestore")
MESSAGE_WINDOW_SIZE = int(os.getenv("MESSAGE_WINDOW_SIZE", "50"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "200"))


class DaprStateStore:
    """Dapr State Store client for conversation state management.

    Provides async methods for CRUD operations on conversation state
    via Dapr HTTP API. Implements degraded mode when Dapr unavailable.

    Attributes:
        base_url: Dapr HTTP endpoint URL
        store_name: Name of the state store component
        _degraded_mode: Flag indicating if operating without state persistence
    """

    def __init__(self, dapr_port: Optional[str] = None, store_name: Optional[str] = None):
        """Initialize Dapr State Store client.

        Args:
            dapr_port: Dapr HTTP port (default from DAPR_HTTP_PORT env)
            store_name: State store component name (default from DAPR_STATE_STORE_NAME env)
        """
        self.dapr_port = dapr_port or DAPR_HTTP_PORT
        self.store_name = store_name or STATE_STORE_NAME
        self.base_url = f"http://localhost:{self.dapr_port}/v1.0/state/{self.store_name}"
        self._degraded_mode = False
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @property
    def is_degraded(self) -> bool:
        """Check if operating in degraded mode (no state persistence)."""
        return self._degraded_mode

    @staticmethod
    def generate_state_key(user_id: str, conversation_id: str) -> str:
        """Generate state key following pattern: chat:{user_id}:{conversation_id}

        Args:
            user_id: User identifier from JWT
            conversation_id: Conversation identifier

        Returns:
            Formatted state key string
        """
        return f"chat:{user_id}:{conversation_id}"

    @staticmethod
    def validate_state_key(key: str, expected_user_id: str) -> bool:
        """Validate state key format and user ownership.

        Args:
            key: State key to validate
            expected_user_id: User ID from JWT to match

        Returns:
            True if key is valid and belongs to user
        """
        if not key.startswith("chat:"):
            return False

        parts = key.split(":")
        if len(parts) != 3:
            return False

        _, user_id, _ = parts
        return user_id == expected_user_id

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation state from Dapr State Store.

        Args:
            key: State key (chat:{user_id}:{conversation_id})

        Returns:
            Conversation state dict or None if not found
        """
        start_time = time.time()

        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/{key}")

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"State GET {key}: {response.status_code} ({elapsed:.2f}ms)")

            if response.status_code == 200:
                self._degraded_mode = False
                # Dapr returns the value directly, not wrapped
                data = response.json()
                return data if data else None
            elif response.status_code == 204:
                # No content - key doesn't exist
                return None
            else:
                logger.warning(f"State GET failed: {response.status_code} - {response.text}")
                return None

        except httpx.ConnectError as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"Dapr connection failed ({elapsed:.2f}ms): {e}")
            self._degraded_mode = True
            return None
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"State GET error ({elapsed:.2f}ms): {e}")
            return None

    async def save_state(self, key: str, value: Dict[str, Any]) -> bool:
        """Save conversation state to Dapr State Store.

        Args:
            key: State key (chat:{user_id}:{conversation_id})
            value: Conversation state dict to save

        Returns:
            True if save successful, False otherwise
        """
        start_time = time.time()

        try:
            client = await self._get_client()

            # Dapr expects array of state items
            payload = [
                {
                    "key": key,
                    "value": value
                }
            ]

            response = await client.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"State SAVE {key}: {response.status_code} ({elapsed:.2f}ms)")

            if response.status_code in (200, 201, 204):
                self._degraded_mode = False
                return True
            else:
                logger.warning(f"State SAVE failed: {response.status_code} - {response.text}")
                return False

        except httpx.ConnectError as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"Dapr connection failed ({elapsed:.2f}ms): {e}")
            self._degraded_mode = True
            return False
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"State SAVE error ({elapsed:.2f}ms): {e}")
            return False

    async def delete_state(self, key: str) -> bool:
        """Delete conversation state from Dapr State Store.

        Args:
            key: State key (chat:{user_id}:{conversation_id})

        Returns:
            True if delete successful, False otherwise
        """
        start_time = time.time()

        try:
            client = await self._get_client()
            response = await client.delete(f"{self.base_url}/{key}")

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"State DELETE {key}: {response.status_code} ({elapsed:.2f}ms)")

            if response.status_code in (200, 204):
                self._degraded_mode = False
                return True
            else:
                logger.warning(f"State DELETE failed: {response.status_code} - {response.text}")
                return False

        except httpx.ConnectError as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"Dapr connection failed ({elapsed:.2f}ms): {e}")
            self._degraded_mode = True
            return False
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"State DELETE error ({elapsed:.2f}ms): {e}")
            return False

    async def health_check(self) -> bool:
        """Check if Dapr sidecar is healthy and accessible.

        Returns:
            True if Dapr is healthy, False otherwise
        """
        try:
            client = await self._get_client()
            health_url = f"http://localhost:{self.dapr_port}/v1.0/healthz"
            response = await client.get(health_url, timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False


# Conversation state helper functions

def create_empty_conversation_state(
    user_id: str,
    conversation_id: str
) -> Dict[str, Any]:
    """Create a new empty conversation state structure.

    Args:
        user_id: User identifier
        conversation_id: Conversation identifier

    Returns:
        Empty conversation state dict
    """
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }


def add_message_to_state(
    state: Dict[str, Any],
    role: str,
    content: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Add a message to conversation state with automatic truncation.

    Args:
        state: Current conversation state
        role: Message role ('user' or 'assistant')
        content: Message content
        tool_calls: Optional list of tool call info (for assistant messages)

    Returns:
        Updated conversation state
    """
    now = datetime.utcnow().isoformat() + "Z"

    message = {
        "role": role,
        "content": content,
        "timestamp": now
    }

    if tool_calls:
        message["tool_calls"] = tool_calls

    state["messages"].append(message)
    state["updated_at"] = now

    # Truncate if exceeds MAX_MESSAGES (keep most recent)
    if len(state["messages"]) > MAX_MESSAGES:
        state["messages"] = state["messages"][-MAX_MESSAGES:]
        logger.info(f"Truncated messages to {MAX_MESSAGES} (max limit)")

    return state


def get_recent_messages(
    state: Dict[str, Any],
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get recent messages from state within window limit.

    Args:
        state: Conversation state
        limit: Max messages to return (default MESSAGE_WINDOW_SIZE)

    Returns:
        List of recent messages
    """
    window = limit or MESSAGE_WINDOW_SIZE
    messages = state.get("messages", [])
    return messages[-window:] if len(messages) > window else messages


# Singleton instance for dependency injection
_state_store_instance: Optional[DaprStateStore] = None


def get_state_store() -> DaprStateStore:
    """Get or create singleton DaprStateStore instance.

    Returns:
        DaprStateStore singleton instance
    """
    global _state_store_instance
    if _state_store_instance is None:
        _state_store_instance = DaprStateStore()
    return _state_store_instance
