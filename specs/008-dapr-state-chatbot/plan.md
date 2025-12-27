# Implementation Plan: Dapr State Store for Chatbot

**Branch**: `008-dapr-state-chatbot` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-dapr-state-chatbot/spec.md`

## Summary

Refactor the AI Chatbot to use Dapr State Store API instead of direct SQL queries for conversation history management. This decouples the chatbot from specific database schemas, enables portable state management across cloud providers, and aligns with Phase V event-driven architecture principles.

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript/Node.js 20+ (Frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, httpx (for Dapr HTTP calls), Pydantic
**Storage**: Dapr State Store (backed by PostgreSQL via statestore component)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Kubernetes (Cloud - DigitalOcean DOKS/Azure AKS/GKE)
**Project Type**: Web application (Backend API + Frontend)
**Performance Goals**: State retrieval <500ms for 50 messages, 1000 concurrent chat sessions
**Constraints**: Max 200 messages per conversation, configurable message window (default 50)
**Scale/Scope**: Multi-user, user-isolated conversation state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Spec-Driven Development | ✅ PASS | Spec created before implementation |
| VIII. User Isolation | ✅ PASS | State key includes user_id: `chat:{user_id}:{conversation_id}` |
| XIV. Stateless AI with DB Persistence | ✅ PASS | Using Dapr State Store (Constitution allows as alternative) |
| XV. Twelve-Factor App | ✅ PASS | Externalized state via Dapr, configurable via env vars |
| XXIII. Sidecar Pattern with Dapr | ✅ PASS | All state operations via Dapr HTTP API |
| XXIV. Infrastructure Independence | ✅ PASS | No direct PostgreSQL client, uses Dapr abstraction |

**Gate Result**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/008-dapr-state-chatbot/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── dapr-state-api.md
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   └── state_store.py      # NEW: Dapr State Store service
│   ├── routers/
│   │   └── chat.py             # MODIFY: Use state store instead of DB
│   ├── schemas.py              # MODIFY: Add ConversationState schema
│   └── agent.py                # MODIFY: Load state before agent run
├── tests/
│   └── test_state_store.py     # NEW: State store tests
└── alembic/
    └── versions/
        └── xxx_deprecate_chat_tables.py  # Migration to deprecate old tables

k8s/
├── dapr-components/
│   └── statestore.yaml         # Dapr state store component config
```

**Structure Decision**: Web application structure with backend modifications. New state store service in `backend/app/services/`. Dapr component configuration in `k8s/dapr-components/`.

## Architecture

### Current Flow (Phase III)
```
User Message → Chat Router → Agent → Direct DB Query → Response
                                   ↓
                            conversations table
                            messages table
```

### Target Flow (Phase V)
```
User Message → Chat Router → State Store Service → Dapr Sidecar → Response
                                   ↓                    ↓
                            Agent with history    PostgreSQL
                                                 (via Dapr State Store)
```

### Dapr State Store Integration

```python
# State Store Service Pattern
class DaprStateStore:
    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.base_url = f"http://localhost:{self.dapr_port}/v1.0/state/statestore"

    async def get_state(self, key: str) -> Optional[dict]:
        """GET http://localhost:{port}/v1.0/state/statestore/{key}"""

    async def save_state(self, key: str, value: dict) -> bool:
        """POST http://localhost:{port}/v1.0/state/statestore"""

    async def delete_state(self, key: str) -> bool:
        """DELETE http://localhost:{port}/v1.0/state/statestore/{key}"""
```

## Migration Strategy

1. **Deploy Dapr State Store** alongside existing DB tables
2. **Create migration script** to copy existing conversations/messages to state store
3. **Switch application** to use Dapr State Store API exclusively
4. **Deprecate tables** via Alembic migration (remove conversations, messages)

## Complexity Tracking

No constitution violations. All changes align with Phase V principles.

## Dependencies

- Dapr runtime installed on Kubernetes cluster
- State Store component configured (`statestore`)
- PostgreSQL database accessible from Dapr
- Phase III AI Chatbot functional
- OpenAI Agents SDK integration complete

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| State store unavailable | Degraded mode - chat works without history |
| Data loss during migration | Backup existing tables before migration |
| Performance degradation | Monitor state retrieval times, optimize if needed |
| Backward compatibility | Maintain same chat API contract |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement state store service
3. Migrate chat router to use state store
4. Create migration script for existing data
5. Deploy and test on Kubernetes
