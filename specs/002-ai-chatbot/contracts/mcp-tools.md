# API Contract: MCP Tools

**Feature**: 002-ai-chatbot
**Version**: 1.0.0
**Date**: 2025-12-21

## Overview

MCP (Model Context Protocol) tools are the bridge between the AI agent and the application's task management functions. These five tools enable the agent to perform CRUD operations on tasks in response to natural language commands. Tools are thin wrappers around existing Phase II functions and automatically enforce user isolation via context injection.

**Key Principle**: Tools read `user_id` from agent context (not function parameters) to prevent user manipulation.

---

## Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

**Function Signature**:
```python
async def add_task(title: str, description: str = None) -> dict
```

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| title | string | Yes | 1-200 chars | Task title |
| description | string | No | 0-1000 chars | Task description (optional) |

**Context Required**:
- `user_id`: string (UUID) - Authenticated user from JWT

**Return Value**:

**Success**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy milk",
    "description": null,
    "completed": false,
    "created_at": "2025-12-21T10:05:30Z"
  }
}
```

**Error**:
```json
{
  "success": false,
  "error": "Title must be between 1 and 200 characters"
}
```

**Validation**:
- title must not be empty
- title length: 1-200 characters
- description length: 0-1000 characters (if provided)
- user_id from context must be valid

**Example Calls**:
```python
# Agent calls after processing "Add a task to buy milk"
result = await add_task(title="Buy milk")

# Agent calls after processing "Add task: finish project with detailed analysis"
result = await add_task(
    title="Finish project",
    description="Detailed analysis required"
)
```

---

## Tool 2: list_tasks

**Purpose**: Retrieve user's tasks, optionally filtered by completion status

**Function Signature**:
```python
async def list_tasks(filter: str = "all") -> dict
```

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| filter | string | No | "all", "active", "completed" | Task status filter (default: "all") |

**Context Required**:
- `user_id`: string (UUID) - Authenticated user from JWT

**Return Value**:

**Success**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": 15,
      "title": "Buy milk",
      "description": null,
      "completed": false,
      "created_at": "2025-12-21T10:05:30Z"
    },
    {
      "id": 12,
      "title": "Call dentist",
      "description": "Bring insurance card",
      "completed": true,
      "created_at": "2025-12-20T14:20:00Z"
    }
  ],
  "count": 2,
  "filter": "all"
}
```

**Empty Result**:
```json
{
  "success": true,
  "tasks": [],
  "count": 0,
  "filter": "all"
}
```

**Error**:
```json
{
  "success": false,
  "error": "Invalid filter. Must be 'all', 'active', or 'completed'"
}
```

**Validation**:
- filter must be one of: "all", "active", "completed"
- user_id from context must be valid

**Example Calls**:
```python
# Agent calls after processing "Show my tasks"
result = await list_tasks(filter="all")

# Agent calls after processing "What do I need to do?" (implies active)
result = await list_tasks(filter="active")

# Agent calls after processing "Show completed tasks"
result = await list_tasks(filter="completed")
```

---

## Tool 3: complete_task

**Purpose**: Mark a task as complete or toggle its completion status

**Function Signature**:
```python
async def complete_task(task_id: int) -> dict
```

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| task_id | integer | Yes | Must exist, must belong to user | Task to mark complete |

**Context Required**:
- `user_id`: string (UUID) - Authenticated user from JWT

**Return Value**:

**Success**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy milk",
    "completed": true,
    "updated_at": "2025-12-21T10:10:00Z"
  }
}
```

**Error (Task Not Found)**:
```json
{
  "success": false,
  "error": "Task 999 not found"
}
```

**Error (Already Complete)**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy milk",
    "completed": true,
    "updated_at": "2025-12-21T10:05:00Z"
  },
  "message": "Task was already complete"
}
```

**Validation**:
- task_id must be positive integer
- Task must exist in database
- Task must belong to context user_id

**Example Calls**:
```python
# Agent calls after processing "Mark task 15 as done"
result = await complete_task(task_id=15)

# Agent calls after processing "I finished buying milk" (agent looked up task by title)
result = await complete_task(task_id=15)
```

---

## Tool 4: delete_task

**Purpose**: Permanently delete a task

**Function Signature**:
```python
async def delete_task(task_id: int) -> dict
```

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| task_id | integer | Yes | Must exist, must belong to user | Task to delete |

**Context Required**:
- `user_id`: string (UUID) - Authenticated user from JWT

**Return Value**:

**Success**:
```json
{
  "success": true,
  "task_id": 15,
  "title": "Buy milk",
  "message": "Task deleted successfully"
}
```

**Error (Task Not Found)**:
```json
{
  "success": false,
  "error": "Task 999 not found"
}
```

**Validation**:
- task_id must be positive integer
- Task must exist in database
- Task must belong to context user_id

**Example Calls**:
```python
# Agent calls after processing "Delete task 15"
result = await delete_task(task_id=15)

# Agent calls after processing "Remove the grocery task" (agent looked up by title)
result = await delete_task(task_id=15)
```

**Warning**: Deletion is permanent. Agent should confirm with user for ambiguous requests.

---

## Tool 5: update_task

**Purpose**: Update task title and/or description

**Function Signature**:
```python
async def update_task(task_id: int, title: str = None, description: str = None) -> dict
```

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| task_id | integer | Yes | Must exist, must belong to user | Task to update |
| title | string | No | 1-200 chars if provided | New title (optional) |
| description | string | No | 0-1000 chars if provided | New description (optional) |

**Context Required**:
- `user_id`: string (UUID) - Authenticated user from JWT

**Return Value**:

**Success**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy milk and bread",
    "description": "Get whole grain bread",
    "completed": false,
    "updated_at": "2025-12-21T10:15:00Z"
  }
}
```

**Error (Task Not Found)**:
```json
{
  "success": false,
  "error": "Task 999 not found"
}
```

**Error (No Changes)**:
```json
{
  "success": false,
  "error": "Must provide at least one field to update (title or description)"
}
```

**Validation**:
- task_id must be positive integer
- At least one of title or description must be provided
- title length: 1-200 characters (if provided)
- description length: 0-1000 characters (if provided)
- Task must exist and belong to context user_id

**Example Calls**:
```python
# Agent calls after processing "Change task 15 title to 'Buy milk and bread'"
result = await update_task(task_id=15, title="Buy milk and bread")

# Agent calls after processing "Add description to task 15: get whole grain bread"
result = await update_task(task_id=15, description="Get whole grain bread")

# Agent calls after processing "Update task 15: new title and add description"
result = await update_task(
    task_id=15,
    title="Buy milk and bread",
    description="Get whole grain bread"
)
```

---

## Tool Implementation Pattern

All tools follow this pattern:

```python
from mcp import tool, get_context
from app.routers.tasks import (
    create_task_crud,
    get_user_tasks_crud,
    update_task_crud,
    delete_task_crud
)

@tool
async def add_task(title: str, description: str = None) -> dict:
    """
    Add a new task for the authenticated user.

    Args:
        title: Task title (1-200 characters, required)
        description: Task description (optional, max 1000 characters)

    Returns:
        Success: {"success": True, "task": {...}}
        Error: {"success": False, "error": "error message"}
    """
    # Get user_id from agent context (set during chat endpoint processing)
    user_id = get_context("user_id")

    # Validation (thin layer on top of CRUD function validation)
    if not title or len(title) > 200:
        return {"success": False, "error": "Title must be 1-200 characters"}

    # Call existing Phase II CRUD function
    try:
        task = await create_task_crud(user_id, title, description)
        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"add_task error for user {user_id}: {e}")
        return {"success": False, "error": "Failed to create task"}
```

**Key Points**:
- `@tool` decorator registers function with MCP SDK
- `get_context("user_id")` reads from agent context (secure)
- Thin wrapper: calls existing `create_task_crud` function
- Returns structured dict (not raises exception)
- Logs errors but returns user-friendly message

---

## Tool Registration

Tools are registered with the agent during initialization:

```python
from openai_agents import Agent
from app.ai.tools import add_task, list_tasks, complete_task, delete_task, update_task

def create_agent(user_id: str, conversation_history: List[Message]):
    agent = Agent(
        name="TodoBot",
        instructions=SYSTEM_INSTRUCTIONS,
        model="gpt-4o",
        tools=[
            add_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task
        ],
        context={"user_id": user_id}  # Injected from JWT
    )
    agent.set_conversation_history(conversation_history)
    return agent
```

---

## Error Handling Contract

### Tool Error Categories

**1. Validation Errors** (user-correctable):
```json
{
  "success": false,
  "error": "Title must be 1-200 characters"
}
```
Agent can retry with corrected parameters or ask user for clarification.

**2. Not Found Errors** (resource doesn't exist):
```json
{
  "success": false,
  "error": "Task 999 not found"
}
```
Agent informs user and suggests listing tasks.

**3. System Errors** (server/database issues):
```json
{
  "success": false,
  "error": "Failed to create task"
}
```
Agent apologizes and suggests retry or using GUI.

### Error Response Guidelines

- Errors are returned as structured objects (not raised exceptions)
- Error messages are user-friendly (no stack traces or internal details)
- Error messages guide next action ("Task not found. Try 'Show my tasks' to see available tasks.")
- System errors are logged server-side with full context

---

## Contract Validation

These MCP tool contracts satisfy:
- **FR-011**: Five MCP tools defined ✓
- **FR-012**: Thin wrappers around existing CRUD ✓
- **FR-013**: user_id from context, not parameters ✓
- **FR-014**: Structured dict responses ✓
- **FR-015**: Parameter validation ✓
- **Principle XIII**: MCP-First Architecture ✓

Tools are ready for implementation by backend-implementer agent.
