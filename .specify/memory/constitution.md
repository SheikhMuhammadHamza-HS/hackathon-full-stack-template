<!--
Sync Impact Report:
- Version Change: 2.0.0 → 3.0.0 (MAJOR)
- Rationale: Adding fundamentally new Intelligence Layer with MCP/Agents architecture alongside existing Web App layer
- Modified Principles:
  * I. "Production-Ready Web Architecture" → Expanded to include Intelligence Layer with MCP bridge
  * II. "Spec-Driven Development" (UNCHANGED - still non-negotiable)
  * IV. "Data Model Integrity" → Expanded to include Conversation and Message tables for stateless AI
  * VIII. "User Isolation and Data Security" → Expanded to include Agent isolation and tool safety
- New Principles Added:
  * XIII. MCP-First Architecture (NEW)
  * XIV. Stateless AI with Database Persistence (NEW)
  * XV. Agentic Workflow (NEW)
  * XVI. Agent Security and Instruction Safety (NEW)
- Removed Sections: None (Phase II principles remain valid for Web App layer)
- Templates Requiring Updates:
  ✅ plan-template.md (Constitution Check must reference MCP, Agent, ChatKit principles)
  ✅ spec-template.md (Requirements must include chat interface, MCP tools, conversation persistence)
  ✅ tasks-template.md (Tasks must include MCP server setup, Agent configuration, ChatKit integration, stateless conversation testing)
- Follow-up TODOs:
  * Verify OpenAI Domain Allowlist configured (deployment step)
  * Document MCP tool registration process in quickstart
  * Add Agent instruction examples to templates
-->

# Phase III AI-Powered Todo Chatbot Constitution

## Phase Transition Context

**Phase I (Console App)**: Established fundamental CRUD operations, clean code practices, and spec-driven development methodology using in-memory storage and console interface.

**Phase II (Full-Stack Web App)**: Transitioned to production-ready, multi-user web application with persistent database, authentication, REST API, responsive UI, and cloud deployment. Built the foundational Web App Layer.

**Phase III (AI-Powered Chatbot)**: Introduces the **Intelligence Layer** on top of the Web App Layer. Users can now interact with the todo system via natural language through an AI chatbot, while traditional GUI interactions remain fully functional. The Intelligence Layer uses **Model Context Protocol (MCP)** as the bridge between AI agents and the Web App Layer's CRUD operations.

**Why This Transition Matters**: Modern applications are evolving from click-based interfaces to conversational AI interfaces. Phase III demonstrates the "Architecture of Intelligence" where AI agents orchestrate existing business logic through standardized protocols (MCP), enabling natural language interactions without rewriting core functionality. This represents the future of human-computer interaction.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                    │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ ChatKit UI   │ ←→ │ OpenAI Agent │ ←→ │ MCP Tools │ │
│  │  (Frontend)  │    │     SDK      │    │  (Bridge) │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────┬───────────────────────┘
                                  │ MCP Protocol
                                  ▼
┌─────────────────────────────────────────────────────────┐
│                      WEB APP LAYER                       │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  Next.js UI  │ ←→ │  FastAPI     │ ←→ │ PostgreSQL│ │
│  │ (Traditional)│    │   (REST)     │    │   (Neon)  │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────────────────────────────┘

Old Flow (Phase II): User Click → API Endpoint → DB Query → Response
New Flow (Phase III): User Message → ChatKit → API (Save) → Agent → MCP Tools → DB Query → AI Response
```

**Key Principle**: The Intelligence Layer does NOT bypass the Web App Layer. MCP Tools are thin wrappers around existing CRUD functions, ensuring both GUI and AI paths use the same validated business logic.

## Core Principles (Phase I & II - Still Valid)

All principles from Phase II remain in effect for the Web App Layer. Phase III adds new principles for the Intelligence Layer while preserving the foundation.

### I. Production-Ready Web Architecture with Intelligence Layer

Phase III extends the three-layer architecture (frontend, backend, database) with a fourth Intelligence Layer. The Web App Layer handles traditional GUI interactions; the Intelligence Layer handles natural language interactions. **MCP (Model Context Protocol)** serves as the standardized bridge between these layers.

**Rationale**: Modern applications must support both traditional and conversational interfaces. The Intelligence Layer architecture allows adding AI capabilities without rewriting existing code. MCP provides a vendor-neutral standard (like REST for web services) for AI-to-application integration, preventing vendor lock-in and enabling tool reusability.

**Rules**:
- Web App Layer rules from Phase II remain unchanged (monorepo, REST API, stateless backend, Neon PostgreSQL)
- Intelligence Layer MUST communicate with Web App Layer exclusively via MCP Tools (no direct database access)
- MCP Tools MUST be thin wrappers around existing CRUD functions (no business logic duplication)
- Agent MUST be stateless (conversation history fetched from database on every request)
- ChatKit frontend MUST authenticate users via same JWT tokens as traditional UI
- Both GUI and AI paths MUST enforce identical security (user isolation, JWT validation)
- Database MUST store conversation history (no in-memory session state)

### II. Spec-Driven Development (NON-NEGOTIABLE)

All code MUST be preceded by written specifications. No implementation may begin without approved spec.md, plan.md, and tasks.md files. This principle is even more critical in Phase III due to the complexity of coordinating Web App Layer, Intelligence Layer, and MCP bridge.

**Rationale**: AI agent behavior is non-deterministic and requires rigorous specification of boundaries, tool definitions, and safety constraints. MCP tool interfaces must be precisely documented as contracts between layers. Spec-driven development prevents architectural misalignment between GUI and AI paths.

**Rules**:
- All Phase II spec-driven rules remain in effect
- Spec MUST document MCP tool signatures (parameters, return types, error handling)
- Spec MUST define Agent system instructions (boundaries, safety constraints, persona)
- Spec MUST specify conversation persistence requirements (what data stored, retention)
- Spec MUST include natural language test scenarios (sample user messages and expected agent behavior)
- MCP tool changes MUST be documented in spec before implementation (breaking changes require version bump)
- Agent instruction changes MUST be reviewed for safety implications

### III. Test-First Development

Tests MUST be written or defined before implementation code. For Phase III, this includes conversational AI testing (natural language commands), MCP tool testing (direct function calls), multi-user safety testing (agent cannot access other users' data), and statelessness testing (conversation persists after server restart).

**Rationale**: AI systems are harder to test than deterministic systems due to non-deterministic language model outputs. Test-first development forces explicit definition of success criteria for natural language interactions, MCP tool behavior, and agent safety boundaries.

**Rules**:
- All Phase II testing rules remain in effect
- MCP Tools MUST be testable via direct function calls (unit test style)
- Agent behavior MUST be testable via sample messages with expected tool calls
- Conversation persistence MUST be tested (send message, restart server, verify history loaded)
- Multi-user safety MUST be tested (User A's agent cannot access User B's tasks)
- Agent boundary testing MUST be included (refuse off-topic requests, reject malicious instructions)
- Tool error handling MUST be tested (invalid task_id, missing parameters, database errors)
- Natural language test scenarios MUST cover: add task, list tasks, complete task, delete task, update task, ambiguous requests, out-of-scope requests

### IV. Data Model Integrity with User Isolation and Conversation Persistence

Database schema MUST maintain referential integrity, enforce user isolation, and support stateless AI conversations. Phase III adds Conversation and Message tables to persist chat history. Every conversation MUST be tied to a user_id. All queries MUST filter by authenticated user_id.

**Rationale**: Stateless AI architecture (required for horizontal scaling) demands database-backed conversation history. Conversation data is as sensitive as task data and requires the same isolation guarantees. Message history enables context-aware AI responses and debugging/auditing of agent behavior.

**Rules**:
- All Phase II data model rules remain in effect (User, Task tables)
- Conversation table MUST include: id (UUID, PK), user_id (FK to users.id, indexed), title (optional), created_at (timestamp), updated_at (timestamp)
- Message table MUST include: id (int, PK, auto), conversation_id (FK to conversations.id, indexed), role (enum: 'user' or 'assistant'), content (text), tool_calls (JSONB, nullable), created_at (timestamp, indexed)
- Every conversation MUST be scoped to authenticated user_id (no cross-user access)
- Agent MUST fetch conversation history from database before processing new message
- Message storage MUST happen in single database transaction (user message + agent response atomic)
- Conversation history MUST be immutable (no updates/deletes, append-only for auditability)
- Use Alembic migration to add Conversation and Message tables
- Index conversations.user_id and messages.conversation_id for query performance
- Index messages.created_at for chronological retrieval

### V. Input Validation and Error Handling

All user input MUST be validated at BOTH frontend and backend. API endpoints MUST use Pydantic models for request validation. Errors MUST be handled gracefully with proper HTTP status codes and user-friendly messages. Phase III extends this to include Agent instruction validation and MCP tool parameter validation.

**Rationale**: AI agents can generate unexpected inputs to MCP tools (hallucinated task IDs, malformed parameters). Tool validation prevents database errors and provides clear feedback to the agent for self-correction. Agent instruction validation prevents prompt injection attacks.

**Rules**:
- All Phase II validation rules remain in effect
- MCP Tools MUST validate all parameters (required fields, types, length limits, format)
- Tool validation errors MUST return structured error objects (not raise exceptions)
- Agent system instructions MUST be sanitized (no user-controlled content injection)
- Chat messages MUST be validated (max length 10,000 characters, no binary data)
- Tool responses MUST be JSON-serializable (agent SDK requirement)
- Frontend MUST validate chat input (non-empty, reasonable length, no code injection attempts)

### VI. Clean Code and Multi-Language Standards

Code MUST follow language-specific conventions and clean code principles. Backend (Python) follows PEP 8. Frontend (TypeScript) follows strict TypeScript standards. Functions MUST be small, focused, and well-named. Phase III code must be readable without excessive comments.

**Rationale**: AI-related code (agent instructions, tool definitions) is harder to understand due to non-deterministic behavior. Exceptionally clear code standards are critical for debugging agent issues and maintaining tool definitions.

**Rules**:
- All Phase II code quality rules remain in effect
- MCP Tools MUST have clear docstrings (parameters, returns, side effects, error conditions)
- Agent system instructions MUST be version-controlled as separate files (not inline strings)
- Tool functions MUST follow single-responsibility principle (one tool = one CRUD operation)
- Chat endpoint MUST be well-factored (separate concerns: auth, persistence, agent invocation, error handling)
- Tool naming MUST be agent-friendly (descriptive, follows verb_noun pattern: add_task, list_tasks)

### VII. Windows via WSL 2 Only

Windows users MUST use Windows Subsystem for Linux (WSL 2) with Ubuntu. Direct Windows execution is not supported for this project.

**Rationale**: Same as Phase II. OpenAI SDKs, MCP servers, and agent tooling are primarily developed/tested on Linux. WSL 2 ensures compatibility.

**Rules**:
- All Phase II WSL rules remain in effect
- OpenAI SDK MUST be installed in WSL Python environment
- MCP server MUST run in WSL (not native Windows Python)

### VIII. User Isolation and Data Security

Every API endpoint MUST require JWT authentication. The authenticated user_id from the JWT MUST match the {user_id} in the URL path. Users MUST only access their own data. Phase III extends this to include Agent-level isolation: agents MUST be context-injected with user_id and MCP tools MUST automatically filter by that user_id.

**Rationale**: AI agents are potential attack vectors for privilege escalation. An agent serving User A must never be tricked (via prompt injection or tool misuse) into accessing User B's data. Defense-in-depth requires isolation at API layer, Agent context layer, and Database query layer.

**Rules**:
- All Phase II security rules remain in effect (JWT validation, user_id matching, database filtering)
- Agent MUST be instantiated with user_id in context (not passed as tool parameter)
- MCP Tools MUST read user_id from agent context (not from function arguments)
- Tools MUST reject any attempt to override context user_id
- Agent system instructions MUST NOT include sensitive data (no usernames, emails, task content in prompt)
- Tool responses MUST NOT leak cross-user data (e.g., task counts should be user-scoped)
- Chat endpoint MUST validate JWT before creating agent instance
- Agent errors MUST NOT expose internal system details (sanitize stack traces)

### IX. RESTful API Design

API MUST follow RESTful conventions with consistent URL structure, proper HTTP methods, JSON payloads, and predictable behavior. Phase III adds chat endpoint following REST principles: POST /api/{user_id}/chat.

**Rationale**: Chat endpoint is part of the REST API surface and must follow the same conventions for consistency, tooling compatibility, and developer experience.

**Rules**:
- All Phase II REST rules remain in effect
- Chat endpoint: POST /api/{user_id}/chat
- Request body: `{"message": "string", "conversation_id": "uuid or null"}`
- Response: `{"reply": "string", "conversation_id": "uuid", "tool_calls": [...]}`
- HTTP status codes: 200 (success), 400 (invalid message), 401 (unauthorized), 403 (user_id mismatch), 500 (agent error)
- Streaming responses optional (return full response by default, stream only if needed)

### X. Authentication-First Approach

Authentication and authorization MUST be designed and implemented BEFORE building features. Better Auth handles user management; JWT tokens authenticate API requests. Phase III chat endpoint MUST require authentication before agent invocation.

**Rationale**: AI agents amplify security risks. Unauthenticated agent access could enable abuse (spamming, prompt injection testing, resource exhaustion). Authentication must be the first line of defense.

**Rules**:
- All Phase II auth rules remain in effect
- Chat endpoint MUST validate JWT before any processing
- ChatKit frontend MUST pass JWT token in requests
- Agent MUST NOT be instantiated without authenticated user_id
- Rate limiting MUST be applied to chat endpoint (prevent abuse)

### XI. Mobile-First Responsive Design

UI MUST be responsive and functional on mobile devices (375px minimum width) and desktop (1024px+). Phase III adds ChatKit interface which must also be responsive.

**Rationale**: Chat interfaces are commonly used on mobile. ChatKit UI must adapt to small screens without losing functionality.

**Rules**:
- All Phase II responsive design rules remain in effect
- ChatKit component MUST render correctly on mobile (375px)
- Chat input MUST be usable on mobile keyboards
- Message bubbles MUST fit within mobile viewport (no horizontal scroll)
- Chat history MUST be scrollable on mobile

### XII. Cloud-Native Deployment

Application MUST be designed for cloud deployment from the start. Frontend deployed on Vercel, backend on Railway/Render, database on Neon. Phase III adds OpenAI API key and domain configuration requirements.

**Rationale**: ChatKit requires domain allowlist configuration in OpenAI dashboard. Production deployment must include these setup steps.

**Rules**:
- All Phase II deployment rules remain in effect
- Environment variables MUST include: `OPENAI_API_KEY` (for agent SDK), `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (for ChatKit frontend)
- OpenAI dashboard MUST be configured with allowlisted domains (Vercel domain)
- Backend MUST use OPENAI_API_KEY from environment (never hardcoded)
- Frontend MUST use NEXT_PUBLIC_OPENAI_DOMAIN_KEY for ChatKit initialization

## Phase III Principles (Intelligence Layer)

### XIII. MCP-First Architecture (NEW)

All task operations (Add, List, Complete, Delete, Update) MUST be exposed as MCP Tools. The Agent MUST NOT access the database directly. MCP Tools are the ONLY interface between Intelligence Layer and Web App Layer. This enforces separation of concerns and enables tool reusability across multiple agents.

**Rationale**: MCP (Model Context Protocol) is the industry standard for connecting AI agents to applications, created by Anthropic. MCP-first architecture ensures the Intelligence Layer remains modular, testable, and vendor-neutral. Tools can be reused by future agents, tested independently, and evolved without changing agent logic. This prevents the "spaghetti integration" pattern common in early AI applications.

**Rules**:
- MUST use Official MCP SDK (Python) for tool definition
- Every CRUD operation MUST have a corresponding MCP Tool: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- Tools MUST be thin wrappers (5-10 lines) around existing CRUD functions
- Tools MUST read user_id from agent context (not function parameters)
- Tools MUST return structured dictionaries (not raw database objects)
- Tools MUST handle errors gracefully (return error dict, not raise exceptions to agent)
- Tool docstrings MUST be agent-friendly (clear description, parameter types, example usage)
- Tool naming MUST follow verb_noun pattern (add_task, not create_task or task_add)
- Tool signatures MUST be stable (breaking changes require new tool version)
- Tools MUST be registered with FastAPI MCP server (not standalone scripts)
- NO direct database imports in agent code (agent only sees tool interface)

**MCP Tool Example Pattern**:
```python
from mcp import tool

@tool
def add_task(title: str, description: str = None) -> dict:
    """
    Add a new task for the authenticated user.

    Args:
        title: Task title (1-200 characters, required)
        description: Task description (optional, max 1000 chars)

    Returns:
        {"success": True, "task": {"id": 123, "title": "...", ...}}
        OR {"success": False, "error": "Title too long"}
    """
    user_id = get_agent_context("user_id")  # From agent context, not parameter
    # Thin wrapper around existing CRUD function
    return create_task_internal(user_id, title, description)
```

### XIV. Stateless AI with Database Persistence (NEW)

The server MUST hold NO conversation state in memory. All conversation history MUST be fetched from the database on every request. Agents MUST be instantiated fresh for each message (no persistent agent objects). This enables horizontal scaling and prevents memory leaks.

**Rationale**: Stateful AI servers (storing conversation in memory) cannot scale horizontally, waste memory on idle conversations, and lose history on crashes. Database-backed stateless architecture is the same pattern that enables REST API scaling. Conversation history in database enables auditability, debugging, and multi-device continuity.

**Rules**:
- NO global or class-level agent instances (must instantiate per-request)
- NO in-memory conversation storage (no session dictionaries, no cache)
- Chat endpoint MUST fetch conversation history from database before calling agent
- Agent MUST receive full conversation history as input (not just latest message)
- Conversation history MUST be immutable append-only log (no message updates/deletes)
- Server restart MUST NOT lose conversation history (verify with test)
- Each request MUST be independent (no assumptions about previous requests)
- Database transaction MUST be atomic (user message + agent response saved together or not at all)
- Conversation retention: keep all messages (no auto-deletion for Phase III; add retention policy in future if needed)

**Stateless Pattern**:
```python
@router.post("/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    # 1. Fetch history from DB (stateless - no memory of previous calls)
    history = await get_conversation_history(request.conversation_id)

    # 2. Instantiate fresh agent with history
    agent = create_agent(user_id=user_id, history=history)

    # 3. Process message
    response = await agent.run(request.message)

    # 4. Save to DB (persist for next request)
    await save_message(user_id, request.message, response)

    # 5. Return (agent discarded, no state retained)
    return {"reply": response.text, "conversation_id": conversation_id}
```

### XV. Agentic Workflow (NEW)

DO NOT write "if/else" parsers for natural language commands. Use OpenAI Agents SDK to interpret user intent and select appropriate MCP tools. The agent decides which tool to call based on natural language understanding, not hardcoded keyword matching.

**Rationale**: Keyword-based parsing (if "add" in message: call add_task) is brittle and does not scale. AI agents use large language models for robust intent recognition, handling synonyms, typos, context, and complex queries. The Agents SDK handles function calling, error recovery, and multi-turn conversations automatically.

**Rules**:
- MUST use OpenAI Agents SDK for agent orchestration
- Agent system instructions MUST define role and capabilities (not parsing logic)
- NO keyword matching or regex parsing in chat endpoint
- NO manual tool selection logic (let agent SDK decide)
- Agent MUST use function calling to invoke MCP tools (not hardcoded branching)
- System instructions MUST define boundaries (what agent can/cannot do)
- System instructions MUST be stored in separate file (not inline string)
- Agent model MUST be GPT-4o or better (required for reliable function calling)
- Conversation history MUST be passed to agent for context-aware responses
- Agent errors MUST be handled gracefully (retry once, then fallback message)

**System Instructions Pattern**:
```python
SYSTEM_INSTRUCTIONS = """
You are TodoBot, a helpful AI assistant for managing todo tasks.

You can help users:
- Add new tasks ("Add a task to buy groceries")
- View their task list ("What tasks do I have?")
- Mark tasks as complete ("Mark task 3 as done")
- Delete tasks ("Remove the grocery task")
- Update task details ("Change task 2 title to 'Call dentist'")

You MUST:
- Use provided tools for all task operations (never hallucinate task data)
- Be concise and friendly
- Confirm actions after completion
- Ask clarifying questions if request is ambiguous

You MUST NOT:
- Answer questions unrelated to todo tasks
- Access or modify other users' data
- Execute system commands or access files
- Generate code or perform calculations
"""
```

### XVI. Agent Security and Instruction Safety (NEW)

System prompts MUST define boundaries. Agent MUST refuse off-topic requests. Tools MUST enforce user isolation. Agents MUST NOT be susceptible to prompt injection attacks. Agent instructions MUST NOT contain sensitive user data.

**Rationale**: AI agents are attack surfaces. Prompt injection (user message that overrides system instructions) can trick agents into bypassing security. Agent isolation (cannot access other users' tools) and tool validation (cannot accept malicious parameters) provide defense-in-depth.

**Rules**:
- System instructions MUST explicitly define what agent can and cannot do
- Agent MUST refuse requests outside of task management domain
- System instructions MUST be stored server-side (not client-controlled)
- Agent MUST NOT accept system instruction overrides from user messages
- User messages MUST be sanitized (no attempts to inject instructions like "Ignore previous instructions")
- Tools MUST validate user_id comes from agent context (not user message)
- Tool responses MUST NOT leak cross-user data (e.g., total task count across all users)
- Agent errors MUST be sanitized before returning to user (no internal stack traces)
- Rate limiting MUST be enforced on chat endpoint (prevent abuse)
- Agent logging MUST capture user_id and conversation_id for audit trail

**Instruction Safety Pattern**:
```python
# GOOD: User context from JWT, not user message
agent = Agent(
    instructions=SYSTEM_INSTRUCTIONS,
    tools=[add_task, list_tasks, ...],
    context={"user_id": authenticated_user_id}  # From JWT, trusted
)

# BAD: User could inject malicious user_id
agent = Agent(
    instructions=SYSTEM_INSTRUCTIONS,
    tools=[add_task, list_tasks, ...],
    context={"user_id": request.json["user_id"]}  # From user, untrusted
)
```

## Scope and Constraints

### In Scope (Phase III)
- All Phase II scope remains (GUI-based CRUD operations)
- Natural language chat interface via ChatKit
- Five MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- Conversation persistence (conversations and messages tables)
- Stateless AI architecture (history fetched from database)
- OpenAI Agents SDK integration
- Multi-user safety (agents cannot cross user boundaries)
- Agent boundary enforcement (refuse off-topic requests)
- Chat endpoint: POST /api/{user_id}/chat
- ChatKit frontend component integration
- OpenAI domain allowlist configuration

### Out of Scope (Future Phases or Explicitly Excluded)
- Multi-turn clarification dialogs (agent asks follow-up questions)
- Conversation summarization or compression
- Voice input/output
- File attachments in chat
- Task search/filtering via natural language beyond basic status
- Task priorities, categories, tags, due dates via chat
- Collaborative features (shared tasks, teams) via chat
- Scheduled task reminders via chat
- Integration with external services (calendar, email) via chat
- Custom agent personas or multiple agents
- Agent fine-tuning or training
- Streaming responses (return full response immediately)
- Rich message formatting (markdown, code blocks)

### Technology Constraints (Phase III Additions)
- All Phase II constraints remain
- Intelligence Layer: OpenAI Agents SDK (Python), Official MCP SDK (Python), ChatKit (React)
- AI Model: GPT-4o or better (required for function calling)
- MCP Server: Integrated with FastAPI (not standalone server)
- NO LangChain or other agent frameworks (use official OpenAI SDK)
- NO custom MCP implementations (use official SDK)
- NO agent memory/context storage beyond conversation history in database

## Project Structure (Phase III Additions)

Phase III adds Intelligence Layer components to the Phase II structure:

```
hackathon-full-stack-template/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # This file (v3.0.0)
│   └── templates/                   # SpecKit Plus templates
├── specs/
│   └── ai-chatbot/                  # Phase III specification
│       ├── spec.md                  # Chatbot feature specification
│       ├── plan.md                  # MCP/Agent implementation plan
│       └── tasks.md                 # Phase III task breakdown
├── frontend/
│   ├── app/
│   │   ├── chat/                    # NEW: Chat page
│   │   │   └── page.tsx             # ChatKit integration
│   │   └── dashboard/
│   │       └── page.tsx             # Add chat button/widget
│   ├── components/
│   │   ├── ChatInterface.tsx        # NEW: ChatKit wrapper
│   │   ├── ChatMessage.tsx          # NEW: Message component
│   │   └── ...                      # Existing components
│   └── .env.local                   # Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY
├── backend/
│   ├── app/
│   │   ├── ai/                      # NEW: Intelligence Layer
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # Agent initialization
│   │   │   ├── tools.py             # MCP tool definitions
│   │   │   └── instructions.py      # System instructions
│   │   ├── routers/
│   │   │   ├── chat.py              # NEW: Chat endpoint
│   │   │   └── ...                  # Existing routers
│   │   ├── models.py                # Add Conversation, Message models
│   │   └── ...                      # Existing files
│   ├── alembic/versions/            # Add migration for conversation tables
│   └── .env                         # Add OPENAI_API_KEY
├── .claude/
│   └── skills/
│       ├── chatkit/                 # NEW: ChatKit skill
│       ├── mcp/                     # NEW: MCP skill
│       ├── openai-agents-sdk/       # NEW: Agents SDK skill
│       └── ...                      # Existing skills
└── ...
```

## Development Workflow (Phase III Additions)

### Specification Phase
- All Phase II steps remain
- Spec MUST include MCP tool signatures with examples
- Spec MUST define agent system instructions
- Spec MUST include natural language test scenarios
- Spec MUST document conversation persistence requirements

### Planning Phase
- All Phase II steps remain
- Plan MUST document MCP server architecture
- Plan MUST explain stateless conversation design
- Plan MUST address agent security and isolation
- Plan MUST document OpenAI API setup and domain configuration

### Task Phase
- All Phase II steps remain
- Tasks MUST include: MCP tool implementation, Agent configuration, ChatKit frontend integration, Conversation database schema, Statelessness testing
- Each task MUST include natural language test scenarios

### Implementation Phase
- All Phase II steps remain
- MCP tools implemented before agent configuration
- Agent tested with direct tool calls before ChatKit integration
- Conversation persistence implemented before multi-turn testing

### Validation Phase
- All Phase II tests remain
- Phase III additional tests:
  1. MCP Tool Testing: Test each tool via direct function call (unit test style)
  2. Agent Behavior Testing: Test with sample messages, verify expected tool calls
  3. Conversation Persistence Testing: Send message, restart server, verify history loaded correctly
  4. Multi-User Safety Testing: Verify User A's agent cannot access User B's tasks
  5. Agent Boundary Testing: Verify agent refuses off-topic requests, rejects instruction overrides
  6. Natural Language Coverage: Test add, list, complete, delete, update via various phrasings
  7. Statelessness Testing: Verify no in-memory state (restart server mid-conversation)

## Success Criteria (Phase III)

Phase III is complete when ALL Phase II criteria remain met AND the following are true:

### Functional Completeness
- ✅ Chat UI visible and functional (ChatKit integrated)
- ✅ User can add tasks via natural language ("Add a task to buy milk")
- ✅ User can list tasks via natural language ("What tasks do I have?")
- ✅ User can complete tasks via natural language ("Mark task 3 as done")
- ✅ User can delete tasks via natural language ("Delete the grocery task")
- ✅ User can update tasks via natural language ("Change task 2 title to 'Call dentist'")
- ✅ Conversation history persists after page reload (database storage working)
- ✅ Agent correctly uses MCP tools (verified via logs/test)
- ✅ Agent refuses off-topic requests ("What's the weather?" -> "I only help with tasks")

### Intelligence Layer Quality
- ✅ Five MCP tools implemented: add_task, list_tasks, complete_task, delete_task, update_task
- ✅ Tools are thin wrappers around existing CRUD functions (5-10 lines each)
- ✅ Tools read user_id from agent context (not function parameters)
- ✅ Tools validate all parameters and return structured responses
- ✅ Agent uses OpenAI Agents SDK (no manual intent parsing)
- ✅ Agent system instructions stored in separate file
- ✅ Agent instantiated per-request (no persistent agent objects)
- ✅ No in-memory conversation state (stateless architecture verified)

### Conversation Persistence Quality
- ✅ Conversation table exists with user_id foreign key
- ✅ Message table exists with conversation_id foreign key
- ✅ Messages stored atomically (user + assistant message in single transaction)
- ✅ Conversation history fetched from database on every request
- ✅ Conversation history immutable (append-only, no updates/deletes)
- ✅ Indexes on user_id, conversation_id, created_at
- ✅ Server restart does not lose conversation history (tested)

### Security Quality
- ✅ All Phase II security criteria remain met
- ✅ Agent cannot access other users' data (multi-user safety tested)
- ✅ Agent context includes authenticated user_id (from JWT)
- ✅ MCP tools validate user_id from context (not parameters)
- ✅ Agent refuses instruction override attempts (boundary tested)
- ✅ Agent errors sanitized (no internal details leaked)
- ✅ Chat endpoint rate-limited (prevent abuse)
- ✅ OpenAI API key stored in environment variable (not hardcoded)

### Frontend Quality
- ✅ ChatKit component integrated into Next.js app
- ✅ Chat interface responsive on mobile (375px) and desktop (1024px+)
- ✅ Chat input validates message before sending
- ✅ Chat displays loading state during agent processing
- ✅ Chat displays agent responses with proper formatting
- ✅ Chat persists across page navigation (conversation ID maintained)
- ✅ ChatKit authenticated with same JWT as traditional UI

### Testing
- ✅ MCP tools tested via direct function calls (all pass)
- ✅ Agent tested with natural language scenarios (add, list, complete, delete, update)
- ✅ Conversation persistence tested (server restart, history loaded)
- ✅ Multi-user safety tested (User A cannot access User B's tasks via agent)
- ✅ Agent boundary tested (refuses off-topic requests, rejects instruction overrides)
- ✅ Statelessness tested (no memory leaks, no stale state)
- ✅ Natural language coverage tested (multiple phrasings for same intent)

### Documentation
- ✅ All Phase II documentation remains complete
- ✅ spec.md includes MCP tool signatures and natural language test scenarios
- ✅ plan.md includes MCP/Agent architecture and statelessness design
- ✅ tasks.md includes Intelligence Layer tasks marked complete
- ✅ README includes OpenAI API setup instructions
- ✅ Environment variable documentation includes OPENAI_API_KEY and NEXT_PUBLIC_OPENAI_DOMAIN_KEY

### Deployment
- ✅ All Phase II deployment criteria remain met
- ✅ Backend deployed with OPENAI_API_KEY configured
- ✅ Frontend deployed with NEXT_PUBLIC_OPENAI_DOMAIN_KEY configured
- ✅ OpenAI dashboard configured with allowlisted domains
- ✅ Chat endpoint accessible and functional in production
- ✅ Conversation history persists in production database

## Governance

### Amendment Process
Constitution changes MUST be documented with:
- Clear rationale for the change
- Version increment following semantic versioning
- Update to dependent templates (spec, plan, tasks)
- Sync Impact Report (HTML comment at top of file)
- Approval before taking effect

### Version Semantics
- MAJOR: Principle removal, fundamental architectural change, scope redefinition (e.g., Phase II → Phase III)
- MINOR: New principle added, significant expansion of existing principle
- PATCH: Clarifications, examples, formatting improvements, typo fixes

### Compliance
- All spec.md files MUST reference relevant constitution principles
- All plan.md files MUST include "Constitution Check" section validating adherence
- All code reviews MUST verify constitutional compliance (especially security principles)
- PHR (Prompt History Records) MUST document any principle violations with justification
- Security principles (VIII, XIII, XIV, XV, XVI) are NON-NEGOTIABLE—no exceptions without explicit written approval

### Non-Compliance Handling
If a principle violation is necessary (e.g., temporarily disable tool validation for debugging):
1. Document in plan.md "Complexity Tracking" or "Security Exceptions" section
2. Provide clear justification for why violation is needed
3. Explain why compliant alternatives were insufficient
4. Define remediation steps (how to restore compliance)
5. Get explicit user approval before proceeding
6. Record decision in ADR if architecturally significant
7. Add TODO comments in code marking the violation
8. Ensure violation is not deployed to production (local dev only)

### Compliance Review Checklist (Phase III Additions)
Before marking Phase III complete, verify:
- [ ] Every CRUD operation has corresponding MCP tool (Principle XIII)
- [ ] No in-memory conversation state (Principle XIV)
- [ ] Agent uses OpenAI SDK, no manual parsing (Principle XV)
- [ ] Agent context includes user_id from JWT (Principle XVI)
- [ ] Tools read user_id from context, not parameters (Principle XIII)
- [ ] Conversation and Message tables exist with proper foreign keys (Principle IV)
- [ ] Agent refuses off-topic requests (Principle XVI)
- [ ] Server restart does not lose conversation history (Principle XIV)
- [ ] Multi-user safety tested (agent cannot access other users' data) (Principle VIII, XVI)
- [ ] OpenAI API key in environment variable (Principle XII)
- [ ] ChatKit authenticated with JWT (Principle X)

**Version**: 3.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-21
