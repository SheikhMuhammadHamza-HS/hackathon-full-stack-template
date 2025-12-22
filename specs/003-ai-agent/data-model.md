# Data Model: AI Agent with MCP Tools

**Feature**: 003-ai-agent
**Created**: 2025-12-22

## Overview

This feature has **NO database tables** - it's pure logic layer. Uses existing tables from other features.

## Data Dependencies

### Uses From Other Features

**From 001-user-auth**:
- User model (for user_id validation)

**From 001-todo-web-app**:
- Task model (for CRUD operations via MCP tools)

**From 002-chat-persistence**:
- Conversation model (for message storage)
- Message model (for conversation history)

## Agent Context

**Runtime Context** (not persisted):

```python
_request_context: Dict[str, Any] = {
    "user_id": "uuid-from-jwt"
}
```

**Purpose**:
- Pass user_id to MCP tools securely
- No database storage
- Cleared after each request

## MCP Tool Schemas

### add_task Tool

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title (1-200 chars)"
    },
    "description": {
      "type": "string",
      "description": "Optional description (max 1000 chars)"
    }
  },
  "required": ["title"]
}
```

**Output**:
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "Buy milk",
    "description": "2 liters",
    "completed": false,
    "created_at": "2025-12-22T10:00:00"
  }
}
```

---

### list_tasks Tool

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "active", "completed"]
    }
  },
  "required": []
}
```

**Output**:
```json
{
  "success": true,
  "tasks": [...],
  "count": 5,
  "filter": "all"
}
```

---

### complete_task Tool

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer"
    }
  },
  "required": ["task_id"]
}
```

**Output**:
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "Buy milk",
    "completed": true,
    "updated_at": "2025-12-22T10:30:00"
  }
}
```

---

### delete_task Tool

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer"
    }
  },
  "required": ["task_id"]
}
```

**Output**:
```json
{
  "success": true,
  "task_id": 1,
  "title": "Buy milk",
  "message": "Task deleted successfully"
}
```

---

### update_task Tool

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer"
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    }
  },
  "required": ["task_id"]
}
```

**Output**:
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "New title",
    "description": "New description",
    "updated_at": "2025-12-22T10:45:00"
  }
}
```

---

## Agent Configuration

**System Instructions** (`backend/app/ai/instructions.py`):
- Agent name: "TodoBot"
- Model: "gpt-4o-mini"
- Behavior boundaries defined
- Tool usage examples included

**Agent Factory** (`backend/app/ai/agent.py`):
- create_agent(user_id, tools) → agent config
- run_agent(config, message, history, executor) → response

---

## Request/Response Models

### ChatRequest Schema

```python
class ChatRequest(BaseModel):
    message: str  # 1-10000 characters
    conversation_id: Optional[int] = None
```

### ChatResponse Schema

```python
class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    tool_calls: List[ToolCallInfo]
    timestamp: datetime
```

### ToolCallInfo Schema

```python
class ToolCallInfo(BaseModel):
    tool: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
```

---

## No Tables in This Feature

This feature is **pure logic layer** - no database tables created here.

It **uses** tables from:
- 001-todo-web-app (tasks table)
- 002-chat-persistence (conversations, messages tables)

It **modifies** data in:
- tasks table (via MCP tools)
- conversations table (update timestamps)
- messages table (insert new messages)
