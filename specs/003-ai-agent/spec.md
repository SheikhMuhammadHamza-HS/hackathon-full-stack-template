# Feature Specification: AI Agent with MCP Tools

**Feature Branch**: `002-ai-chatbot` (implemented)
**Created**: 2025-12-22
**Status**: Implemented (spec written after implementation)

## Overview

AI-powered natural language processing layer that interprets user commands and executes task management operations through standardized MCP tools.

## User Scenarios & Testing

### User Story 1 - Natural Language Task Creation

As a user, I want to create tasks by typing natural language instead of filling forms.

**Independent Test**: Type "Add a task to buy groceries" → task created

**Acceptance Scenarios**:

1. **Given** I type "Add a task to buy milk", **Then** AI creates task with title "Buy milk"
2. **Given** I type "Remind me to call dentist", **Then** AI extracts intent and creates task
3. **Given** I type vague command, **Then** AI asks clarifying question

---

### User Story 2 - Conversational Task Viewing

As a user, I want to ask about my tasks and get natural language responses.

**Independent Test**: Type "What tasks do I have?" → AI lists tasks

**Acceptance Scenarios**:

1. **Given** I ask "Show my tasks", **Then** AI lists all tasks with IDs and titles
2. **Given** I have no tasks, **Then** AI responds "You don't have any tasks yet"

---

### User Story 3 - Task Operations via Chat

As a user, I want to complete, delete, and update tasks through conversation.

**Independent Test**: Type "Mark task 1 as done" → task completed

**Acceptance Scenarios**:

1. **Given** I say "Mark task 3 as done", **Then** AI completes task 3
2. **Given** I say "Delete task 2", **Then** AI deletes task 2
3. **Given** I say "Update task 1 title to X", **Then** AI updates task title

---

## Requirements

### Functional Requirements

#### AI Agent Core
- **FR-001**: Agent MUST use OpenAI Agents SDK (AsyncOpenAI)
- **FR-002**: Agent MUST use gpt-4o-mini model (or better)
- **FR-003**: Agent MUST be stateless (created fresh per request)
- **FR-004**: Agent MUST have system instructions defining boundaries

#### MCP Tools
- **FR-005**: Implement 5 MCP tools using official MCP SDK
- **FR-006**: add_task tool: Creates new task
- **FR-007**: list_tasks tool: Retrieves user's tasks
- **FR-008**: complete_task tool: Marks task as done
- **FR-009**: delete_task tool: Removes task
- **FR-010**: update_task tool: Modifies task details

#### Tool Execution
- **FR-011**: Tools MUST read user_id from agent context (not parameters)
- **FR-012**: Tools MUST return structured dict (success/error format)
- **FR-013**: Tools MUST validate all input parameters
- **FR-014**: Tool errors MUST be caught and returned as error dicts

#### Security
- **FR-015**: Agent context MUST be injected with authenticated user_id
- **FR-016**: Agent MUST refuse off-topic requests
- **FR-017**: Agent MUST enforce instruction boundaries
- **FR-018**: Agent MUST NOT reveal internal system details

#### Chat Endpoint
- **FR-019**: POST /api/{user_id}/chat endpoint with JWT auth
- **FR-020**: Endpoint MUST get or create conversation
- **FR-021**: Endpoint MUST save user message to database
- **FR-022**: Endpoint MUST process message with AI agent
- **FR-023**: Endpoint MUST save assistant response to database
- **FR-024**: Endpoint MUST return reply and tool_calls
- **FR-025**: Endpoint MUST be rate limited (20 requests/min)

## Success Criteria

- **SC-001**: AI correctly interprets 95% of common task commands
- **SC-002**: Agent refuses 100% of off-topic requests
- **SC-003**: All 5 MCP tools execute successfully
- **SC-004**: Response time < 3 seconds (P95)
- **SC-005**: Zero cross-user data leakage

## Scope

### In Scope

**AI Agent**:
- OpenAI AsyncOpenAI client
- Agent factory (creates fresh agent per request)
- System instructions (TodoBot personality)
- Context injection (user_id)

**MCP Tools**:
- Official MCP SDK integration
- 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- Tool definitions with input schemas
- Tool executor connecting to database

**Chat Endpoint**:
- POST /api/{user_id}/chat
- GET /api/{user_id}/conversations
- GET /api/{user_id}/conversations/{id}/messages
- DELETE /api/{user_id}/conversations/{id}
- Rate limiting with SlowAPI
- JWT authentication

**Backend Logic**:
- Conversation get-or-create
- Message persistence
- Tool call recording
- Error handling

### Out of Scope

- Streaming responses
- Multi-agent systems
- Agent memory beyond conversation
- Custom model fine-tuning
- Voice input/output

### Assumptions

- 001-user-auth provides JWT validation
- 002-chat-persistence provides database tables
- OpenAI API key configured
- Internet connection available

### Dependencies

**Requires**:
- 001-user-auth (JWT validation)
- 002-chat-persistence (database tables)
- 001-todo-web-app (Task model and CRUD logic)

**Blocks**:
- 004-chat-ui (needs working chat endpoint)

### Constraints

**Technical**:
- MUST use OpenAI Agents SDK
- MUST use Official MCP SDK
- MUST use gpt-4o-mini or better
- Agent MUST support function calling

**Security**:
- User_id from JWT ONLY (not request body)
- All tool queries filter by user_id
- Agent instructions server-side only

**Performance**:
- Response time < 3 seconds P95
- Rate limit: 20 messages/min/user

## Non-Functional Requirements

### Performance
- **NFR-001**: Chat response P95 < 3 seconds
- **NFR-002**: Tool execution < 500ms each

### Security
- **NFR-003**: Agent context injection secure
- **NFR-004**: Prompt injection attempts blocked
- **NFR-005**: Rate limiting enforced

### Reliability
- **NFR-006**: OpenAI API failures handled gracefully
- **NFR-007**: Database errors don't crash agent
- **NFR-008**: Context cleared after each request
