# Research: Dapr State Store for Chatbot

**Feature**: 008-dapr-state-chatbot
**Date**: 2025-12-25
**Status**: Complete

## Research Questions

### 1. Dapr State Store API Best Practices

**Decision**: Use HTTP API directly with httpx async client

**Rationale**:
- Dapr Python SDK adds unnecessary dependency
- HTTP API is well-documented and stable
- httpx provides async support matching FastAPI patterns
- Simpler debugging (curl commands work directly)

**Alternatives Considered**:
- Dapr Python SDK: Adds dependency, less transparent
- requests library: Not async, would block FastAPI event loop
- aiohttp: Works but httpx is more modern and consistent with FastAPI

### 2. State Key Pattern Design

**Decision**: `chat:{user_id}:{conversation_id}`

**Rationale**:
- User ID first enables efficient key prefix queries if needed
- Conversation ID allows multiple conversations per user
- Colon separator is Dapr convention
- Keys are human-readable for debugging

**Alternatives Considered**:
- `{user_id}/{conversation_id}`: Slash can cause URL encoding issues
- UUID-only keys: Lose user context, harder to debug
- Hash of user+conversation: Loses readability

### 3. Conversation State Schema

**Decision**: Single JSON object containing messages array

**Rationale**:
- Atomic read/write of entire conversation
- No need for complex queries (just load all messages)
- Message window handled at application level (take last N)
- Timestamps in messages for ordering

**Schema**:
```json
{
  "conversation_id": "conv-001",
  "user_id": "user-abc123",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:15:00Z",
  "messages": [
    {
      "role": "user",
      "content": "...",
      "timestamp": "...",
      "tool_calls": null
    }
  ]
}
```

**Alternatives Considered**:
- One key per message: Requires multiple reads, complex ordering
- Separate metadata key: Adds complexity, two reads per operation

### 4. Degraded Mode Behavior

**Decision**: Chat continues without history when state store unavailable

**Rationale**:
- Better UX than complete failure
- User can still get AI assistance for new requests
- Warning banner informs user of limitation
- Aligns with graceful degradation principle

**Implementation**:
```python
try:
    history = await state_store.get_state(key)
except DaprStateStoreUnavailable:
    logger.warning(f"State store unavailable, proceeding without history")
    history = None
    show_degraded_warning = True
```

### 5. Message Window Strategy

**Decision**: Configurable window (default 50, max 200)

**Rationale**:
- 50 messages provides good context for most conversations
- 200 max prevents unbounded state growth
- OpenAI models have token limits, more messages = more tokens
- Configurable via environment variable for flexibility

**Implementation**:
```python
MESSAGE_WINDOW = int(os.getenv("CHAT_MESSAGE_WINDOW", "50"))
MAX_MESSAGES = 200

# When saving state
if len(messages) > MAX_MESSAGES:
    messages = messages[-MAX_MESSAGES:]  # Keep most recent
```

### 6. State Store Component Configuration

**Decision**: PostgreSQL-backed state store

**Rationale**:
- Reuses existing Neon PostgreSQL database
- No additional infrastructure (Redis, etc.)
- Consistent with Phase IV database strategy
- Dapr handles connection pooling

**Component YAML**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: database-credentials
      key: connection-string
```

### 7. Existing Data Migration

**Decision**: One-time migration script, then deprecate tables

**Rationale**:
- Clean break from old architecture
- No dual-write complexity
- Migration can be run during maintenance window
- Tables deprecated but not immediately dropped (rollback safety)

**Migration Steps**:
1. Create backup of conversations/messages tables
2. Run migration script to populate state store
3. Deploy new application version using state store
4. Verify functionality
5. Create Alembic migration to drop tables (after stability period)

### 8. Error Handling Strategy

**Decision**: Graceful degradation with logging

**Error Scenarios**:
| Error | Behavior |
|-------|----------|
| State store unavailable | Continue without history, show warning |
| State not found | Return empty state, create on first message |
| Malformed state data | Log error, return empty state |
| Save failure | Log error, don't fail user request |

## Technology Decisions Summary

| Area | Decision |
|------|----------|
| HTTP Client | httpx (async) |
| State Key | `chat:{user_id}:{conversation_id}` |
| State Schema | Single JSON with messages array |
| Failure Mode | Degraded (continue without history) |
| Message Limit | Window 50, Max 200 |
| Backend Store | PostgreSQL via Dapr |
| Migration | One-time script + table deprecation |
| Port Config | DAPR_HTTP_PORT env var (default 3500) |

## References

- [Dapr State Management API](https://docs.dapr.io/reference/api/state_api/)
- [Dapr PostgreSQL State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
- [OpenAI Agents SDK Context Management](https://openai.github.io/openai-agents-python/)
