# AI Agent with MCP Tools

## Overview

AI intelligence layer that processes natural language commands and executes task operations through standardized MCP tools.

## What This Feature Provides

### AI Agent
- OpenAI AsyncOpenAI client integration
- Stateless agent (fresh per request)
- System instructions (TodoBot personality)
- Context injection (user_id security)

### MCP Tools (Official SDK)
- add_task - Create new tasks
- list_tasks - Retrieve user's tasks
- complete_task - Mark tasks as done
- delete_task - Remove tasks
- update_task - Modify task details

### Chat API Endpoints
- POST /api/{user_id}/chat - Process messages
- GET /api/{user_id}/conversations - List conversations
- GET /api/{user_id}/conversations/{id}/messages - Get history
- DELETE /api/{user_id}/conversations/{id} - Delete conversation

## What This Feature Does NOT Include

❌ Database tables → See `002-chat-persistence`
❌ Chat UI components → See `004-chat-ui`
❌ Task CRUD logic → Uses `001-todo-web-app`

This is **pure intelligence layer** - AI processing and MCP tools.

## Files in This Specification

| File | Purpose |
|------|---------|
| `spec.md` | AI agent requirements |
| `data-model.md` | MCP tool schemas and agent context |
| `plan.md` | Architecture and design decisions |
| `research.md` | Technical research (OpenAI SDK, MCP) |
| `tasks.md` | 71 implementation tasks (all completed) |
| `README.md` | This file |

## Implementation Files

### Backend AI Module
- `backend/app/ai/instructions.py` - TodoBot system instructions
- `backend/app/ai/agent.py` - Agent factory with AsyncOpenAI
- `backend/app/ai/tools.py` - 5 MCP tool implementations
- `backend/app/ai/mcp_server.py` - MCP SDK server

### Backend API
- `backend/app/routers/chat.py` - Chat endpoints
- `backend/app/schemas.py` - ChatRequest/ChatResponse models
- `backend/app/main.py` - Router registration

## Dependencies

**Requires**:
- 001-user-auth (JWT validation)
- 002-chat-persistence (database tables)
- 001-todo-web-app (Task CRUD logic)

**Provides To**:
- 004-chat-ui (working chat API)

## Status

✅ **IMPLEMENTED** - AI agent working with MCP tools

## Quick Test

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/YOUR_USER_ID/chat \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}'
```

Expected response:
```json
{
  "reply": "Task 'Buy milk' added successfully!",
  "conversation_id": 1,
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy milk"},
      "result": {"success": true, "task": {...}}
    }
  ],
  "timestamp": "2025-12-22T10:00:00Z"
}
```
