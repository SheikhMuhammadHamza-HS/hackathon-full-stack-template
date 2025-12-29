# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/002-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Feature Branch**: `002-ai-chatbot`
**Generated**: 2025-12-21

**Tests**: Tests are NOT explicitly requested in the specification. Test scenarios are provided in quickstart.md for manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` and `frontend/` at repository root
- Backend follows FastAPI + SQLModel patterns from Phase II
- Frontend follows Next.js 16 App Router patterns from Phase II

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and environment configuration

- [x] T001 Add OPENAI_API_KEY to backend/.env.example with placeholder value
- [x] T002 [P] Add Phase III dependencies to backend/pyproject.toml (openai-agents, slowapi, mcp)
- [x] T003 [P] Add ChatKit dependency to frontend/package.json (@openai/chatkit-react or custom components)
- [x] T004 Create backend/app/ai/ directory structure with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [x] T005 Create Conversation model in backend/app/models.py per data-model.md
- [x] T006 Create Message model in backend/app/models.py per data-model.md
- [x] T007 Generate Alembic migration: `alembic revision --autogenerate -m "add conversations and messages tables"`
- [x] T008 Apply migration and verify tables created in Neon dashboard

### Agent Infrastructure

- [x] T009 Create system instructions in backend/app/ai/instructions.py per research.md
- [x] T010 [P] Create agent factory function in backend/app/ai/agent.py per research.md
- [x] T011 [P] Add ChatRequest and ChatResponse schemas to backend/app/schemas.py per chat-endpoint.md
- [x] T060 [P] Create MCP server in backend/app/ai/mcp_server.py using official MCP SDK
- [x] T061 [P] Refactor chat router to use MCP tools instead of direct function calling

### Chat Endpoint Core

- [x] T012 Create chat router skeleton in backend/app/routers/chat.py with POST /{user_id}/chat
- [x] T013 Implement conversation fetch/create logic in chat endpoint
- [x] T014 Implement message save logic (user and assistant messages) with atomic transaction
- [x] T015 Add rate limiting decorator (20/minute) to chat endpoint using SlowAPI
- [x] T016 Include chat router in backend/app/main.py

**Checkpoint**: Foundation ready - agent infrastructure and persistence working

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1)

**Goal**: Users can create tasks by typing natural language commands instead of filling forms

**Independent Test**: User types "Add a task to buy groceries" in chat interface, new task appears in task list

### Implementation for User Story 1

- [x] T017 [US1] Create add_task MCP tool in backend/app/ai/tools.py per mcp-tools.md
- [x] T018 [US1] Register add_task tool with agent in backend/app/ai/agent.py
- [x] T019 [US1] Implement agent.run() call in chat endpoint to process messages
- [x] T020 [US1] Create chat page at frontend/app/chat/page.tsx with basic message input
- [x] T021 [US1] Implement chat API call in frontend with JWT authentication
- [x] T022 [US1] Display chat messages (user and assistant) in frontend chat interface
- [x] T023 [US1] Add loading state while AI processes message

**Checkpoint**: Users can create tasks via chat. MVP complete!

**Manual Test**:
1. Open /chat page
2. Type "Add a task to buy milk"
3. Verify task appears in /dashboard task list
4. Verify chat shows confirmation message

---

## Phase 4: User Story 2 - Conversational Task Viewing (Priority: P1)

**Goal**: Users can ask about their tasks in natural language and receive formatted responses

**Independent Test**: User types "What tasks do I have?" and receives formatted task list

### Implementation for User Story 2

- [x] T024 [US2] Create list_tasks MCP tool in backend/app/ai/tools.py per mcp-tools.md
- [x] T025 [US2] Register list_tasks tool with agent in backend/app/ai/agent.py
- [x] T026 [US2] Update system instructions to include list_tasks usage examples

**Checkpoint**: Users can view tasks via chat

**Manual Test**:
1. Create 2-3 tasks (via chat or GUI)
2. Type "Show my tasks"
3. Verify formatted list returned with task titles and status

---

## Phase 5: User Story 6 - Conversation Persistence (Priority: P1)

**Goal**: Conversation history persists across page reloads and server restarts

**Independent Test**: User sends message, refreshes page, previous messages still visible

### Implementation for User Story 6

- [x] T027 [US6] Implement conversation history fetch in chat endpoint (recent 50 messages)
- [x] T028 [US6] Pass conversation history to agent for context continuity
- [x] T029 [US6] Fetch and display conversation history on frontend page load
- [x] T030 [US6] Support conversation_id in chat request to continue existing conversation
- [x] T031 [US6] Update conversation.updated_at timestamp on each new message

**Checkpoint**: Conversations persist across sessions

**Manual Test**:
1. Send message "Add task buy milk"
2. Refresh browser page
3. Verify previous messages display
4. Restart backend server
5. Send "What tasks do I have?"
6. Verify agent has context from previous conversation

---

## Phase 6: User Story 3 - Task Completion via Chat (Priority: P2)

**Goal**: Users can mark tasks as complete by referencing them in natural language

**Independent Test**: User types "Mark task 3 as done" and task status changes

### Implementation for User Story 3

- [x] T032 [US3] Create complete_task MCP tool in backend/app/ai/tools.py per mcp-tools.md
- [x] T033 [US3] Register complete_task tool with agent in backend/app/ai/agent.py
- [x] T034 [US3] Update system instructions for task completion patterns

**Checkpoint**: Users can complete tasks via chat

**Manual Test**:
1. Create a task via chat
2. Type "Mark task {id} as complete"
3. Verify task shows as completed in /dashboard

---

## Phase 7: User Story 4 - Task Deletion via Chat (Priority: P3)

**Goal**: Users can delete tasks by asking the AI to remove specific tasks

**Independent Test**: User types "Delete task 2" and task disappears from list

### Implementation for User Story 4

- [x] T035 [US4] Create delete_task MCP tool in backend/app/ai/tools.py per mcp-tools.md
- [x] T036 [US4] Register delete_task tool with agent in backend/app/ai/agent.py
- [x] T037 [US4] Update system instructions for deletion patterns and safety

**Checkpoint**: Users can delete tasks via chat

**Manual Test**:
1. Create a task via chat
2. Note the task ID
3. Type "Delete task {id}"
4. Verify task removed from /dashboard

---

## Phase 8: User Story 5 - Task Modification via Chat (Priority: P3)

**Goal**: Users can update existing task titles and descriptions via chat

**Independent Test**: User types "Change task 4 title to 'Call dentist at 3pm'" and task updates

### Implementation for User Story 5

- [x] T038 [US5] Create update_task MCP tool in backend/app/ai/tools.py per mcp-tools.md
- [x] T039 [US5] Register update_task tool with agent in backend/app/ai/agent.py
- [x] T040 [US5] Update system instructions for update patterns

**Checkpoint**: All 5 CRUD operations available via chat

**Manual Test**:
1. Create a task via chat
2. Type "Update task {id} title to 'New title'"
3. Verify task title changed in /dashboard

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, UX improvements, and integration

### Security & Boundaries

- [x] T041 [P] Test agent boundary enforcement (refuse off-topic requests)
- [x] T042 [P] Test prompt injection attempts and verify rejection
- [x] T043 Add error sanitization in chat endpoint (no stack traces to user)

### User Experience

- [x] T044 [P] Add chat link/button to frontend/app/dashboard/page.tsx
- [x] T045 [P] Style chat interface to match existing app theme
- [x] T046 Implement mobile responsive layout for chat (375px minimum)
- [x] T047 Add friendly error messages for OpenAI API failures
- [x] T052 Add quick action suggestion buttons above chat messages area
- [x] T053 Implement click-to-prompt functionality for quick actions (Add Task, Update Title, Mark Done, Delete Task)
- [x] T054 Persist conversation ID in localStorage to maintain chat history across page navigation
- [x] T055 Create conversation sidebar component with list of conversations
- [x] T056 Implement conversation switching functionality (select from sidebar)
- [x] T057 Add DELETE /api/{user_id}/conversations/{id} endpoint for conversation deletion
- [x] T058 Implement delete conversation UI with confirmation dialog
- [x] T059 Add mobile-responsive sidebar with hamburger menu toggle

### Multi-User Isolation Testing

- [x] T048 Create two test users and verify conversation isolation
- [x] T049 Verify MCP tools filter by user_id from context

### Final Validation

- [x] T050 Run quickstart.md testing checklist (all scenarios)
- [x] T051 Verify all 10 success criteria from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational completion
  - US1 (Task Creation) must complete before testing other tools
  - US2 (Task Viewing) can start after US1
  - US6 (Persistence) can start after US1
  - US3, US4, US5 can proceed after US1+US2
- **Polish (Phase 9)**: Depends on all user stories complete

### User Story Dependencies

| Story | Depends On | Can Run Parallel With |
|-------|------------|----------------------|
| US1 (P1) | Foundational | None (MVP start) |
| US2 (P1) | US1 | US6 |
| US6 (P1) | US1 | US2 |
| US3 (P2) | US1, US2 | US4, US5, US6 |
| US4 (P3) | US1, US2 | US3, US5 |
| US5 (P3) | US1, US2 | US3, US4 |

### Within Each User Story

1. Backend tool implementation first
2. Register tool with agent
3. Update system instructions
4. Frontend integration (if applicable)
5. Manual testing to verify

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 [P] Add backend dependencies
T003 [P] Add frontend dependencies
```

**Phase 2 (Foundational)**:
```
T010 [P] Create agent factory
T011 [P] Add request/response schemas
```

**Phase 9 (Polish)**:
```
T041 [P] Test boundary enforcement
T042 [P] Test prompt injection
T044 [P] Add chat link to dashboard
T045 [P] Style chat interface
```

---

## Parallel Example: Foundational Phase

```bash
# After T005-T008 (database), these can run in parallel:
Task T010: "Create agent factory function in backend/app/ai/agent.py"
Task T011: "Add ChatRequest and ChatResponse schemas to backend/app/schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T016)
3. Complete Phase 3: User Story 1 (T017-T023)
4. **STOP and VALIDATE**: Test task creation via chat
5. Deploy MVP if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Task Creation) → Test → Deploy MVP!
3. Add US2 (Task Viewing) + US6 (Persistence) → Test → Deploy
4. Add US3 (Completion) → Test → Deploy
5. Add US4 (Deletion) + US5 (Modification) → Test → Deploy
6. Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational done:
   - Developer A: US1 (Task Creation) + Frontend
   - Developer B: US2 (Task Viewing) + US6 (Persistence)
3. After US1 complete:
   - Developer A: US3 (Completion)
   - Developer B: US4 (Deletion) + US5 (Modification)
4. Final: Both on Polish phase

---

## Task Summary

| Phase | Task Count | Priority |
|-------|------------|----------|
| Phase 1: Setup | 4 | Required |
| Phase 2: Foundational | 14 | Required |
| Phase 3: US1 (Create) | 7 | P1 - MVP |
| Phase 4: US2 (View) | 3 | P1 |
| Phase 5: US6 (Persist) | 5 | P1 |
| Phase 6: US3 (Complete) | 3 | P2 |
| Phase 7: US4 (Delete) | 3 | P3 |
| Phase 8: US5 (Update) | 3 | P3 |
| Phase 9: Polish | 19 | Final |
| Phase 10: Task Numbering | 12 | P1 |
| **Total** | **73** | |

### Per User Story Task Count

| User Story | Tasks | Independent Test |
|------------|-------|------------------|
| US1: Task Creation | 7 | "Add a task to buy groceries" |
| US2: Task Viewing | 3 | "What tasks do I have?" |
| US3: Task Completion | 3 | "Mark task 3 as done" |
| US4: Task Deletion | 3 | "Delete task 2" |
| US5: Task Modification | 3 | "Change task 4 title to..." |
| US6: Persistence | 5 | Refresh page, history visible |

### MVP Scope (Recommended)

**Minimum for demo**: Phases 1-3 (23 tasks)
- Setup + Foundational + US1 (Task Creation)
- Users can create tasks via chat
- Demonstrates AI + MCP integration

**Full P1 Features**: Phases 1-5 (31 tasks)
- Adds task viewing and conversation persistence
- Complete conversational task management experience

---

## Phase 10: User-Specific Task Numbering (Priority: P1)

**Goal**: Each user's tasks are numbered independently (1, 2, 3...) instead of using global database IDs

**Problem Solved**: Previously, if User 1 created 3 tasks (IDs 1, 2, 3), User 2's first task would get ID 4. Now each user starts from 1.

**Independent Test**: User 2 creates their first task, it gets task_number=1 (not a high global ID)

### Database Changes

- [x] T062 Add task_number column to Task model in backend/app/models.py
- [x] T063 Create Alembic migration for task_number with per-user sequential numbering
- [x] T064 Migration populates existing tasks with sequential task_number per user

### Backend Implementation

- [x] T065 Update backend/app/schemas.py TaskResponse to include task_number field
- [x] T066 Add _get_next_task_number helper function in backend/app/routers/tasks.py
- [x] T067 Update create_task endpoint to assign task_number when creating tasks
- [x] T068 Update all task response builders to include task_number in response

### AI Tools Update

- [x] T069 Update add_task tool to assign task_number using get_next_task_number helper
- [x] T070 Update list_tasks tool to return task_number instead of global id
- [x] T071 Update complete_task tool to lookup by task_number instead of id
- [x] T072 Update delete_task tool to lookup by task_number instead of id
- [x] T073 Update update_task tool to lookup by task_number instead of id

**Checkpoint**: Chatbot uses user-specific task numbers

**Manual Test**:
1. Create User A and add 3 tasks via chat → Tasks should be #1, #2, #3
2. Create User B and add 1 task via chat → Task should be #1 (not #4)
3. User A types "Show my tasks" → See tasks #1, #2, #3
4. User B types "Complete task 1" → Only User B's task #1 is affected
5. User A's tasks remain unchanged

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Manual test procedures in quickstart.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies
