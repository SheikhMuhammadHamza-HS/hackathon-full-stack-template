---
name: openai-agents-sdk
description: OpenAI Agents SDK skill for building agentic AI applications in Python. Use when creating AI agents, multi-agent systems, tool integrations, handoffs between agents, guardrails, MCP servers, or LLM-powered workflows. Triggers on keywords like agent, OpenAI, LLM, handoff, tool, guardrail, MCP, AI assistant, chatbot.
---

# OpenAI Agents SDK Skill

## Overview

The OpenAI Agents SDK is a lightweight Python framework for building agentic AI applications. It's the production-ready upgrade of OpenAI's Swarm experiment, providing minimal abstractions for creating intelligent agent-based systems.

## Core Primitives

The SDK is built on four fundamental components:

| Primitive | Purpose |
|-----------|---------|
| **Agents** | LLM instances with instructions and tools |
| **Handoffs** | Delegate tasks between agents |
| **Guardrails** | Validate inputs and outputs |
| **Tools** | Functions agents can call |

## Installation

```bash
# Basic installation
pip install openai-agents

# With LiteLLM support (for non-OpenAI models)
pip install "openai-agents[litellm]"

# Set API key
export OPENAI_API_KEY=sk-...
```

## Quick Start

```python
from agents import Agent, Runner

# Create an agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)

# Run synchronously
result = Runner.run_sync(agent, "Write a haiku about Python")
print(result.final_output)

# Run asynchronously
async def main():
    result = await Runner.run(agent, "Write a haiku about Python")
    print(result.final_output)
```

## Agent Configuration

### Basic Agent

```python
from agents import Agent

agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant that speaks like a pirate",
    model="gpt-4.1",  # Default model
)
```

### Agent with Tools

```python
from agents import Agent, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather information for a city.

    Args:
        city: The city name to get weather for.
    """
    return f"The weather in {city} is sunny, 72°F"

@function_tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the database for records.

    Args:
        query: Search query string.
        limit: Maximum results to return.
    """
    return f"Found {limit} results for: {query}"

agent = Agent(
    name="Weather Assistant",
    instructions="Help users with weather information",
    tools=[get_weather, search_database],
)
```

### Agent with Structured Output

```python
from agents import Agent
from pydantic import BaseModel

class WeatherReport(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int

agent = Agent(
    name="Weather Reporter",
    instructions="Extract weather information into structured format",
    output_type=WeatherReport,  # Enforces structured output
)

result = Runner.run_sync(agent, "The weather in NYC is 72°F and sunny with 45% humidity")
report: WeatherReport = result.final_output
print(f"City: {report.city}, Temp: {report.temperature}")
```

### Model Settings

```python
from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

agent = Agent(
    name="Creative Writer",
    instructions="Write creative stories",
    model="gpt-4.1",
    model_settings=ModelSettings(
        temperature=0.8,
        top_p=0.9,
        max_tokens=2000,
        # For GPT-5 models
        reasoning=Reasoning(effort="low"),
        verbosity="low",
    ),
)
```

## Function Tools

### Basic Tool Definition

```python
from agents import function_tool

@function_tool
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers.

    Args:
        a: First number.
        b: Second number.
    """
    return a + b

@function_tool
async def fetch_user_data(user_id: str) -> dict:
    """Fetch user data from the database.

    Args:
        user_id: The unique user identifier.
    """
    # Async operation
    return {"id": user_id, "name": "John Doe"}
```

### Tool with Context Access

```python
from agents import function_tool, RunContextWrapper
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: str
    db_connection: any

@function_tool
def get_user_orders(ctx: RunContextWrapper[AppContext]) -> str:
    """Get orders for the current user."""
    user_id = ctx.context.user_id
    # Access context data
    return f"Orders for user {user_id}"
```

### Custom Tool Name and Description

```python
@function_tool(
    name_override="search",
    description_override="Search for information in the knowledge base"
)
def search_knowledge_base(query: str) -> str:
    """Internal search function."""
    return f"Results for: {query}"
```

### Tool Return Types

```python
from agents import function_tool
from agents.tool import ToolOutputText, ToolOutputImage, ToolOutputFileContent
import base64

@function_tool
def get_text() -> str:
    """Return plain text."""
    return "Hello, world!"

@function_tool
def get_image() -> ToolOutputImage:
    """Return an image."""
    with open("image.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return ToolOutputImage(data=data, media_type="image/png")

@function_tool
def get_file() -> ToolOutputFileContent:
    """Return a file."""
    return ToolOutputFileContent(
        content="File contents here",
        filename="report.txt"
    )
```

## Hosted Tools (Built-in)

```python
from agents import Agent
from agents.tool import (
    WebSearchTool,
    FileSearchTool,
    CodeInterpreterTool,
    ImageGenerationTool,
    ComputerTool,
    LocalShellTool,
)

# Web search
agent = Agent(
    name="Researcher",
    tools=[WebSearchTool()],
)

# Code interpreter (sandboxed execution)
agent = Agent(
    name="Coder",
    tools=[CodeInterpreterTool()],
)

# File search (requires vector store)
agent = Agent(
    name="Document Expert",
    tools=[FileSearchTool(vector_store_ids=["vs_123"])],
)

# Image generation
agent = Agent(
    name="Artist",
    tools=[ImageGenerationTool()],
)

# Local shell (use with caution)
agent = Agent(
    name="System Admin",
    tools=[LocalShellTool()],
)
```

## Running Agents

### Synchronous Execution

```python
from agents import Agent, Runner

agent = Agent(name="Helper", instructions="Be helpful")

# Simple run
result = Runner.run_sync(agent, "Hello!")
print(result.final_output)

# With context
result = Runner.run_sync(
    agent,
    "Hello!",
    context=my_context,  # Custom context object
)
```

### Asynchronous Execution

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Helper", instructions="Be helpful")

    # Async run
    result = await Runner.run(agent, "Hello!")
    print(result.final_output)

    # Multiple concurrent runs
    results = await asyncio.gather(
        Runner.run(agent, "Question 1"),
        Runner.run(agent, "Question 2"),
        Runner.run(agent, "Question 3"),
    )
```

### Streaming

```python
from agents import Agent, Runner

async def stream_response():
    agent = Agent(name="Writer", instructions="Write stories")

    result = await Runner.run_streamed(agent, "Write a short story")

    async for event in result.stream_events():
        # Raw token events
        if event.type == "raw_response_event":
            if hasattr(event.data, "delta"):
                print(event.data.delta, end="", flush=True)

        # High-level events
        elif event.type == "run_item_stream_event":
            print(f"\nItem completed: {event.item.type}")

        elif event.type == "agent_updated_stream_event":
            print(f"\nAgent changed to: {event.new_agent.name}")

    # Final result still available
    print(f"\n\nFinal: {result.final_output}")
```

### Run Configuration

```python
from agents import Agent, Runner, RunConfig

agent = Agent(name="Helper", instructions="Be helpful")

config = RunConfig(
    model="gpt-4.1",  # Override model for all agents
    model_settings=ModelSettings(temperature=0.5),
    max_turns=10,  # Prevent infinite loops
    tracing_disabled=False,  # Enable tracing
    trace_id="custom-trace-123",
    workflow_name="customer-support",
)

result = await Runner.run(agent, "Hello!", run_config=config)
```

## Handoffs (Multi-Agent)

### Basic Handoffs

```python
from agents import Agent, handoff

# Specialist agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing questions. Be precise about amounts and dates."
)

support_agent = Agent(
    name="Support Agent",
    instructions="Handle technical support questions."
)

# Triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are the first point of contact.
    - For billing questions, hand off to Billing Agent
    - For technical issues, hand off to Support Agent
    """,
    handoffs=[billing_agent, support_agent],
)

# Run - agent can hand off automatically
result = Runner.run_sync(triage_agent, "I have a question about my bill")
print(f"Handled by: {result.last_agent.name}")
print(f"Response: {result.final_output}")
```

### Custom Handoff Configuration

```python
from agents import Agent, handoff
from pydantic import BaseModel

class EscalationData(BaseModel):
    reason: str
    priority: str

async def on_escalation(ctx, data: EscalationData):
    """Called when handoff happens."""
    print(f"Escalating: {data.reason} (Priority: {data.priority})")

escalation_agent = Agent(name="Escalation Team", instructions="Handle escalated issues")

main_agent = Agent(
    name="Main Agent",
    instructions="Handle requests. Escalate complex issues.",
    handoffs=[
        handoff(
            agent=escalation_agent,
            tool_name_override="escalate_to_human",
            tool_description_override="Escalate to human team for complex issues",
            on_handoff=on_escalation,
            input_type=EscalationData,
        )
    ],
)
```

### Agents as Tools (Orchestrator Pattern)

```python
from agents import Agent

# Specialist agents
translator = Agent(
    name="Translator",
    instructions="Translate text between languages accurately."
)

summarizer = Agent(
    name="Summarizer",
    instructions="Create concise summaries of text."
)

# Orchestrator uses agents as tools (maintains control)
orchestrator = Agent(
    name="Orchestrator",
    instructions="Process user requests using available tools.",
    tools=[
        translator.as_tool(
            tool_name="translate",
            tool_description="Translate text to another language"
        ),
        summarizer.as_tool(
            tool_name="summarize",
            tool_description="Summarize long text"
        ),
    ],
)
```

## Context Management

### Creating Context

```python
from dataclasses import dataclass
from agents import Agent, Runner, RunContextWrapper

@dataclass
class UserContext:
    user_id: str
    name: str
    is_premium: bool

    async def fetch_orders(self):
        # Fetch from database
        return ["order1", "order2"]

# Context-aware tool
@function_tool
def get_user_info(ctx: RunContextWrapper[UserContext]) -> str:
    """Get information about the current user."""
    return f"User: {ctx.context.name}, Premium: {ctx.context.is_premium}"

# Agent typed with context
agent = Agent[UserContext](
    name="Personal Assistant",
    instructions="Help the user with their account",
    tools=[get_user_info],
)

# Run with context
context = UserContext(user_id="123", name="Alice", is_premium=True)
result = Runner.run_sync(agent, "What's my account info?", context=context)
```

### Dynamic Instructions with Context

```python
from agents import Agent, RunContextWrapper

def dynamic_instructions(ctx: RunContextWrapper[UserContext], agent: Agent) -> str:
    user = ctx.context
    base = f"You are helping {user.name}. "
    if user.is_premium:
        return base + "They are a premium user, provide VIP support."
    return base + "Provide standard support."

agent = Agent[UserContext](
    name="Support Agent",
    instructions=dynamic_instructions,  # Function instead of string
)
```

## Guardrails

### Input Guardrails

```python
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def check_appropriate_content(
    ctx, agent, input_data
) -> GuardrailFunctionOutput:
    """Check if input is appropriate."""
    # Use a cheap/fast model for validation
    validator = Agent(
        name="Validator",
        model="gpt-4.1-mini",
        instructions="Return 'inappropriate' if content is harmful, else 'ok'",
    )
    result = await Runner.run(validator, str(input_data))

    is_inappropriate = "inappropriate" in result.final_output.lower()

    return GuardrailFunctionOutput(
        output_info={"validation": result.final_output},
        tripwire_triggered=is_inappropriate,
    )

# Agent with input guardrail
agent = Agent(
    name="Assistant",
    instructions="Be helpful",
    input_guardrails=[check_appropriate_content],
)

# If guardrail trips, raises InputGuardrailTripwireTriggered
try:
    result = await Runner.run(agent, user_input)
except InputGuardrailTripwireTriggered:
    print("Content blocked by guardrail")
```

### Output Guardrails

```python
from agents import Agent, output_guardrail, GuardrailFunctionOutput

@output_guardrail
async def check_no_pii(ctx, agent, output) -> GuardrailFunctionOutput:
    """Ensure no PII in output."""
    # Check for patterns like SSN, credit cards, etc.
    has_pii = contains_pii(str(output))

    return GuardrailFunctionOutput(
        output_info={"pii_check": "failed" if has_pii else "passed"},
        tripwire_triggered=has_pii,
    )

agent = Agent(
    name="Data Assistant",
    instructions="Help with data queries",
    output_guardrails=[check_no_pii],
)
```

## MCP Integration

### Stdio MCP Server

```python
from agents import Agent
from agents.mcp import MCPServerStdio

# Connect to local MCP server via stdio
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
            instructions="Help manage files",
            tools=tools,
        )

        result = await Runner.run(agent, "List files in the directory")
```

### HTTP MCP Server

```python
from agents.mcp import MCPServerStreamableHttp

server = MCPServerStreamableHttp(
    url="https://mcp-server.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=30,
)

async def main():
    async with server:
        tools = await server.list_tools()
        agent = Agent(name="MCP Agent", tools=tools)
        result = await Runner.run(agent, "Use MCP tools")
```

### Hosted MCP Tools

```python
from agents import Agent
from agents.tool import HostedMCPTool

# MCP tool hosted by OpenAI
mcp_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "my-mcp-server",
        "server_url": "https://mcp.example.com",
        "allowed_tools": ["tool1", "tool2"],
    }
)

agent = Agent(
    name="MCP Agent",
    tools=[mcp_tool],
)
```

## Conversation Management

### Manual History Management

```python
from agents import Agent, Runner

agent = Agent(name="Chat", instructions="Be helpful")

# First message
result1 = await Runner.run(agent, "My name is Alice")

# Build history for next turn
history = result1.to_input_list()

# Continue conversation
result2 = await Runner.run(agent, "What's my name?", input=history)
print(result2.final_output)  # "Your name is Alice"
```

### Using Sessions (Automatic)

```python
from agents import Agent, Runner
from agents.sessions import SQLiteSession

agent = Agent(name="Chat", instructions="Be helpful")

# Session automatically manages history
session = SQLiteSession("conversation_123")

# Messages automatically stored/retrieved
result1 = await Runner.run(agent, "My name is Bob", session=session)
result2 = await Runner.run(agent, "What's my name?", session=session)
print(result2.final_output)  # "Your name is Bob"
```

### Server-Managed Conversations

```python
from agents import Agent, Runner
from openai import AsyncOpenAI

client = AsyncOpenAI()

# Create conversation
conversation = await client.conversations.create()

agent = Agent(name="Chat", instructions="Be helpful")

# Use conversation_id for automatic management
result = await Runner.run(
    agent,
    "Hello!",
    conversation_id=conversation.id,
)
```

## Tracing & Debugging

### Basic Tracing

```python
from agents import Agent, Runner, trace

async def workflow():
    agent = Agent(name="Worker", instructions="Process tasks")

    # Wrap multiple operations in a trace
    with trace("My Workflow"):
        result1 = await Runner.run(agent, "Step 1")
        result2 = await Runner.run(agent, f"Step 2: {result1.final_output}")

    return result2

# View traces at: https://platform.openai.com/traces
```

### Custom Spans

```python
from agents import custom_span

async def my_function():
    with custom_span("my-operation"):
        # Your code here
        result = await some_async_operation()
    return result
```

### Disable Tracing

```python
from agents import Runner, RunConfig

# Disable for specific run
result = await Runner.run(
    agent,
    "Hello",
    run_config=RunConfig(tracing_disabled=True),
)

# Or globally via environment
# export OPENAI_AGENTS_DISABLE_TRACING=1
```

## Results & Outputs

### Accessing Results

```python
from agents import Agent, Runner

result = await Runner.run(agent, "Hello")

# Final output (string or structured type)
print(result.final_output)

# Which agent responded last
print(result.last_agent.name)

# All items generated during run
for item in result.new_items:
    if item.type == "message_output_item":
        print(f"Message: {item.raw_item}")
    elif item.type == "tool_call_item":
        print(f"Tool called: {item.raw_item}")

# Input/output guardrail results
print(result.input_guardrail_results)
print(result.output_guardrail_results)

# Raw model responses
print(result.raw_responses)
```

### Chaining Runs

```python
agent1 = Agent(name="Researcher", instructions="Research topics")
agent2 = Agent(name="Writer", instructions="Write based on research")

# Run 1
research = await Runner.run(agent1, "Research Python async")

# Pass output to next agent
article = await Runner.run(agent2, f"Write about: {research.final_output}")
```

## Using Different Models

### OpenAI Models

```python
from agents import Agent

# Default (gpt-4.1)
agent = Agent(name="Default", instructions="...")

# Specific model
agent = Agent(name="GPT-5", model="gpt-5", instructions="...")

# Mini model for simple tasks
agent = Agent(name="Fast", model="gpt-4.1-mini", instructions="...")
```

### Non-OpenAI Models (LiteLLM)

```python
from agents import Agent

# Anthropic Claude
agent = Agent(
    name="Claude",
    model="litellm/anthropic/claude-3-5-sonnet-20240620",
    instructions="..."
)

# Google Gemini
agent = Agent(
    name="Gemini",
    model="litellm/gemini/gemini-pro",
    instructions="..."
)

# Local Ollama
agent = Agent(
    name="Local",
    model="litellm/ollama/llama2",
    instructions="..."
)
```

### Custom OpenAI-Compatible Endpoint

```python
from agents import Agent, set_default_openai_client
from openai import AsyncOpenAI

# Set custom endpoint globally
client = AsyncOpenAI(base_url="https://my-endpoint.com/v1")
set_default_openai_client(client)

agent = Agent(name="Custom", instructions="...")
```

## Error Handling

```python
from agents import Agent, Runner
from agents.exceptions import (
    AgentsException,
    MaxTurnsExceeded,
    ModelBehaviorError,
    UserError,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

async def safe_run():
    agent = Agent(name="Agent", instructions="...")

    try:
        result = await Runner.run(agent, "Hello", run_config=RunConfig(max_turns=5))
        return result.final_output

    except MaxTurnsExceeded:
        return "Agent took too many turns"

    except InputGuardrailTripwireTriggered as e:
        return f"Input blocked: {e.guardrail_result}"

    except OutputGuardrailTripwireTriggered as e:
        return f"Output blocked: {e.guardrail_result}"

    except ModelBehaviorError as e:
        return f"Model error: {e}"

    except AgentsException as e:
        return f"Agent error: {e}"
```

## Complete Example: Customer Support System

```python
from agents import Agent, Runner, function_tool, handoff
from pydantic import BaseModel
from dataclasses import dataclass

# Context
@dataclass
class CustomerContext:
    customer_id: str
    name: str
    tier: str  # "free", "pro", "enterprise"

# Tools
@function_tool
def lookup_order(ctx: RunContextWrapper[CustomerContext], order_id: str) -> str:
    """Look up order details."""
    return f"Order {order_id} for customer {ctx.context.customer_id}: Shipped"

@function_tool
def process_refund(ctx: RunContextWrapper[CustomerContext], order_id: str, amount: float) -> str:
    """Process a refund for an order."""
    return f"Refund of ${amount} processed for order {order_id}"

# Specialist agents
billing_agent = Agent[CustomerContext](
    name="Billing Specialist",
    instructions="""You handle billing inquiries.
    - Look up orders using the lookup_order tool
    - Process refunds when appropriate
    - Be professional and empathetic""",
    tools=[lookup_order, process_refund],
)

tech_agent = Agent[CustomerContext](
    name="Technical Support",
    instructions="""You handle technical issues.
    - Help with product setup and troubleshooting
    - Escalate complex issues to engineering""",
)

# Triage agent
def triage_instructions(ctx: RunContextWrapper[CustomerContext], agent: Agent) -> str:
    customer = ctx.context
    base = f"You are helping {customer.name} ({customer.tier} tier).\n"
    base += "Route to appropriate specialist:\n"
    base += "- Billing questions -> Billing Specialist\n"
    base += "- Technical issues -> Technical Support\n"

    if customer.tier == "enterprise":
        base += "\nThis is an enterprise customer - prioritize their request."

    return base

triage_agent = Agent[CustomerContext](
    name="Support Triage",
    instructions=triage_instructions,
    handoffs=[billing_agent, tech_agent],
)

# Run the system
async def handle_support_request(customer_id: str, message: str):
    # Load customer data
    context = CustomerContext(
        customer_id=customer_id,
        name="Alice Smith",
        tier="pro",
    )

    result = await Runner.run(
        triage_agent,
        message,
        context=context,
    )

    return {
        "response": result.final_output,
        "handled_by": result.last_agent.name,
    }

# Usage
response = await handle_support_request(
    "cust_123",
    "I need a refund for order #456"
)
print(response)
```

## Best Practices

### 1. Agent Design

```python
# Good: Clear, specific instructions
agent = Agent(
    name="Order Processor",
    instructions="""Process customer orders.

    Guidelines:
    - Verify all required fields before processing
    - Apply discounts for orders over $100
    - Send confirmation after successful processing

    You have access to: lookup_product, create_order, send_email
    """,
    tools=[lookup_product, create_order, send_email],
)

# Avoid: Vague instructions
agent = Agent(
    name="Helper",
    instructions="Help with stuff",  # Too vague
)
```

### 2. Tool Design

```python
# Good: Clear docstring with Args
@function_tool
def search_products(
    query: str,
    category: str = "all",
    max_results: int = 10
) -> str:
    """Search for products in the catalog.

    Args:
        query: Search terms to find products.
        category: Filter by category (default: all).
        max_results: Maximum number of results (default: 10).
    """
    return "..."

# Avoid: Missing docstring
@function_tool
def search(q: str) -> str:  # No docstring - LLM won't know what this does
    return "..."
```

### 3. Error Handling

```python
# Use try/except for graceful handling
async def process_request(user_input: str):
    try:
        result = await Runner.run(agent, user_input)
        return {"success": True, "response": result.final_output}
    except MaxTurnsExceeded:
        return {"success": False, "error": "Request too complex"}
    except InputGuardrailTripwireTriggered:
        return {"success": False, "error": "Invalid input"}
```

### 4. Use Appropriate Models

```python
# Fast, cheap model for simple tasks
validator = Agent(model="gpt-4.1-mini", ...)

# Powerful model for complex reasoning
analyst = Agent(model="gpt-4.1", ...)

# Most capable for critical tasks
expert = Agent(model="gpt-5", ...)
```

## Resources

- [Official Documentation](https://openai.github.io/openai-agents-python/)
- [GitHub Repository](https://github.com/openai/openai-agents-python)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Tracing Dashboard](https://platform.openai.com/traces)
