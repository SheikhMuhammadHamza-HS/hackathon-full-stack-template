---
id: 0004
title: Create Chat Router for AI Chatbot
stage: green
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-ai-chatbot
branch: 002-ai-chatbot
user: developer
command: create chat router
labels: ["backend", "fastapi", "chat", "rate-limiting", "api"]
links:
  spec: specs/002-ai-chatbot/contracts/chat-endpoint.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/routers/chat.py
  - backend/app/main.py
tests:
  - Manual testing required via curl/httpx
---

## Prompt

Create the chat router for the AI chatbot feature at backend/app/routers/chat.py.

**Context:**
- Feature: 002-ai-chatbot
- Spec: specs/002-ai-chatbot/contracts/chat-endpoint.md
- Existing auth pattern: See backend/app/routers/tasks.py for JWT auth pattern

**Requirements:**

1. Create POST /{user_id}/chat endpoint that:
   - Requires JWT authentication (use existing verify_jwt dependency)
   - Validates user_id matches JWT token
   - Accepts ChatRequest (message, conversation_id)
   - Returns ChatResponse (reply, conversation_id, tool_calls, timestamp)

2. Implement conversation logic:
   - If conversation_id is None: Create new conversation
   - If conversation_id provided: Fetch and verify it belongs to user
   - Save user message to database
   - Process with agent (placeholder for now - just return a simple response)
   - Save assistant response to database
   - Return response

3. Add rate limiting (20 requests/minute per user) using SlowAPI

4. Error handling:
   - 400 for invalid input
   - 401 for missing/invalid JWT
   - 403 for user_id mismatch
   - 429 for rate limit exceeded
   - 500 for server errors

**Existing patterns to follow:**
- backend/app/routers/tasks.py - for auth pattern
- backend/app/auth.py - for verify_jwt function
- backend/app/database.py - for get_session

**Models to use:**
- backend/app/models.py: Conversation, Message
- backend/app/schemas.py: ChatRequest, ChatResponse

Create a complete, working chat router. For now, the agent processing can be a placeholder that returns a simple response - we'll add real agent logic in the next phase.

## Response snapshot

Created chat router at `backend/app/routers/chat.py` implementing:

1. **POST /{user_id}/chat endpoint** - Main chat processing endpoint with:
   - JWT authentication via `verify_jwt` dependency
   - User ID validation (403 if mismatch)
   - Rate limiting at 20 requests/minute per user via SlowAPI
   - Conversation creation/retrieval logic
   - Message persistence (user + assistant messages)
   - Placeholder agent processing (returns simple response)

2. **GET /{user_id}/conversations** - List user's conversations

3. **GET /{user_id}/conversations/{conversation_id}/messages** - Fetch messages for a conversation

4. **Helper functions:**
   - `_validate_user_access()` - Validates URL user_id matches JWT
   - `_get_or_create_conversation()` - Creates new or retrieves existing conversation
   - `_save_message()` - Persists messages to database
   - `_fetch_conversation_history()` - Retrieves messages for context (limit 50)
   - `_process_with_agent()` - Placeholder for OpenAI Agent SDK integration

5. **Updated main.py:**
   - Added SlowAPI rate limiter setup
   - Added RateLimitExceeded exception handler with spec-compliant error format
   - Registered chat router at `/api` prefix

## Outcome

- Impact: Chat API foundation complete with proper auth, rate limiting, and error handling
- Tests: Manual testing required - backend must be running with database
- Files: 2 files created/modified
- Next prompts: Integrate OpenAI Agent SDK in _process_with_agent(), add MCP tools
- Reflection: Followed existing patterns from tasks.py for consistency; placeholder agent allows testing endpoint independently of OpenAI integration

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - implementation task
- Prompt variant (if applicable): N/A
- Next experiment: Test rate limiting behavior with rapid requests
