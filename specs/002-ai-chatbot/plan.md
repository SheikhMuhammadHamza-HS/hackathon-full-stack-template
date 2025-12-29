# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `002-ai-chatbot` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ai-chatbot/spec.md`

## Summary

Implement conversational AI interface for task management using OpenAI Agents SDK, MCP tools, and ChatKit. Users will be able to create, view, complete, delete, and update tasks via natural language commands. The system uses a stateless architecture where conversation history is stored in PostgreSQL and fetched on every request, enabling horizontal scaling and ensuring no data loss on server restarts.

**Technical Approach**:
- **Intelligence Layer**: OpenAI Agent with 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
- **MCP Bridge**: Tools are thin wrappers around existing Phase II CRUD functions
- **Stateless Design**: Agent instantiated per-request with database-backed conversation history
- **Frontend**: ChatKit React components for chat UI
- **Database**: Two new tables (conversations, messages) with foreign keys to users
- **Security**: JWT authentication, agent context injection, three-layer user isolation

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK, ChatKit React, FastAPI, SQLModel, Next.js 16, React 19
**Storage**: Neon Serverless PostgreSQL (extend with conversations and messages tables)
**Testing**: Manual testing via chat interface, curl for API testing, multi-user isolation testing
**Target Platform**: Cloud deployment (Render backend, Vercel frontend, Neon database)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**: P95 response time < 3 seconds, conversation history fetch < 500ms, message save < 200ms
**Constraints**: Stateless architecture (no in-memory state), user isolation enforced, rate limit 20 messages/minute per user
**Scale/Scope**: Support 100 concurrent users, 10,000 messages per user max, 100-message conversation history without degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gates (Phase II Principles)

✅ **Principle II (Spec-Driven Development)**:
- spec.md created with 6 user stories, 35 functional requirements, 10 success criteria
- plan.md (this file) being generated before any implementation
- Tasks will be generated via /sp.tasks before coding begins

✅ **Principle III (Test-First Development)**:
- Each user story includes acceptance scenarios (24 total scenarios defined)
- 10 edge cases identified in spec
- Testing checklist in quickstart.md
- Manual test procedures defined for each feature

✅ **Principle IV (Data Model Integrity)**:
- data-model.md defines Conversation and Message entities
- Foreign keys to users table (CASCADE delete)
- Indexes on user_id, conversation_id, created_at for performance
- User isolation enforced via database schema

✅ **Principle V (Input Validation)**:
- Message content validation: 1-10,000 characters
- Role validation: CHECK constraint ('user' or 'assistant')
- MCP tool parameter validation defined in contracts
- Tool responses are structured dicts (not exceptions)

✅ **Principle VIII (User Isolation)**:
- All queries filter by authenticated user_id from JWT
- Agent context injection pattern prevents user_id manipulation
- Three-layer defense: API → Agent Context → Database
- Conversation and message queries always include user_id filter

✅ **Principle IX (RESTful API)**:
- Chat endpoint follows REST conventions: POST /api/{user_id}/chat
- Request/response use JSON format
- Proper HTTP status codes: 200, 400, 401, 403, 429, 500
- Error responses in consistent format: {"error": "message"}

✅ **Principle X (Authentication-First)**:
- Chat endpoint requires JWT authentication (Depends(verify_jwt))
- Agent instantiation only after JWT validation
- ChatKit uses same JWT token as traditional UI

### Phase III Specific Gates

✅ **Principle XIII (MCP-First Architecture)**:
- All 5 CRUD operations exposed as MCP tools (FR-011)
- Tools are thin wrappers calling existing CRUD functions (FR-012)
- Tools read user_id from agent context, not parameters (FR-013)
- No direct database access in agent code

✅ **Principle XIV (Stateless AI)**:
- No in-memory conversation storage (FR-021)
- Agent instantiated per-request, no persistent objects (FR-022)
- Conversation history fetched from database every request (FR-018)
- Server restart does not lose data (FR-023)

✅ **Principle XV (Agentic Workflow)**:
- OpenAI Agents SDK used for orchestration (research.md confirms)
- No manual keyword matching or intent parsing
- Agent decides tool selection via function calling
- System instructions define boundaries, not parsing logic

✅ **Principle XVI (Agent Security)**:
- Agent context set from JWT user_id (FR-027)
- Tools validate parameters and return structured errors (FR-015)
- System instructions stored server-side (instructions.py file)
- Agent boundary testing included (refuse off-topic requests)
- Rate limiting enforced (FR-030)

**Status**: ✅ ALL GATES PASSED - Proceeding to Phase 0 research

### Post-Design Re-Check

*Completed after Phase 1 design artifacts generated*

✅ **Data Model Integrity**:
- Conversation and Message entities fully specified in data-model.md
- Foreign keys, indexes, and validation rules defined
- Migration strategy documented

✅ **API Contracts**:
- chat-endpoint.md defines POST /api/{user_id}/chat contract
- mcp-tools.md defines all 5 tool signatures
- Request/response schemas fully specified
- Error handling documented

✅ **Security Design**:
- Agent context injection pattern prevents user_id manipulation
- All queries filter by authenticated_user_id
- Tool validation prevents invalid parameters
- Multi-layer defense documented

**Status**: ✅ ALL DESIGN GATES PASSED - Ready for /sp.tasks

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-chatbot/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical research and decisions
├── data-model.md        # Database schema design
├── quickstart.md        # Setup and testing guide
├── contracts/           # API contract specifications
│   ├── chat-endpoint.md # POST /api/{user_id}/chat
│   └── mcp-tools.md     # MCP tool signatures
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Generated by /sp.tasks (not yet created)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── ai/                      # NEW: Intelligence Layer
│   │   ├── __init__.py
│   │   ├── agent.py             # Agent creation function
│   │   ├── tools.py             # 5 MCP tool implementations
│   │   └── instructions.py      # System instructions (boundaries)
│   ├── routers/
│   │   ├── chat.py              # NEW: Chat endpoint
│   │   ├── auth.py              # Existing (unchanged)
│   │   ├── tasks.py             # Existing (unchanged)
│   │   └── admin.py             # Existing (unchanged)
│   ├── models.py                # Add Conversation, Message models
│   ├── schemas.py               # Add ChatRequest, ChatResponse schemas
│   ├── database.py              # Existing (unchanged)
│   ├── auth.py                  # Existing (unchanged)
│   └── main.py                  # Include chat router
│
├── alembic/versions/
│   └── [timestamp]_add_conversations_and_messages_tables.py  # NEW migration
│
└── tests/                       # Existing (Phase III tests optional)

frontend/
├── app/
│   ├── chat/                    # NEW: Chat page
│   │   └── page.tsx             # ChatKit integration or custom UI
│   ├── dashboard/
│   │   └── page.tsx             # Add chat button/link
│   ├── auth/                    # Existing (unchanged)
│   └── admin/                   # Existing (unchanged)
│
├── components/
│   ├── ChatInterface.tsx        # NEW (if custom UI)
│   ├── ChatMessage.tsx          # NEW (if custom UI)
│   ├── ChatInput.tsx            # NEW (if custom UI)
│   └── ...                      # Existing components (unchanged)
│
└── lib/
    ├── api-client.ts            # Existing (unchanged)
    └── auth.ts                  # Existing (unchanged)

.claude/
└── skills/
    ├── chatkit/                 # NEW: ChatKit skill documentation
    ├── mcp/                     # Existing MCP skill
    ├── openai-agents-sdk/       # Existing Agents SDK skill
    └── ...                      # Other skills
```

**Structure Decision**: Web application (Option 2 from template). Backend extends existing FastAPI app with new /ai directory for Intelligence Layer. Frontend adds /chat page. No changes to existing Phase II structure except additions.

## Complexity Tracking

> **No constitutional violations** - All principles adhered to. This section left empty as no complexity justification needed.

---

## Phase 0: Research (COMPLETE)

Research completed in `research.md`. All technical unknowns resolved:

1. ✅ OpenAI Agents SDK integration pattern (per-request instantiation)
2. ✅ MCP tool definition approach (thin wrappers with context injection)
3. ✅ ChatKit frontend integration (Client Component with JWT provider)
4. ✅ Stateless architecture pattern (fetch history → process → save)
5. ✅ Database schema design (conversations + messages tables)
6. ✅ Agent system instructions (boundary enforcement)
7. ✅ Security - agent context injection (JWT → context → tools)
8. ✅ Rate limiting strategy (SlowAPI middleware)
9. ✅ Error handling - OpenAI failures (try-except with fallback)
10. ✅ Performance - conversation history limits (50 recent messages)

**Key Decisions**:
- Use OpenAI Agents SDK (official, constitution-required)
- Use Official MCP SDK (industry standard)
- Use ChatKit for UI (battle-tested, maintained)
- Stateless per-request pattern (scalability)
- 50-message history limit (performance vs context tradeoff)
- SlowAPI for rate limiting (simple, FastAPI-compatible)

No NEEDS CLARIFICATION items remaining. Proceeding to Phase 1.

---

## Phase 1: Design (COMPLETE)

### 1.1 Data Model ✅

**File**: `data-model.md` (generated)

**Entities Designed**:
- **Conversation**: id, user_id (FK), created_at, updated_at
- **Message**: id, user_id (FK), conversation_id (FK), role, content, tool_calls, created_at

**Relationships**:
- users (1) → conversations (N)
- users (1) → messages (N)
- conversations (1) → messages (N)

**Indexes**: 5 indexes for query optimization
**Foreign Keys**: 3 with CASCADE delete
**Validation**: Role CHECK constraint, content NOT NULL
**Migration**: Alembic migration strategy documented

---

### 1.2 API Contracts ✅

**Files**: `contracts/chat-endpoint.md`, `contracts/mcp-tools.md`

**Chat Endpoint Contract**:
- Method: POST /api/{user_id}/chat
- Request: {message, conversation_id}
- Response: {reply, conversation_id, tool_calls, timestamp}
- Errors: 400, 401, 403, 429, 500 with detailed scenarios
- Rate limit: 20/minute per user

**MCP Tool Contracts**:
- add_task(title, description) → {success, task}
- list_tasks(filter) → {success, tasks, count}
- complete_task(task_id) → {success, task}
- delete_task(task_id) → {success, task_id, title}
- update_task(task_id, title, description) → {success, task}

All tools return structured dicts (not raise exceptions).

---

### 1.3 Quickstart Guide ✅

**File**: `quickstart.md` (generated)

**Includes**:
- Prerequisites checklist (Phase II completion)
- Environment variable setup (OPENAI_API_KEY)
- Dependency installation (openai-agents-sdk, chatkit-react)
- Database migration steps
- Development workflow (5 phases)
- Testing checklist (backend, frontend, integration)
- Common commands
- Troubleshooting guide

**Ready for**: Implementation team to follow step-by-step

---

### 1.4 Agent Context Update ✅

Running agent context update script:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

**Status**: ✅ COMPLETE - Agent context updated successfully

---

## Phase 2: Implementation (PENDING)

### 2.1 Backend Implementation

**Target Directory**: `backend/app/ai/`

**Files to Create**:
- `backend/app/ai/__init__.py` - Package initialization
- `backend/app/ai/agent.py` - Agent creation and management functions
- `backend/app/ai/tools.py` - MCP tool implementations (add_task, list_tasks, complete_task, delete_task, update_task)
- `backend/app/ai/instructions.py` - System instructions for agent boundaries

**Files to Modify**:
- `backend/app/models.py` - Add Conversation and Message SQLModel classes
- `backend/app/schemas.py` - Add ChatRequest and ChatResponse Pydantic models
- `backend/app/routers/chat.py` - New chat endpoint router
- `backend/app/main.py` - Include chat router in main app
- `alembic/versions/[timestamp]_add_conversations_and_messages_tables.py` - Database migration

### 2.2 Frontend Implementation

**Target Directory**: `frontend/`

**Files to Create**:
- `frontend/app/chat/page.tsx` - Chat page component using ChatKit
- `frontend/components/ChatInterface.tsx` - ChatKit wrapper component (if needed)
- `frontend/components/ChatMessage.tsx` - Message display component (if custom UI needed)
- `frontend/components/ChatInput.tsx` - Input component (if custom UI needed)

**Files to Modify**:
- `frontend/app/dashboard/page.tsx` - Add link/button to chat page

### 2.3 MCP Server Setup

**Target Directory**: `.claude/skills/chatkit/`

**Files to Create**:
- `.claude/skills/chatkit/` - Documentation and configuration for ChatKit integration

### 2.4 Implementation Order

1. Database schema (models and migration)
2. MCP tools (backend logic)
3. Chat endpoint (API integration)
4. Frontend components (UI)
5. Integration testing

---

## Phase 3: Testing (PENDING)

### 3.1 Unit Tests

- MCP tool validation tests
- Agent context injection tests
- Database model validation tests
- Error handling tests

### 3.2 Integration Tests

- End-to-end chat flow tests
- User isolation tests
- Rate limiting tests
- Conversation history persistence tests

### 3.3 Manual Testing Checklist

- [ ] User can start new conversation
- [ ] User can add tasks via chat
- [ ] User can list tasks via chat
- [ ] User can complete tasks via chat
- [ ] User can delete tasks via chat
- [ ] User can update tasks via chat
- [ ] User cannot access other users' conversations
- [ ] Rate limiting works correctly
- [ ] Error handling works (API unavailable)
- [ ] Conversation history persists across messages

---

## Phase 4: Validation (PENDING)

### 4.1 Success Criteria Verification

All 10 success criteria from spec.md will be validated:

- SC-001: Task creation via chat completes in < 10 seconds
- SC-002: 95% of natural language commands correctly interpreted
- SC-003: All conversation history persists across server restarts
- SC-004: All 5 task operations available via chat interface
- SC-005: Zero cross-user data leakage
- SC-006: P95 response time < 3 seconds
- SC-007: Chat UI loads in < 1 second
- SC-008: No performance degradation with 100+ message conversations
- SC-009: 90% of users complete first operation successfully
- SC-010: Agent refuses all off-topic requests

### 4.2 Performance Validation

- Database query timing for conversation history fetch
- Agent response time measurement
- Memory usage monitoring during extended conversations

### 4.3 Security Validation

- Cross-user data access prevention
- JWT authentication validation
- Rate limiting effectiveness
- System instruction boundary enforcement

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create implementation tasks from this plan
2. **Set Up Environment**: Follow quickstart.md to prepare development environment
3. **Create Branch**: Create feature branch from main for implementation
4. **Implement Tasks**: Follow generated tasks.md in order
5. **Test Implementation**: Execute testing checklist from Phase 3
6. **Validate Success**: Verify all 10 success criteria are met

**Ready for**: `/sp.tasks` to generate implementation tasks
