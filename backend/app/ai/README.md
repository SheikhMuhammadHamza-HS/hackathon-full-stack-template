# AI Module - Agent Implementations

This folder contains two implementations of the AI agent:

## Current Implementation (In Use)

**Files:**
- `agent.py` - Uses low-level `AsyncOpenAI` client
- `tools.py` - Plain async functions with manual context management
- `mcp_server.py` - MCP SDK for tool definitions

**Pattern:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()
response = await client.chat.completions.create(...)
# Manual function calling handling
```

**Status:** ✅ Working and in production use

---

## Proper Agents SDK Implementation (Alternative)

**Files:**
- `agent_proper.py` - Uses `Agent` and `Runner` from agents library
- `tools_agents_sdk.py` - Tools with `@function_tool` decorator

**Pattern:**
```python
from agents import Agent, Runner, function_tool

@function_tool
async def add_task(ctx: RunContextWrapper[TodoContext], title: str) -> str:
    ...

agent = Agent(name="TodoBot", tools=[...])
result = await Runner.run(agent, message, context=context)
```

**Status:** ⚠️ Implemented but not active (reference implementation)

---

## Why Two Implementations?

**Current (agent.py):**
- ✅ Already tested and working
- ✅ Simple and straightforward
- ✅ Direct control over function calling
- ❌ More boilerplate code
- ❌ Not using Agents SDK abstractions

**Proper SDK (agent_proper.py):**
- ✅ Uses official Agents SDK patterns
- ✅ Cleaner abstractions (Agent, Runner)
- ✅ @function_tool decorators
- ✅ Better context management
- ⚠️ Needs migration and testing
- ⚠️ Not yet production-tested

---

## How to Switch to Agents SDK

1. Update `chat.py`:
   ```python
   # Change from:
   from app.ai.agent import create_agent, run_agent
   # To:
   from app.ai.agent_proper import run_agent_proper
   ```

2. Update tool execution:
   ```python
   # Change from:
   result = await run_agent(agent_config, message, history, tool_executor)
   # To:
   result = await run_agent_proper(message, history, session, user_id)
   ```

3. Test thoroughly before production

---

## 5 MCP Tools

Both implementations provide the same 5 tools:

1. **add_task** - Create new task
2. **list_tasks** - Get all tasks with filter
3. **complete_task** - Mark task as done
4. **delete_task** - Remove task
5. **update_task** - Modify task title/description

All tools:
- Read user_id from context (security)
- Validate parameters
- Return JSON string with success/error
- Filter by authenticated user_id

---

## Instructions

**System Instructions:** `instructions.py`
- Agent name: TodoBot
- Model: gpt-4o-mini
- Boundaries and capabilities defined

Both agent implementations use the same instructions.
