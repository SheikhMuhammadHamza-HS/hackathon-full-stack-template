# Tasks: AI Agent with MCP Tools

**Input**: Implemented code in `backend/app/ai/` and `backend/app/routers/chat.py`
**Status**: All tasks completed (spec written after implementation)

## Format: `- [x] [ID] Description`

All tasks marked complete as implementation already exists.

---

## Phase 1: AI Agent Infrastructure

**Purpose**: Set up OpenAI client and agent factory

- [x] T001 Create backend/app/ai/ directory with __init__.py
- [x] T002 Create backend/app/ai/instructions.py with system instructions for TodoBot
- [x] T003 Define AGENT_NAME = "TodoBot" in instructions.py
- [x] T004 Define AGENT_MODEL = "gpt-4o-mini" in instructions.py
- [x] T005 Write system instructions defining agent capabilities and boundaries
- [x] T006 Create backend/app/ai/agent.py with agent factory pattern
- [x] T007 Implement create_agent(user_id, tools) function returning agent config
- [x] T008 Use AsyncOpenAI client for non-blocking operations
- [x] T009 Implement run_agent(config, message, history, executor) async function
- [x] T010 Add context management: set_context(), get_context(), clear_context()

**Implemented in**: `backend/app/ai/instructions.py`, `backend/app/ai/agent.py`

---

## Phase 2: MCP Tools Implementation

**Purpose**: Create 5 MCP tools using official MCP SDK

- [x] T011 Create backend/app/ai/tools.py for MCP tool implementations
- [x] T012 Import required tools: add_task, list_tasks, complete_task, delete_task, update_task
- [x] T013 Implement add_task(session, title, description) → dict
- [x] T014 Implement list_tasks(session, filter) → dict with tasks array
- [x] T015 Implement complete_task(session, task_id) → dict
- [x] T016 Implement delete_task(session, task_id) → dict
- [x] T017 Implement update_task(session, task_id, title, description) → dict
- [x] T018 All tools read user_id from get_context("user_id")
- [x] T019 All tools return {"success": bool, ...} format
- [x] T020 Add input validation in each tool
- [x] T021 Add error handling (return error dict, don't raise exceptions)

**Implemented in**: `backend/app/ai/tools.py`

---

## Phase 3: MCP Server Integration

**Purpose**: Use official MCP SDK for standardized tool definitions

- [x] T022 Add mcp>=1.0.0 to backend/pyproject.toml dependencies
- [x] T023 Install MCP SDK: pip install mcp
- [x] T024 Create backend/app/ai/mcp_server.py with MCP server
- [x] T025 Define mcp_server = Server("todo-tasks-server")
- [x] T026 Implement @mcp_server.list_tools() handler
- [x] T027 Return 5 Tool objects with name, description, inputSchema
- [x] T028 Implement @mcp_server.call_tool() handler
- [x] T029 Create get_mcp_tools() function returning OpenAI-compatible format
- [x] T030 Create execute_mcp_tool(name, args, session) async function
- [x] T031 Map tool names to tool functions in execute_mcp_tool

**Implemented in**: `backend/app/ai/mcp_server.py`

---

## Phase 4: Chat Endpoint Implementation

**Purpose**: Create REST API endpoint for chat processing

- [x] T032 Create backend/app/routers/chat.py
- [x] T033 Add ChatRequest and ChatResponse schemas to backend/app/schemas.py
- [x] T034 Implement POST /{user_id}/chat endpoint with JWT auth
- [x] T035 Add rate limiting decorator: @limiter.limit("20/minute")
- [x] T036 Implement get-or-create conversation logic
- [x] T037 Save user message to database (Message table)
- [x] T038 Fetch conversation history for context (last N messages)
- [x] T039 Call AI agent with message and history
- [x] T040 Parse agent response and extract tool_calls
- [x] T041 Save assistant response to database with tool_calls JSON
- [x] T042 Update conversation.updated_at timestamp
- [x] T043 Return ChatResponse with reply and tool_calls
- [x] T044 Add error handling with fallback messages
- [x] T045 Clear agent context after request completion

**Implemented in**: `backend/app/routers/chat.py`

---

## Phase 5: Conversation Management Endpoints

**Purpose**: API endpoints for conversation list and deletion

- [x] T046 Implement GET /{user_id}/conversations endpoint
- [x] T047 Return conversations ordered by updated_at DESC (most recent first)
- [x] T048 Limit to 20 conversations
- [x] T049 Implement GET /{user_id}/conversations/{id}/messages endpoint
- [x] T050 Return messages ordered by created_at ASC (chronological)
- [x] T051 Include tool_calls in message response
- [x] T052 Implement DELETE /{user_id}/conversations/{id} endpoint
- [x] T053 Delete all messages in conversation first
- [x] T054 Delete conversation record
- [x] T055 Return success message

**Implemented in**: `backend/app/routers/chat.py`

---

## Phase 6: Router Integration

**Purpose**: Register chat router with FastAPI app

- [x] T056 Import chat router in backend/app/main.py
- [x] T057 Register limiter with app.state.limiter
- [x] T058 Include chat router: app.include_router(chat.router, prefix="/api")
- [x] T059 Add RateLimitExceeded exception handler
- [x] T060 Update API version to 0.2.0
- [x] T061 Update API description to include "AI Chatbot"

**Implemented in**: `backend/app/main.py`

---

## Phase 7: Testing & Validation

**Purpose**: Verify AI agent and MCP tools work correctly

- [x] T062 Test add_task tool: create task via chat, verify in database
- [x] T063 Test list_tasks tool: ask "show my tasks", verify response
- [x] T064 Test complete_task tool: "mark task 1 as done", verify status changed
- [x] T065 Test delete_task tool: "delete task 2", verify removed
- [x] T066 Test update_task tool: "update task 3 title", verify changed
- [x] T067 Test agent boundary: ask "what's the weather", verify refusal
- [x] T068 Test user isolation: verify tools filter by user_id from context
- [x] T069 Test rate limiting: send 21 requests in 1 minute, verify 429 error
- [x] T070 Test conversation persistence: refresh page, verify history loads
- [x] T071 Test error handling: invalid OpenAI key, verify fallback message

**Verified via**: Manual testing with multiple users and scenarios

---

## Dependencies & Execution Order

### Prerequisites
- ✅ 001-user-auth (JWT validation)
- ✅ 002-chat-persistence (database tables)
- ✅ 001-todo-web-app (Task model and CRUD)

### Execution Order
1. Phase 1: AI Infrastructure (T001-T010)
2. Phase 2: MCP Tools (T011-T021)
3. Phase 3: MCP Server (T022-T031)
4. Phase 4: Chat Endpoint (T032-T045)
5. Phase 5: Conversation APIs (T046-T055)
6. Phase 6: Integration (T056-T061)
7. Phase 7: Testing (T062-T071)

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Infrastructure | 10 | Agent factory setup |
| Phase 2: MCP Tools | 11 | 5 tools implementation |
| Phase 3: MCP Server | 10 | Official SDK integration |
| Phase 4: Chat Endpoint | 14 | Main API endpoint |
| Phase 5: Conversation APIs | 10 | List/delete endpoints |
| Phase 6: Integration | 6 | Router registration |
| Phase 7: Testing | 10 | Validation tests |
| **Total** | **71** | All completed ✅ |

---

## Implementation Evidence

### Files Created
- ✅ `backend/app/ai/instructions.py` - System instructions
- ✅ `backend/app/ai/agent.py` - Agent factory
- ✅ `backend/app/ai/tools.py` - 5 MCP tools
- ✅ `backend/app/ai/mcp_server.py` - MCP SDK server
- ✅ `backend/app/routers/chat.py` - Chat endpoints
- ✅ `backend/app/schemas.py` - ChatRequest/Response schemas

### Dependencies Added
- ✅ openai>=1.59.0
- ✅ openai-agents>=0.0.3
- ✅ slowapi>=0.1.9
- ✅ mcp>=1.0.0

### API Endpoints Live
- ✅ POST /api/{user_id}/chat
- ✅ GET /api/{user_id}/conversations
- ✅ GET /api/{user_id}/conversations/{id}/messages
- ✅ DELETE /api/{user_id}/conversations/{id}
