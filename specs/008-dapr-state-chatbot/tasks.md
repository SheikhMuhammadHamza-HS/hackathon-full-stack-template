# Implementation Tasks: Dapr State Store for Chatbot

**Feature**: 008-dapr-state-chatbot
**Generated**: 2025-12-25
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup & Infrastructure

- [x] [008-001] [P0] [Setup] Create Dapr state store component configuration at `k8s/dapr-components/statestore.yaml`
- [ ] [008-002] [P0] [Setup] Verify Dapr sidecar injection works locally with `dapr run --app-id backend`
- [x] [008-003] [P0] [Setup] Add httpx dependency to `backend/requirements.txt` for Dapr HTTP calls (already in pyproject.toml)

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] [008-004] [P1] [Foundation] Create `backend/app/services/state_store.py` with DaprStateStore class
- [x] [008-005] [P1] [Foundation] Implement `get_state(key: str)` method for retrieving conversation state
- [x] [008-006] [P1] [Foundation] Implement `save_state(key: str, value: dict)` method for persisting state
- [x] [008-007] [P1] [Foundation] Implement `delete_state(key: str)` method for clearing conversation
- [x] [008-008] [P1] [Foundation] Add DAPR_HTTP_PORT environment variable support (default: 3500)
- [x] [008-009] [P1] [Foundation] Create Pydantic schemas in `backend/app/schemas.py`: ConversationState, MessageEntry, ToolCallInfo

---

## Phase 3: User Story 1 - Seamless Chat Experience (P1)

> Users interact with the AI chatbot and their conversation history persists across sessions without any change in user experience.

- [x] [008-010] [P1] [Story1] Modify `backend/app/routers/chat.py` to use DaprStateStore instead of direct DB queries
- [x] [008-011] [P1] [Story1] Implement state key generation following pattern `chat:{user_id}:{conversation_id}`
- [x] [008-012] [P1] [Story1] Load conversation state before agent run in `backend/app/agent.py`
- [x] [008-013] [P1] [Story1] Save updated conversation state after each message exchange
- [x] [008-014] [P1] [Story1] Handle empty state (new conversation) gracefully - create new state on first message
- [ ] [008-015] [P1] [Story1] Test: Start conversation, send 5 messages, close browser, reopen and verify full context preserved

---

## Phase 4: User Story 2 - Conversation State Consistency (P1)

> System maintains conversation state reliably without data loss or corruption even under concurrent access.

- [x] [008-016] [P1] [Story2] Implement message ordering preservation (append to messages array in chronological order)
- [x] [008-017] [P1] [Story2] Add optimistic concurrency handling (last-write-wins pattern)
- [x] [008-018] [P1] [Story2] Implement error handling for malformed state data - log and continue with empty state
- [ ] [008-019] [P1] [Story2] Test: Send 10 rapid messages in 5 seconds, verify all stored in correct order

---

## Phase 5: User Story 3 - Efficient State Retrieval (P2)

> AI agent retrieves conversation history quickly to maintain responsive chat experience.

- [x] [008-020] [P2] [Story3] Implement configurable message window (default: 50, max: 200 messages)
- [x] [008-021] [P2] [Story3] Add MESSAGE_WINDOW_SIZE and MAX_MESSAGES env variables
- [x] [008-022] [P2] [Story3] Implement automatic truncation when messages exceed 200 (keep most recent)
- [x] [008-023] [P2] [Story3] Add timestamps to state (created_at, updated_at)
- [ ] [008-024] [P2] [Story3] Test: Load conversation with 100 messages, verify response time under 2 seconds

---

## Phase 6: User Story 4 - Secure State Isolation (P1)

> Each user's conversation state is isolated and inaccessible to other users.

- [x] [008-025] [P1] [Story4] Validate user_id in state key matches JWT authenticated user before any operation
- [x] [008-026] [P1] [Story4] Return 403 Forbidden if user_id mismatch detected
- [x] [008-027] [P1] [Story4] Implement state key format validation (must match `chat:{user_id}:{conversation_id}`)
- [ ] [008-028] [P1] [Story4] Test: User B attempts to access User A's conversation, verify 403 returned

---

## Phase 7: Degraded Mode & Error Handling

- [x] [008-029] [P1] [Edge] Implement degraded mode when Dapr State Store unavailable - chat continues without history
- [x] [008-030] [P1] [Edge] Add warning banner to response when operating in degraded mode
- [x] [008-031] [P1] [Edge] Implement state TTL configuration (default: 30 days) via Dapr component metadata
- [x] [008-032] [P1] [Edge] Add logging for all state operations (get, save, delete) with timing metrics

---

## Phase 8: Migration

- [ ] [008-033] [P1] [Migration] Create one-time migration script `backend/scripts/migrate_chat_to_dapr.py`
- [ ] [008-034] [P1] [Migration] Migrate existing conversations from DB to Dapr State Store
- [ ] [008-035] [P1] [Migration] Migrate existing messages from DB to state store format
- [ ] [008-036] [P1] [Migration] Verify migration data integrity (message count, timestamps)
- [ ] [008-037] [P2] [Migration] Create Alembic migration `xxx_deprecate_chat_tables.py` to drop conversations/messages tables

---

## Phase 9: Testing & Documentation

- [ ] [008-038] [P1] [Test] Create `backend/tests/test_state_store.py` with unit tests for DaprStateStore
- [ ] [008-039] [P1] [Test] Add integration tests for chat router with mocked Dapr sidecar
- [ ] [008-040] [P1] [Test] Test state store unavailability - verify degraded mode activates
- [ ] [008-041] [P2] [Docs] Update quickstart.md with local development setup instructions
- [ ] [008-042] [P2] [Docs] Document Dapr state store component configuration in k8s/

---

## Summary

| Phase | Tasks | Priority |
|-------|-------|----------|
| Setup | 3 | P0 |
| Foundation | 6 | P1 |
| Story 1 - Seamless Chat | 6 | P1 |
| Story 2 - State Consistency | 4 | P1 |
| Story 3 - Efficient Retrieval | 5 | P2 |
| Story 4 - Secure Isolation | 4 | P1 |
| Error Handling | 4 | P1 |
| Migration | 5 | P1-P2 |
| Testing & Docs | 5 | P1-P2 |
| **Total** | **42** | |

---

## Acceptance Checklist

- [ ] All P1 tasks completed and tested
- [ ] State retrieval under 500ms for 50 messages
- [ ] Zero cross-user data leakage
- [ ] Chat works in degraded mode when state store unavailable
- [ ] Migration script tested and documented
- [ ] Existing chat API contract unchanged (backward compatible)
