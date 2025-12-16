---
name: mcp
description: Model Context Protocol (MCP) skill for building MCP servers and clients. Use when working with MCP servers, MCP tools, MCP resources, MCP prompts, stdio transport, HTTP transport, or integrating AI applications with external systems. Triggers on keywords like MCP, Model Context Protocol, MCP server, MCP client, MCP tools, resources, prompts, context protocol.
---

# Model Context Protocol (MCP) Skill

## Overview

**Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. Think of it as **USB-C for AI** — a standardized way to connect AI applications to data sources, tools, and workflows.

**Created by:** Anthropic
**Official Docs:** https://modelcontextprotocol.io/

## What MCP Enables

| Use Case | Example |
|----------|---------|
| **Personalized AI** | Agents access Google Calendar and Notion |
| **Design-to-Code** | Generate web apps from Figma designs |
| **Enterprise Integration** | Connect chatbots to multiple databases |
| **Physical Automation** | Create 3D designs in Blender and print them |

## Architecture

### Three Key Participants

```
┌─────────────────────────────────────────┐
│         MCP Host (AI Application)        │
│      (Claude Desktop, Claude Code)       │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼───┐
│ Client │          │ Client │
│   #1   │          │   #2   │
└───┬────┘          └────┬───┘
    │                    │
┌───▼────┐          ┌────▼───┐
│ Server │          │ Server │
│   #1   │          │   #2   │
└────────┘          └────────┘
```

1. **MCP Host** - The AI application coordinating connections
2. **MCP Client** - Maintains 1:1 connection with a server
3. **MCP Server** - Exposes tools, resources, and prompts

### Two-Layer Design

| Layer | Purpose | Technology |
|-------|---------|------------|
| **Data Layer** | Protocol messages, lifecycle, features | JSON-RPC 2.0 |
| **Transport Layer** | Connection, message framing, auth | stdio or HTTP+SSE |

## Core Primitives

### Server-Exposed

| Primitive | Purpose |
|-----------|---------|
| **Tools** | Executable functions for AI actions |
| **Resources** | Data sources providing context |
| **Prompts** | Reusable interaction templates |

### Client-Exposed

| Primitive | Purpose |
|-----------|---------|
| **Sampling** | Request LLM completions from host |
| **Elicitation** | Request additional user input |
| **Logging** | Send debug/monitoring messages |

## Installation

```bash
# Python SDK
pip install mcp

# TypeScript SDK
npm install @modelcontextprotocol/sdk
```

## Building an MCP Server (Python)

### Basic Server

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Create server
server = Server("example-server")

# Define a tool
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or zip code"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units"
                    }
                },
                "required": ["location"]
            }
        )
    ]

# Implement tool
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        location = arguments["location"]
        units = arguments.get("units", "celsius")

        # Your tool logic here
        weather_data = fetch_weather(location, units)

        return [
            TextContent(
                type="text",
                text=f"Weather in {location}: {weather_data}"
            )
        ]

    raise ValueError(f"Unknown tool: {name}")

# Run server
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Server with Resources

```python
from mcp.types import Resource, TextContent

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file:///project/README.md",
            name="README.md",
            description="Project documentation",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "file:///project/README.md":
        with open("README.md", "r") as f:
            return f.read()

    raise ValueError(f"Unknown resource: {uri}")
```

### Server with Prompts

```python
from mcp.types import Prompt, PromptMessage

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="code_review",
            description="Review code for quality and best practices",
            arguments=[
                {
                    "name": "code",
                    "description": "The code to review",
                    "required": True
                }
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> list[PromptMessage]:
    if name == "code_review":
        code = arguments["code"]
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Please review this code:\n\n{code}"
                )
            )
        ]

    raise ValueError(f"Unknown prompt: {name}")
```

## Using MCP in OpenAI Agents SDK

### Stdio MCP Server

```python
from agents import Agent
from agents.mcp import MCPServerStdio

# Connect to local MCP server
server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
)

async def main():
    async with server:
        # Get tools from MCP server
        tools = await server.list_tools()

        agent = Agent(
            name="File Manager",
            instructions="Help manage files using MCP tools",
            tools=tools,
        )

        result = await Runner.run(agent, "List all files")
        print(result.final_output)
```

### HTTP MCP Server

```python
from agents.mcp import MCPServerStreamableHttp

server = MCPServerStreamableHttp(
    url="https://mcp-server.example.com/mcp",
    headers={"Authorization": "Bearer token"},
    timeout=30,
)

async def main():
    async with server:
        tools = await server.list_tools()
        resources = await server.list_resources()

        agent = Agent(
            name="MCP Agent",
            instructions="Use MCP tools and resources",
            tools=tools,
        )

        result = await Runner.run(agent, "Get data from MCP")
```

### Hosted MCP Tools (OpenAI)

```python
from agents import Agent
from agents.tool import HostedMCPTool

# MCP tool hosted by OpenAI Responses API
mcp_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "my-mcp-server",
        "server_url": "https://mcp.example.com/mcp",
        "allowed_tools": ["search", "calculate"],
    }
)

agent = Agent(
    name="MCP Agent",
    instructions="Use hosted MCP tools",
    tools=[mcp_tool],
)
```

## Transport Types

### 1. Stdio Transport (Local)

**Use when:**
- Running local MCP servers
- Low latency required
- No network needed

**Example:**
```bash
# Server as subprocess
python mcp_server.py

# Client launches it via stdio
```

### 2. HTTP with SSE Transport (Remote)

**Use when:**
- Remote MCP servers
- Multiple clients
- Web-based deployment

**Features:**
- HTTP POST for client → server
- HTTP GET with SSE for server → client
- Session management via `Mcp-Session-Id` header
- OAuth/Bearer token authentication

## MCP in FastAPI

### Exposing MCP Server via HTTP

```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from mcp.server import Server
import json

app = FastAPI()
mcp_server = Server("my-mcp-server")

# Define tools
@mcp_server.list_tools()
async def list_tools():
    return [...]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    return [...]

# MCP endpoint
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()

    # Handle MCP request
    response = await mcp_server.handle_request(body)

    return response

@app.get("/mcp")
async def mcp_sse(request: Request):
    async def event_generator():
        # SSE stream for server-initiated messages
        async for event in mcp_server.events():
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## Complete MCP Server Example

```python
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt, TextContent
import mcp.server.stdio
import sqlite3

server = Server("todo-mcp-server")

# Database connection
db = sqlite3.connect("todos.db")

# 1. Define Tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_task",
            description="Add a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add_task":
        title = arguments["title"]
        description = arguments.get("description", "")

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description)
        )
        db.commit()
        task_id = cursor.lastrowid

        return [TextContent(
            type="text",
            text=f"Task created with ID: {task_id}"
        )]

    elif name == "list_tasks":
        cursor = db.cursor()
        cursor.execute("SELECT id, title, completed FROM tasks")
        tasks = cursor.fetchall()

        tasks_text = "\n".join([
            f"{id}: {title} {'✓' if completed else '○'}"
            for id, title, completed in tasks
        ])

        return [TextContent(type="text", text=tasks_text)]

    elif name == "complete_task":
        task_id = arguments["task_id"]
        cursor = db.cursor()
        cursor.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )
        db.commit()

        return [TextContent(
            type="text",
            text=f"Task {task_id} marked as completed"
        )]

    raise ValueError(f"Unknown tool: {name}")

# 2. Define Resources
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="sqlite:///todos.db",
            name="Tasks Database",
            description="SQLite database containing all tasks",
            mimeType="application/x-sqlite3"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "sqlite:///todos.db":
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        return str(tasks)

    raise ValueError(f"Unknown resource: {uri}")

# 3. Define Prompts
@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="task_summary",
            description="Generate a summary of all tasks",
            arguments=[]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "task_summary":
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        completed = cursor.fetchone()[0]

        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please summarize: {pending} pending tasks, {completed} completed tasks"
                    }
                }
            ]
        }

    raise ValueError(f"Unknown prompt: {name}")

# Run server
if __name__ == "__main__":
    import asyncio

    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    asyncio.run(main())
```

## Using MCP Servers in Claude Code

### Configure in .claude/mcp.json

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "todo": {
      "command": "python",
      "args": ["mcp_server.py"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

### Using in Agents

Once configured, MCP tools are automatically available:

```python
from agents import Agent, Runner

# Agent automatically has access to MCP tools
agent = Agent(
    name="File Manager",
    instructions="Help manage files and tasks using available MCP tools"
)

# MCP tools are called automatically by the agent
result = await Runner.run(agent, "List all files in the project")
```

## Protocol Messages

### 1. Initialization

**Client Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "sampling": {}
    },
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

**Server Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true}
    },
    "serverInfo": {
      "name": "my-server",
      "version": "1.0.0"
    }
  }
}
```

### 2. Tool Operations

**List Tools:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**Call Tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "units": "celsius"
    }
  }
}
```

**Tool Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Temperature: 20°C, Conditions: Sunny"
      }
    ],
    "isError": false
  }
}
```

### 3. Resource Operations

**List Resources:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list"
}
```

**Read Resource:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///project/README.md"
  }
}
```

**Resource Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "file:///project/README.md",
        "mimeType": "text/markdown",
        "text": "# My Project\n\nProject documentation..."
      }
    ]
  }
}
```

### 4. Prompt Operations

**List Prompts:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "prompts/list"
}
```

**Get Prompt:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def hello(): pass"
    }
  }
}
```

### 5. Notifications

**Server → Client (Tool list changed):**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

**Server → Client (Resource updated):**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "uri": "file:///project/data.json"
  }
}
```

## Tool Input Schema

```python
# JSON Schema for tool parameters
tool_schema = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query"
        },
        "limit": {
            "type": "integer",
            "description": "Max results",
            "minimum": 1,
            "maximum": 100,
            "default": 10
        },
        "filters": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Filter categories"
        }
    },
    "required": ["query"]
}
```

## Tool Output Types

```python
from mcp.types import (
    TextContent,
    ImageContent,
    AudioContent,
    ResourceContent
)

# Text output
return [TextContent(type="text", text="Result text")]

# Image output
return [ImageContent(
    type="image",
    data="base64-encoded-data",
    mimeType="image/png"
)]

# Audio output
return [AudioContent(
    type="audio",
    data="base64-encoded-data",
    mimeType="audio/wav"
)]

# Resource output
return [ResourceContent(
    type="resource",
    resource={
        "uri": "file:///result.txt",
        "mimeType": "text/plain",
        "text": "Resource content"
    }
)]
```

## Resource Annotations

```python
Resource(
    uri="file:///important.txt",
    name="important.txt",
    description="Critical file",
    mimeType="text/plain",
    annotations={
        "audience": ["user"],        # or ["assistant"]
        "priority": 0.9,             # 0.0 to 1.0
        "lastModified": "2025-01-12T15:00:58Z"
    }
)
```

## Common URI Schemes

| Scheme | Purpose | Example |
|--------|---------|---------|
| `file://` | Local files | `file:///home/user/file.txt` |
| `https://` | Web resources | `https://api.example.com/data` |
| `git://` | Git repositories | `git://repo/path/to/file` |
| `sqlite://` | Database resources | `sqlite:///database.db` |
| Custom | App-specific | `myapp://resource/123` |

## Error Handling

### JSON-RPC Errors

```python
# In tool/resource handlers
if not valid:
    raise ValueError("Invalid parameter")  # Becomes JSON-RPC error

# Client receives:
{
  "jsonrpc": "2.0",
  "id": 8,
  "error": {
    "code": -32602,
    "message": "Invalid parameter"
  }
}
```

### Tool Execution Errors

```python
# Return error in result
return [TextContent(
    type="text",
    text="Failed to fetch data: Connection timeout"
)], {"isError": True}

# Client receives:
{
  "result": {
    "content": [...],
    "isError": true
  }
}
```

## Security Best Practices

### Server-Side

1. **Validate inputs** - Always validate tool arguments and resource URIs
2. **Access control** - Implement proper authorization
3. **Rate limiting** - Prevent abuse
4. **Sanitize outputs** - Clean data before returning
5. **Bind locally** - Use `127.0.0.1` for local servers
6. **Validate Origin** - Check Origin header for HTTP servers

### Client-Side

1. **User confirmation** - Prompt before sensitive operations
2. **Show inputs** - Display tool arguments to users
3. **Validate results** - Check tool outputs before using
4. **Timeouts** - Implement call timeouts
5. **Audit logging** - Track all tool usage

## MCP Server Examples

### File System Server

```bash
# Official filesystem MCP server
npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

### GitHub Server

```bash
# Official GitHub MCP server
npx -y @modelcontextprotocol/server-github

# Set GITHUB_TOKEN in environment
export GITHUB_TOKEN=ghp_xxx
```

### Database Server

```bash
# PostgreSQL MCP server
npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
```

### Custom Server

```python
# Custom MCP server
from mcp.server import Server
import mcp.server.stdio

server = Server("custom-server")

# Add your tools, resources, prompts
# ...

# Run
async def main():
    async with mcp.server.stdio.stdio_server() as streams:
        await server.run(*streams, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Testing MCP Servers

```python
# test_mcp_server.py
import pytest
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_tool_call():
    async with stdio_client(["python", "mcp_server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            assert len(tools) > 0

            # Call tool
            result = await session.call_tool(
                "get_weather",
                {"location": "NYC"}
            )
            assert result.content[0].text
```

## Debugging

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Server logs
server = Server("debug-server")
server.logger.debug("Tool called: %s", name)
server.logger.error("Error: %s", error)
```

## Quick Reference

| Operation | Method | Direction |
|-----------|--------|-----------|
| Initialize | `initialize` | Client → Server |
| List tools | `tools/list` | Client → Server |
| Call tool | `tools/call` | Client → Server |
| List resources | `resources/list` | Client → Server |
| Read resource | `resources/read` | Client → Server |
| List prompts | `prompts/list` | Client → Server |
| Get prompt | `prompts/get` | Client → Server |
| Tool list changed | `notifications/tools/list_changed` | Server → Client |

## Resources

- [Official MCP Docs](https://modelcontextprotocol.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Community Servers](https://github.com/modelcontextprotocol/servers)
