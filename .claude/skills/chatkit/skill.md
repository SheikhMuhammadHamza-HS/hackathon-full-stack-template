---
name: chatkit
description: OpenAI ChatKit skill for building AI-powered chat experiences. Use when creating chat interfaces, integrating conversational AI, building chat UIs with React/Next.js, implementing streaming responses, or connecting frontend chat components to backend agents. Triggers on keywords like ChatKit, chat interface, conversational AI, chat UI, OpenAI chat, streaming chat, AI assistant interface, chat components.
---

# ChatKit Skill

**OpenAI ChatKit integration skill for building AI-powered chat experiences.**

## Overview

ChatKit is OpenAI's official framework for building high-quality, AI-powered chat interfaces. This skill provides patterns and best practices for integrating ChatKit into React/Next.js applications with custom backends.

## What is ChatKit?

ChatKit is a batteries-included framework that provides:
- Pre-built chat UI components (React)
- Response streaming support
- Agent action visualization
- File upload capabilities
- Thread/conversation management
- Source annotations and citations
- Customizable themes and styling

## Installation

### Frontend (React/Next.js)
```bash
npm install @openai/chatkit-react
```

### Backend (Python/FastAPI)
```bash
pip install openai
```

## Quick Start

### 1. Backend Setup (FastAPI)

Create a token endpoint for ChatKit authentication:

```python
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/chat/token")
async def get_chat_token(
    user_id: str = Depends(verify_jwt)
):
    """
    Generate ChatKit client secret for authenticated user.

    Returns:
        client_secret: Token for ChatKit initialization
    """
    try:
        response = client.beta.realtime.sessions.create(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="sage"
        )
        return {
            "client_secret": response.client_secret.value
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create session: {str(e)}")
```

### 2. Frontend Integration (Next.js)

```typescript
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useEffect, useState } from 'react';

export default function ChatPage() {
  const [isReady, setIsReady] = useState(false);

  const { control } = useChatKit({
    api: {
      // Fetch token from your backend
      getClientSecret: async () => {
        const response = await fetch('/api/chat/token', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        });
        const data = await response.json();
        return data.client_secret;
      }
    },
    // Optional: Agent configuration
    agent: {
      name: "TodoBot",
      instructions: "You are a helpful todo assistant",
      tools: [] // Tools configuration
    }
  });

  useEffect(() => {
    if (control) {
      setIsReady(true);
    }
  }, [control]);

  if (!isReady) {
    return <div>Loading chat...</div>;
  }

  return (
    <div className="h-screen">
      <ChatKit
        control={control}
        // Optional customization
        theme={{
          colorScheme: 'dark',
          primaryColor: '#6366f1'
        }}
      />
    </div>
  );
}
```

## Architecture Patterns

### Pattern 1: ChatKit UI + Custom Backend

Use ChatKit's pre-built UI with your FastAPI backend and MCP tools.

```
┌─────────────┐
│  ChatKit UI │  (Frontend - Pre-built)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │  (Your Backend)
│  + MCP Tools│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │  (PostgreSQL)
└─────────────┘
```

**Implementation:**
```python
# backend/app/routers/chat.py

from openai_agents import Agent, tool

@tool
def add_task(user_id: str, title: str):
    """Add a new task for the user."""
    # Your database logic
    pass

@tool
def list_tasks(user_id: str):
    """List user's tasks."""
    # Your database logic
    pass

# Create agent with tools
agent = Agent(
    name="TodoBot",
    instructions="You help users manage their todo tasks",
    tools=[add_task, list_tasks]
)

@router.post("/chat/message")
async def handle_message(
    message: str,
    user_id: str = Depends(verify_jwt)
):
    """Process chat message through agent."""
    response = await agent.run(
        message,
        context={"user_id": user_id}
    )
    return {"reply": response.text}
```

### Pattern 2: Server-Side Conversation Management

Store conversations in your database for persistence.

```python
# backend/app/models.py

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field()  # "user" or "assistant"
    content: str = Field()
    tool_calls: Optional[str] = None  # JSON
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

```python
# Save messages to database
@router.post("/chat/message")
async def handle_message(
    request: ChatRequest,
    user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    # Get or create conversation
    conversation = await get_or_create_conversation(user_id, session)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    session.add(user_msg)

    # Process with agent
    response = await agent.run(request.message)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response.text,
        tool_calls=json.dumps(response.tool_calls)
    )
    session.add(assistant_msg)
    await session.commit()

    return {"reply": response.text}
```

## Customization

### Theme Customization

```typescript
<ChatKit
  control={control}
  theme={{
    colorScheme: 'dark',
    primaryColor: '#6366f1',
    backgroundColor: '#1f2937',
    textColor: '#f3f4f6',
    borderRadius: '0.5rem',
    fontFamily: 'Inter, sans-serif'
  }}
/>
```

### Custom Components

```typescript
import { ChatKit, ChatMessage } from '@openai/chatkit-react';

<ChatKit
  control={control}
  components={{
    // Custom message renderer
    message: (props) => (
      <ChatMessage
        {...props}
        avatar={<UserAvatar user={props.message.author} />}
      />
    ),
    // Custom input
    input: (props) => (
      <CustomChatInput
        {...props}
        placeholder="Ask me anything about your tasks..."
      />
    )
  }}
/>
```

## MCP Tools Integration

ChatKit works seamlessly with MCP (Model Context Protocol) tools.

### Define MCP Tools

```python
from openai_agents import tool

@tool
def add_task(user_id: str, title: str, description: str = None) -> dict:
    """
    Add a new task for the user.

    Args:
        user_id: The authenticated user's ID
        title: Task title (required)
        description: Optional task description

    Returns:
        dict with success status and task details
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    # Save to database
    session.add(task)
    session.commit()

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description
        }
    }

@tool
def list_tasks(user_id: str, filter: str = "all") -> dict:
    """
    List user's tasks.

    Args:
        user_id: The authenticated user's ID
        filter: "all", "completed", or "active"

    Returns:
        dict with list of tasks
    """
    query = select(Task).where(Task.user_id == user_id)

    if filter == "completed":
        query = query.where(Task.completed == True)
    elif filter == "active":
        query = query.where(Task.completed == False)

    tasks = session.execute(query).scalars().all()

    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "completed": t.completed,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ]
    }

@tool
def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete."""
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return {"success": False, "error": "Task not found"}

    task.completed = True
    task.updated_at = datetime.utcnow()
    session.commit()

    return {
        "success": True,
        "task_id": task_id,
        "title": task.title
    }

@tool
def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return {"success": False, "error": "Task not found"}

    title = task.title
    session.delete(task)
    session.commit()

    return {
        "success": True,
        "task_id": task_id,
        "title": title
    }

@tool
def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict:
    """Update task details."""
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return {"success": False, "error": "Task not found"}

    if title:
        task.title = title
    if description is not None:
        task.description = description

    task.updated_at = datetime.utcnow()
    session.commit()

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description
        }
    }
```

### Register Tools with Agent

```python
from openai_agents import Agent

agent = Agent(
    name="TodoBot",
    instructions="""
    You are TodoBot, a helpful AI assistant for managing todo tasks.

    You can help users:
    - Add new tasks
    - View their task list
    - Mark tasks as complete
    - Delete tasks
    - Update task details

    Always be friendly and concise. Confirm actions after completing them.
    """,
    tools=[
        add_task,
        list_tasks,
        complete_task,
        delete_task,
        update_task
    ]
)
```

## Testing Examples

### User Interactions

```
User: "Add a task to buy groceries"
Bot: ✅ Task added: Buy groceries

User: "Show me my tasks"
Bot: You have 3 tasks:
     1. Buy groceries (pending)
     2. Call dentist (pending)
     3. Finish report (completed)

User: "Mark task 1 as done"
Bot: ✅ Task "Buy groceries" marked as complete!

User: "Delete the dentist task"
Bot: ✅ Task "Call dentist" has been deleted

User: "Change task 3 title to 'Submit quarterly report'"
Bot: ✅ Task updated: Submit quarterly report
```

## Security Best Practices

### 1. User Isolation

Always validate user_id in tool functions:

```python
@tool
def add_task(user_id: str, title: str):
    # Verify user_id matches authenticated user
    if user_id != get_authenticated_user():
        raise PermissionError("Access denied")
    # ... rest of logic
```

### 2. Rate Limiting

Prevent abuse with rate limits:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat/message")
@limiter.limit("20/minute")
async def handle_message(...):
    pass
```

### 3. Input Validation

Validate all tool inputs:

```python
@tool
def add_task(user_id: str, title: str):
    if not title or len(title) > 200:
        raise ValueError("Title must be 1-200 characters")

    if not user_id:
        raise ValueError("user_id is required")

    # ... rest of logic
```

## Environment Variables

```env
# OpenAI API Key
OPENAI_API_KEY=sk-...

# ChatKit Configuration (optional)
CHATKIT_MODEL=gpt-4o-realtime-preview-2024-12-17
CHATKIT_VOICE=sage
```

## Troubleshooting

### Issue: "Failed to create session"

**Solution:** Check OpenAI API key is valid and has access to realtime models.

### Issue: Tools not being called

**Solution:** Ensure tool descriptions are clear and follow OpenAI function calling format.

### Issue: User context not passed to tools

**Solution:** Use agent context to inject user_id:

```python
response = await agent.run(
    message,
    context={"user_id": authenticated_user}
)
```

## Resources

- [ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [ChatKit API Reference](https://platform.openai.com/docs/api-reference/chatkit)
- [ChatKit GitHub](https://github.com/openai/chatkit-js)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-sdk/)
- [MCP Documentation](https://modelcontextprotocol.io/)

## Example Projects

- **Starter Template**: https://github.com/openai/openai-chatkit-starter-app
- **Advanced Samples**: https://github.com/openai/openai-chatkit-advanced-samples

## License

Apache 2.0 (follows OpenAI ChatKit license)
