# Feature Specification: Dapr State Store for Chatbot

**Feature Branch**: `008-dapr-state-chatbot`
**Created**: 2025-12-25
**Status**: Draft
**Phase**: V (Cloud Deployment & Event-Driven Architecture)
**Input**: Refactor Chatbot to use Dapr State Store API instead of direct SQL queries for conversation history management.

## Clarifications

### Session 2025-12-25

- Q: When Dapr State Store is unavailable, should chat still work without history or fail completely? → A: Chat works without history (degraded mode) - user sees warning message
- Q: What should be the absolute maximum messages stored per conversation before truncation? → A: 200 messages maximum
- Q: Should Dapr sidecar port be configurable or hardcoded? → A: Environment variable DAPR_HTTP_PORT with default 3500
- Q: What happens to existing conversations/messages database tables after migration? → A: Migrate existing data to state store, then deprecate tables

## Overview

Decouple the AI Chatbot's conversation history persistence from direct database queries by leveraging Dapr's State Store API. This enables portable, cloud-native state management with built-in consistency, caching, and multi-store support.

## User Scenarios & Testing

### User Story 1 - Seamless Chat Experience (Priority: P1)

Users interact with the AI chatbot and their conversation history persists across sessions without any change in user experience.

**Why P1**: Core functionality - users must not notice any behavioral changes after migration to Dapr State Store.

**Independent Test**: Start a new conversation, send 5 messages, close browser, reopen and continue the conversation with full context preserved.

**Acceptance Scenarios**:
1. **Given** a new user starts a chat, **When** they send a message, **Then** conversation state is saved and a conversation ID is returned
2. **Given** an existing conversation, **When** user sends another message, **Then** previous context is loaded and response is contextually aware
3. **Given** user closes browser mid-conversation, **When** they return with the same conversation ID, **Then** full history is available
4. **Given** user has multiple conversations, **When** they switch between them, **Then** each conversation maintains its own isolated state

---

### User Story 2 - Conversation State Consistency (Priority: P1)

System maintains conversation state reliably without data loss or corruption even under concurrent access.

**Why P1**: Data integrity is critical - losing conversation context breaks user trust.

**Independent Test**: Send 10 rapid messages in succession, verify all are stored in correct order.

**Acceptance Scenarios**:
1. **Given** rapid message submission, **When** 10 messages sent in 5 seconds, **Then** all messages stored in chronological order
2. **Given** concurrent chat requests, **When** user opens multiple tabs, **Then** each session sees consistent state
3. **Given** state store temporary unavailability, **When** it recovers, **Then** pending writes are persisted without data loss
4. **Given** malformed state data, **When** retrieved, **Then** system gracefully handles and logs error without crashing

---

### User Story 3 - Efficient State Retrieval (Priority: P2)

AI agent retrieves conversation history quickly to maintain responsive chat experience.

**Why P2**: Performance optimization - affects user experience but system works without it.

**Independent Test**: Load a conversation with 100 messages, verify response time is under 2 seconds.

**Acceptance Scenarios**:
1. **Given** conversation with 50 messages, **When** new message sent, **Then** context retrieved in under 1 second
2. **Given** conversation with 200+ messages, **When** context loaded, **Then** only recent N messages used (configurable window)
3. **Given** first message in new conversation, **When** no prior state exists, **Then** empty state returned without error

---

### User Story 4 - Secure State Isolation (Priority: P1)

Each user's conversation state is isolated and inaccessible to other users.

**Why P1**: Security requirement - user data must never leak to other users.

**Independent Test**: Attempt to access another user's conversation state, verify access denied.

**Acceptance Scenarios**:
1. **Given** User A's conversation, **When** User B attempts access with User A's conversation ID, **Then** access denied (403 or empty state)
2. **Given** state key pattern, **When** user_id mismatch detected, **Then** request rejected before state access
3. **Given** valid JWT token, **When** accessing own conversation, **Then** full access granted

---

### Edge Cases

- State store unavailable: Chat continues in degraded mode without history, user sees warning banner
- Conversation ID not found: Return empty conversation, create new state on first message
- State size exceeds 200 messages: Truncate oldest messages, preserve most recent 200
- Invalid state key format: Validation error before API call
- Concurrent state updates: Last-write-wins with optimistic concurrency
- State TTL expiration: Configurable retention (default: 30 days)

## Requirements

### Functional Requirements

- **FR-001**: System MUST save conversation state via Dapr State Store API
- **FR-002**: System MUST retrieve conversation state before each AI agent run
- **FR-003**: System MUST use state key pattern: `chat:{user_id}:{conversation_id}`
- **FR-004**: System MUST validate user_id in state key matches authenticated user
- **FR-005**: System MUST handle state store unavailability gracefully by operating in degraded mode (chat continues without history, user sees warning)
- **FR-006**: System MUST preserve message order in conversation history
- **FR-007**: System MUST support configurable message window (default: 50, max: 200 messages)
- **FR-008**: System MUST store both user and assistant messages with metadata
- **FR-009**: System MUST include tool_calls in assistant message metadata
- **FR-010**: System MUST support state TTL for automatic expiration
- **FR-011**: System MUST NOT expose direct database queries for chat state
- **FR-012**: System MUST maintain backward compatibility with existing chat API

### Key Entities

- **Conversation State**: JSON object containing message history, metadata, and timestamps
- **Message Entry**: Role (user/assistant), content, timestamp, optional tool_calls
- **State Key**: Composite key following Dapr naming pattern
- **State Metadata**: TTL, consistency mode, concurrency info

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can continue conversations across sessions with full context in under 2 seconds
- **SC-002**: 99.9% of state save operations complete successfully
- **SC-003**: State retrieval for 50-message conversations completes in under 500ms
- **SC-004**: Zero cross-user data leakage incidents
- **SC-005**: System handles 1000 concurrent chat sessions without degradation
- **SC-006**: State store switchover (e.g., PostgreSQL to Redis) requires zero code changes
- **SC-007**: 100% of existing chat functionality works without modification to API contract

## Assumptions

- Dapr sidecar is deployed alongside application pods
- PostgreSQL-backed state store component is configured
- Conversation history size typically under 100 messages
- Users authenticated via JWT with user_id claim
- Dapr State Store supports CRUD operations
- Network latency to Dapr sidecar is negligible (localhost)

## Dependencies

- Phase III AI Chatbot functional
- Dapr runtime installed on Kubernetes cluster
- State Store component configured (`statestore`)
- PostgreSQL database accessible from Dapr
- OpenAI Agents SDK integration complete

## Migration Strategy

- **Step 1**: Deploy Dapr State Store alongside existing DB tables
- **Step 2**: Run one-time migration script to copy existing conversations/messages to state store
- **Step 3**: Switch application to use Dapr State Store API exclusively
- **Step 4**: Deprecate and remove `conversations` and `messages` tables via Alembic migration

## Out of Scope

- State store component configuration (infrastructure concern)
- Multi-region state replication
- State encryption at rest (handled by state store)
- Real-time state synchronization across devices
- Conversation search/indexing
- State analytics/reporting

## Dapr Integration Patterns

### State Store Operations

| Operation | Dapr HTTP Route | Purpose |
|-----------|-----------------|---------|
| Save State | `POST http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore` | Persist conversation after each message |
| Get State | `GET http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore/{key}` | Retrieve history before agent run |
| Delete State | `DELETE http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore/{key}` | Clear conversation on user request |

**Note**: `DAPR_HTTP_PORT` is configurable via environment variable (default: 3500)

### State Key Pattern

```
chat:{user_id}:{conversation_id}

Examples:
- chat:user-abc123:conv-001
- chat:user-xyz789:conv-042
```

### State Payload Schema

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
      "timestamp": "2025-12-25T10:00:00Z"
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

## Validation Rules

| Field | Validation | Error Response |
|-------|------------|----------------|
| user_id | Must match JWT claim | 403 Forbidden |
| conversation_id | Alphanumeric, max 50 chars | 400 Bad Request |
| message.role | Must be "user" or "assistant" | 400 Bad Request |
| message.content | Non-empty string, max 10000 chars | 400 Bad Request |
| State key format | Must match `chat:{user_id}:{conversation_id}` | 400 Bad Request |

## Constitution Alignment

- Principle VIII: User Isolation (user_id in state key enforces data separation)
- Principle XXII: Event-Driven Architecture (Dapr integration)
- Principle XXIII: Dapr Components (State Store usage)
- Principle II: Spec-Driven Development (this specification)
- Principle XV: Twelve-Factor App (externalized state management)
