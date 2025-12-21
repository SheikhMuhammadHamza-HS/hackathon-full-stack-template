---
id: 0002
title: Update Constitution Phase III
stage: constitution
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-user-auth
user: SheikhMuhammadHamza-HS
command: /sp.constitution
labels: ["phase-iii", "ai-chatbot", "mcp", "agents-sdk", "constitution", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .claude/skills/chatkit/skill.md
tests:
  - Manual review of Phase III principles
  - Verification of MCP-First Architecture principle
  - Validation of Stateless AI principle
---

## Prompt

You are updating the Constitution file from Phase II to Phase III of the Todo application hackathon project.

## Context
Phase II (Full-Stack Web App) is complete. We are now transitioning to **Phase III: AI-Powered Todo Chatbot**.
The goal is to evolve the application from a GUI-based CRUD app to an **AI-Native System** where users interact via natural language.

## What Changed from Phase II to Phase III

### Technology Evolution
**Phase II:**
- Standard REST API
- Click-based UI interaction
- Logic hardcoded in API endpoints

**Phase III (Additions):**
- **AI Interface:** OpenAI ChatKit (Frontend)
- **AI Logic:** OpenAI Agents SDK (Backend)
- **Tooling Standard:** Official MCP (Model Context Protocol) SDK
- **Architecture:** Stateless Chat Server (State persists in DB, not memory)

### Architecture Changes
**Old Flow:** User Click → API Endpoint → DB Query → Response
**New Flow:** User Message → ChatKit → API (Save Msg) → Agent → **MCP Tools** → DB Query → AI Response

[Full requirements as provided in command args...]

## Response snapshot

Constitution successfully updated from v2.0.0 to v3.0.0 (MAJOR version bump).

**Key Changes:**

1. **Four New Principles Added** (XIII-XVI):
   - XIII. MCP-First Architecture: All CRUD operations exposed as MCP tools
   - XIV. Stateless AI with Database Persistence: No in-memory conversation state
   - XV. Agentic Workflow: Use OpenAI SDK, no manual intent parsing
   - XVI. Agent Security and Instruction Safety: Boundary enforcement and prompt injection protection

2. **Architecture Layer Added**:
   - Intelligence Layer (ChatKit + Agent + MCP) sits on top of Web App Layer
   - MCP serves as standardized bridge between layers
   - Both GUI and AI paths use same business logic via MCP tools

3. **Data Model Expanded**:
   - Added Conversation table (user_id, created_at, updated_at)
   - Added Message table (conversation_id, role, content, tool_calls, timestamp)
   - Immutable append-only conversation history for auditability

4. **Security Principles Extended**:
   - Agent context must include user_id from JWT (not tool parameters)
   - Tools must validate user_id from context
   - Agent must refuse off-topic requests and instruction overrides
   - Rate limiting required on chat endpoint

5. **Technology Stack Extended**:
   - OpenAI Agents SDK (Python)
   - Official MCP SDK (Python)
   - ChatKit (React)
   - GPT-4o or better model requirement

6. **New Success Criteria**:
   - Natural language task management (add, list, complete, delete, update)
   - Conversation persistence across server restarts
   - Multi-user agent safety (no cross-user access)
   - Agent boundary enforcement (refuses off-topic)
   - MCP tools as thin wrappers (5-10 lines)

## Outcome

- ✅ Impact: Constitution v3.0.0 established Phase III governance framework
- 🧪 Tests: Compliance checklist updated with 11 Phase III verification items
- 📁 Files: .specify/memory/constitution.md updated, .claude/skills/chatkit/skill.md created
- 🔁 Next prompts: /sp.specify (create Phase III chatbot feature spec)
- 🧠 Reflection: MAJOR version bump justified by fundamental architectural addition (Intelligence Layer). All Phase II principles preserved while adding AI-specific governance.

## Evaluation notes (flywheel)

- Failure modes observed: None (constitutional amendment process followed)
- Graders run and results (PASS/FAIL): Manual review PASS (all principles coherent, no conflicts)
- Prompt variant (if applicable): N/A (constitutional amendment)
- Next experiment (smallest change to try): Begin Phase III spec generation with /sp.specify
