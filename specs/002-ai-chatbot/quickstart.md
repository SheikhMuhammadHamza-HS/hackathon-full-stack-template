# Quickstart: AI-Powered Todo Chatbot

**Feature**: 002-ai-chatbot
**Branch**: `002-ai-chatbot`
**Date**: 2025-12-21

## Prerequisites

Before starting Phase III implementation, ensure Phase II is complete:

- ✅ Backend running on port 8001 with FastAPI
- ✅ Frontend running on port 3000 with Next.js 16
- ✅ Database: Neon PostgreSQL with users and tasks tables
- ✅ Authentication working (signup, signin, JWT validation)
- ✅ Task CRUD operations functional via GUI

## Setup Steps

### 1. Environment Variables

**Backend (.env)**:
```env
# Existing Phase II variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
ALLOWED_ORIGINS=http://localhost:3000

# NEW Phase III variables
OPENAI_API_KEY=sk-proj-...  # Get from platform.openai.com
```

**Frontend (.env.local)**:
```env
# Existing Phase II variables
NEXT_PUBLIC_API_URL=http://localhost:8001
BETTER_AUTH_SECRET=...

# NEW Phase III variables (if using ChatKit)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=...  # Optional for ChatKit
```

### 2. Install Dependencies

**Backend**:
```bash
cd backend

# Add Phase III dependencies to pyproject.toml
# - openai-agents-sdk
# - mcp-sdk (or openai[mcp] if bundled)
# - slowapi (rate limiting)

# Install
uv pip install -e .
```

**Frontend**:
```bash
cd frontend

# Install ChatKit (if using pre-built UI)
npm install @openai/chatkit-react

# Or build custom chat UI (no additional dependencies needed)
```

### 3. Database Migration

```bash
cd backend

# Generate migration for conversations and messages tables
alembic revision --autogenerate -m "add conversations and messages tables for chatbot"

# Review generated migration file
cat alembic/versions/[timestamp]_add_conversations_and_messages_tables.py

# Apply migration
alembic upgrade head

# Verify tables created
# Check Neon dashboard or run: SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### 4. Verify Database Schema

Expected tables after migration:
- `users` (Phase II)
- `tasks` (Phase II)
- `conversations` (NEW)
- `messages` (NEW)
- `alembic_version` (migration tracking)

---

## Development Workflow

### Phase 1: Backend - MCP Tools

**File**: `backend/app/ai/tools.py`

1. Create `backend/app/ai/` directory
2. Implement 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
3. Each tool is thin wrapper (~10 lines) calling existing CRUD functions
4. Tools read user_id from context via `get_context("user_id")`
5. Tools return structured dicts (success/error)

**Test**: Call tools directly with mock context
```python
from app.ai.tools import add_task
from mcp import set_context

set_context("user_id", "test-user-123")
result = await add_task(title="Test Task")
assert result["success"] == True
```

---

### Phase 2: Backend - Agent Configuration

**File**: `backend/app/ai/agent.py`

1. Define system instructions in `backend/app/ai/instructions.py`
2. Create `create_agent()` function that:
   - Takes user_id and conversation_history as parameters
   - Instantiates Agent with tools and instructions
   - Sets user_id in context
   - Returns agent instance

**Test**: Create agent and verify tool access
```python
agent = create_agent(user_id="test-user", conversation_history=[])
assert agent.context["user_id"] == "test-user"
assert len(agent.tools) == 5
```

---

### Phase 3: Backend - Chat Endpoint

**File**: `backend/app/routers/chat.py`

1. Create router with POST `/{user_id}/chat` endpoint
2. Implement stateless pattern:
   - Fetch conversation history from database
   - Create fresh agent with user_id context
   - Process message through agent
   - Save user message and agent response atomically
   - Return reply and conversation_id

**Test**: Send chat requests via curl
```bash
curl -X POST http://localhost:8001/api/user-123/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task buy milk", "conversation_id": null}'

# Expected: 200 OK, reply confirms task added
```

---

### Phase 4: Frontend - Chat Interface

**Option A: ChatKit (Recommended)**

**File**: `frontend/app/chat/page.tsx`

1. Create /chat page as Client Component
2. Integrate ChatKit with custom token provider
3. Connect to backend /api/{user_id}/chat endpoint

**Test**: Open http://localhost:3000/chat, verify UI renders

**Option B: Custom Chat UI**

**Files**:
- `frontend/components/ChatInterface.tsx`
- `frontend/components/ChatMessage.tsx`
- `frontend/components/ChatInput.tsx`

1. Build custom React components
2. Manage message state and API calls
3. Style with Tailwind CSS matching dashboard theme

---

### Phase 5: Integration Testing

**Test Scenario 1: Natural Language Task Creation**
1. Open chat interface
2. Type: "Add a task to buy milk"
3. Verify: Task appears in dashboard task list
4. Verify: Chat shows confirmation message

**Test Scenario 2: Conversation Persistence**
1. Send message: "Add task buy milk"
2. Send message: "Show my tasks"
3. Refresh browser page
4. Verify: Both messages visible in chat history
5. Restart backend server
6. Send message: "What tasks do I have?"
7. Verify: Agent has context from previous messages

**Test Scenario 3: Multi-User Isolation**
1. Sign in as User A
2. Send message: "Add task buy milk"
3. Sign out, sign in as User B
4. Send message: "Show my tasks"
5. Verify: User B does NOT see User A's "buy milk" task

---

## Testing Checklist

### Backend Tests

- [ ] Database migration applies without errors
- [ ] Conversations table created with correct schema
- [ ] Messages table created with correct schema
- [ ] Indexes created successfully
- [ ] MCP tools can be called directly (unit test)
- [ ] Tools enforce user_id from context
- [ ] Chat endpoint requires JWT authentication
- [ ] Chat endpoint validates user_id matches JWT
- [ ] Conversation history fetched correctly
- [ ] Messages saved atomically (user + assistant)
- [ ] Rate limiting enforces 20/minute limit

### Frontend Tests

- [ ] Chat interface renders on /chat page
- [ ] JWT token passed to chat endpoint
- [ ] Message input validates non-empty
- [ ] Loading state displays during processing
- [ ] Chat history displays chronologically
- [ ] Mobile responsive (375px width)
- [ ] Error messages displayed user-friendly
- [ ] Conversation persists after page reload

### Integration Tests

- [ ] User can create task via chat
- [ ] User can list tasks via chat
- [ ] User can complete task via chat
- [ ] User can delete task via chat
- [ ] User can update task via chat
- [ ] Conversation history persists across server restart
- [ ] Multi-user isolation enforced
- [ ] Agent refuses off-topic requests
- [ ] Prompt injection attempts rejected

---

## Common Commands

### Start Development Servers

```bash
# Backend (Terminal 1)
cd backend
.venv/Scripts/uvicorn.exe app.main:app --reload --port 8001

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Database Operations

```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check current version
alembic current
```

### Testing Chat Endpoint

```bash
# Get JWT token (signin first via GUI or API)
TOKEN="..."

# Send chat message
curl -X POST http://localhost:8001/api/{user_id}/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test chatbot", "conversation_id": null}'

# Check conversation created
# (via Neon dashboard SQL editor or database tool)
SELECT * FROM conversations WHERE user_id = '{user_id}';

# Check messages saved
SELECT * FROM messages WHERE user_id = '{user_id}' ORDER BY created_at;
```

---

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution**: Add OPENAI_API_KEY to backend/.env
```bash
# Get API key from https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-proj-..." >> backend/.env

# Restart backend server
```

### Issue: "Chat endpoint returns 500"

**Debugging**:
1. Check backend logs for detailed error
2. Verify database migration applied: `alembic current`
3. Verify OpenAI API key valid: test with simple API call
4. Check conversation_id exists if provided

### Issue: "Conversation history not loading"

**Solution**:
1. Verify messages saved in database: `SELECT * FROM messages WHERE conversation_id = X;`
2. Check query includes user_id filter
3. Verify indexes created: `\d messages` in psql

### Issue: "Agent not calling tools"

**Possible Causes**:
1. Tool docstrings unclear (agent doesn't understand when to use)
2. System instructions too restrictive
3. Model doesn't support function calling (must use GPT-4o or better)

**Solution**: Review agent logs, improve tool descriptions

### Issue: "Rate limit blocking legitimate users"

**Solution**: Adjust rate limit in chat endpoint decorator:
```python
@limiter.limit("30/minute")  # Increase from 20 to 30
```

---

## Quick Reference

### File Locations

**Backend**:
- `backend/app/ai/tools.py` - MCP tool implementations
- `backend/app/ai/agent.py` - Agent creation function
- `backend/app/ai/instructions.py` - System instructions
- `backend/app/routers/chat.py` - Chat endpoint
- `backend/app/models.py` - Add Conversation and Message models
- `backend/alembic/versions/[timestamp]_add_conversations_and_messages_tables.py` - Migration

**Frontend**:
- `frontend/app/chat/page.tsx` - Chat page (ChatKit or custom)
- `frontend/components/ChatInterface.tsx` - Chat UI (if custom)

**Specs**:
- `specs/002-ai-chatbot/spec.md` - Feature specification
- `specs/002-ai-chatbot/plan.md` - Implementation plan
- `specs/002-ai-chatbot/data-model.md` - Database schema
- `specs/002-ai-chatbot/contracts/` - API contracts

### Key URLs

- **Chat Interface**: http://localhost:3000/chat
- **Chat API**: http://localhost:8001/api/{user_id}/chat
- **API Docs**: http://localhost:8001/docs (includes chat endpoint)
- **Database**: Neon dashboard at https://console.neon.tech/

### Environment Variable Summary

| Variable | Location | Required | Description |
|----------|----------|----------|-------------|
| OPENAI_API_KEY | backend/.env | Yes | OpenAI API access |
| DATABASE_URL | backend/.env | Yes | Neon PostgreSQL connection |
| BETTER_AUTH_SECRET | both | Yes | JWT signing (existing) |
| NEXT_PUBLIC_API_URL | frontend/.env.local | Yes | Backend URL (existing) |

---

## Next Steps

After completing quickstart setup:

1. **Run `/sp.tasks`** - Generate task breakdown from plan
2. **Implement tasks sequentially** - MCP tools → Agent → Chat endpoint → Frontend
3. **Test each task** - Verify acceptance criteria before moving to next
4. **Manual testing** - Try natural language commands, verify behavior
5. **Multi-user testing** - Create 2+ users, verify isolation
6. **Deploy** - Update Render/Vercel with new environment variables

Phase III implementation estimated at 15-20 tasks total.
