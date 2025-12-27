# Dapr State Store API Contract

**Feature**: 008-dapr-state-chatbot
**Date**: 2025-12-25

## State Store Operations

### Get State

Retrieve conversation state for a user's conversation.

```http
GET http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore/{key}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| key | string | State key: `chat:{user_id}:{conversation_id}` |

**Response 200 OK**:
```json
{
  "conversation_id": "conv-001",
  "user_id": "user-abc123",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:15:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Add task: Buy groceries",
      "timestamp": "2025-12-25T10:00:00Z",
      "tool_calls": null
    },
    {
      "role": "assistant",
      "content": "I've added 'Buy groceries' to your task list.",
      "timestamp": "2025-12-25T10:00:02Z",
      "tool_calls": [
        {
          "tool": "add_task",
          "parameters": {"title": "Buy groceries"},
          "result": {"task_id": 42}
        }
      ]
    }
  ]
}
```

**Response 204 No Content**: Key not found (empty state)

---

### Save State

Save or update conversation state.

```http
POST http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore
Content-Type: application/json
```

**Request Body**:
```json
[
  {
    "key": "chat:user-abc123:conv-001",
    "value": {
      "conversation_id": "conv-001",
      "user_id": "user-abc123",
      "created_at": "2025-12-25T10:00:00Z",
      "updated_at": "2025-12-25T10:15:00Z",
      "messages": [...]
    },
    "metadata": {
      "ttlInSeconds": "2592000"
    }
  }
]
```

**Response 204 No Content**: State saved successfully

**Response 500 Internal Server Error**: State store unavailable

---

### Delete State

Delete conversation state (clear conversation).

```http
DELETE http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore/{key}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| key | string | State key: `chat:{user_id}:{conversation_id}` |

**Response 204 No Content**: State deleted successfully

---

## Application API (Unchanged)

The existing chat API contract remains unchanged. Backend internally uses Dapr State Store instead of direct DB queries.

### POST /api/{user_id}/chat

Send a message to the AI chatbot.

**Request**:
```json
{
  "message": "Add task: Buy groceries",
  "conversation_id": 1
}
```

**Response 200 OK**:
```json
{
  "reply": "I've added 'Buy groceries' to your task list.",
  "conversation_id": 1,
  "tool_calls": [...],
  "timestamp": "2025-12-25T10:00:02Z"
}
```

**Response Headers** (when degraded mode):
```
X-Chat-Degraded: true
```

---

## State Key Format

```
chat:{user_id}:{conversation_id}

Examples:
- chat:user-abc123:conv-001
- chat:user-abc123:conv-002
- chat:user-xyz789:conv-001
```

**Validation Rules**:
- user_id: Must match authenticated JWT user
- conversation_id: Alphanumeric, max 50 characters

---

## State Payload Schema

### ConversationState

```python
class ConversationState(BaseModel):
    conversation_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageEntry]

class MessageEntry(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    tool_calls: Optional[List[ToolCallInfo]] = None

class ToolCallInfo(BaseModel):
    tool: str
    parameters: dict
    result: dict
```

---

## Error Responses

| Status | Meaning | Action |
|--------|---------|--------|
| 204 | Success (no body) | Continue |
| 400 | Bad request | Fix request format |
| 403 | Forbidden | User ID mismatch |
| 500 | State store error | Degraded mode |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| DAPR_HTTP_PORT | 3500 | Dapr sidecar HTTP port |
| CHAT_MESSAGE_WINDOW | 50 | Messages to load for context |
| CHAT_MAX_MESSAGES | 200 | Max messages before truncation |
| CHAT_STATE_TTL | 2592000 | State TTL in seconds (30 days) |
