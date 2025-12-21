# Data Model: AI-Powered Todo Chatbot

**Feature**: 002-ai-chatbot
**Branch**: `002-ai-chatbot`
**Date**: 2025-12-21
**Status**: Design Complete

## Overview

Phase III extends the Phase II data model with two new tables to support stateless conversation architecture. The existing User and Task tables remain unchanged. The new Conversation and Message tables enable persistent chat history that survives server restarts and supports multi-device continuity.

**Design Principle**: Conversation data follows the same user isolation pattern as Task data - every conversation and message belongs to exactly one user, enforced via foreign keys and query filters.

## Entity Relationship Diagram

```
┌─────────────────────┐
│      Users          │ (Phase II - Unchanged)
│─────────────────────│
│ id (PK)             │ TEXT (UUID)
│ email (UNIQUE)      │ TEXT
│ name                │ TEXT
│ password_hash       │ TEXT (nullable for OAuth)
│ oauth_provider      │ TEXT (nullable)
│ oauth_id            │ TEXT (nullable)
│ profile_picture     │ TEXT (nullable)
│ created_at          │ TIMESTAMP
│ updated_at          │ TIMESTAMP
└─────────────────────┘
          │
          │ 1:N
          ├──────────────────────────┐
          │                          │
          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐
│      Tasks          │    │   Conversations     │ (Phase III - NEW)
│─────────────────────│    │─────────────────────│
│ id (PK)             │    │ id (PK)             │ INTEGER (auto)
│ user_id (FK)        │    │ user_id (FK)        │ TEXT → users.id
│ title               │    │ created_at          │ TIMESTAMP
│ description         │    │ updated_at          │ TIMESTAMP
│ completed           │    └──────────┬──────────┘
│ created_at          │               │ 1:N
│ updated_at          │               │
└─────────────────────┘               ▼
                              ┌─────────────────────┐
                              │     Messages        │ (Phase III - NEW)
                              │─────────────────────│
                              │ id (PK)             │ INTEGER (auto)
                              │ user_id (FK)        │ TEXT → users.id
                              │ conversation_id (FK)│ INTEGER → conversations.id
                              │ role                │ TEXT ('user'|'assistant')
                              │ content             │ TEXT
                              │ tool_calls          │ JSONB (nullable)
                              │ created_at          │ TIMESTAMP
                              └─────────────────────┘
```

**Relationships**:
- One user has many conversations (1:N)
- One user has many tasks (1:N) - existing from Phase II
- One conversation has many messages (1:N)
- Messages belong to both conversation AND user (for efficient filtering)

## Entities

### Conversation Entity (NEW)

**Purpose**: Represents a chat session between a user and the AI assistant. Groups related messages together for context and organization.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| user_id | TEXT | NOT NULL, FOREIGN KEY → users.id | Owner of this conversation |
| created_at | TIMESTAMP | DEFAULT NOW() | When conversation started |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `idx_conversations_user_id` on (user_id) - Fast user conversation lookup
- `idx_conversations_updated_at` on (updated_at DESC) - Recent conversations first

**Constraints**:
- Foreign key to users.id with CASCADE delete (if user deleted, conversations deleted)
- user_id must exist in users table (referential integrity)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """Conversation between user and AI assistant."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules**:
- user_id must be valid UUID format
- user_id must exist in users table
- created_at ≤ updated_at (automatically maintained)

**State Transitions**:
- Created: When user sends first message without conversation_id
- Updated: Every time a new message added (updated_at refreshed)
- Deleted: When user explicitly deletes conversation or user account deleted (CASCADE)

**Usage Pattern**:
```python
# Create new conversation
conversation = Conversation(user_id=authenticated_user_id)
session.add(conversation)
await session.commit()

# Update timestamp when new message added
conversation.updated_at = datetime.utcnow()
await session.commit()

# List user's recent conversations
conversations = await session.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
    .limit(20)
)
```

---

### Message Entity (NEW)

**Purpose**: Represents a single message in a conversation, sent either by the user or the AI assistant. Stores message content, role, and optional metadata about tool calls.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| user_id | TEXT | NOT NULL, FOREIGN KEY → users.id | Owner (for filtering) |
| conversation_id | INTEGER | NOT NULL, FOREIGN KEY → conversations.id | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender |
| content | TEXT | NOT NULL | Message text content |
| tool_calls | JSONB | NULL | Tool execution metadata (assistant only) |
| created_at | TIMESTAMP | DEFAULT NOW() | Message timestamp |

**Indexes**:
- `idx_messages_conversation_id` on (conversation_id) - Fast conversation history fetch
- `idx_messages_created_at` on (conversation_id, created_at) - Chronological ordering
- `idx_messages_user_id` on (user_id) - User isolation queries

**Constraints**:
- Foreign key to users.id with CASCADE delete
- Foreign key to conversations.id with CASCADE delete
- role must be exactly 'user' or 'assistant' (CHECK constraint)
- content cannot be empty string
- tool_calls must be valid JSON if present

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text
from datetime import datetime
from typing import Optional
import json

class Message(SQLModel, table=True):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        arbitrary_types_allowed = True
```

**Validation Rules**:
- role must be 'user' or 'assistant' (enforced by CHECK constraint and application code)
- content must not be empty
- content maximum length: 10,000 characters (per spec constraint)
- user_id must exist in users table
- conversation_id must exist in conversations table
- If role is 'user', tool_calls must be NULL
- If role is 'assistant', tool_calls may be NULL or valid JSON array

**State Transitions**:
- Created: When message sent (user) or response generated (assistant)
- Immutable: Messages never updated or deleted (append-only log)

**Usage Pattern**:
```python
# Save user message
user_message = Message(
    user_id=authenticated_user_id,
    conversation_id=conversation.id,
    role="user",
    content=user_input_text
)
session.add(user_message)

# Save assistant message with tool calls
assistant_message = Message(
    user_id=authenticated_user_id,
    conversation_id=conversation.id,
    role="assistant",
    content=agent_response.text,
    tool_calls=json.dumps(agent_response.tool_calls) if agent_response.tool_calls else None
)
session.add(assistant_message)

# Fetch conversation history (chronological order)
history = await session.execute(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)  # User isolation
    .order_by(Message.created_at.asc())
    .limit(50)  # Recent 50 for performance
)
```

---

## Relationships

### User → Conversations (1:N)
- One user can have multiple conversations
- User deletion cascades to conversations (ON DELETE CASCADE)
- Foreign key enforced at database level

### User → Messages (1:N)
- One user can have multiple messages (across all conversations)
- User deletion cascades to messages (ON DELETE CASCADE)
- Used for filtering: "Show all my messages"

### Conversation → Messages (1:N)
- One conversation contains multiple messages (user and assistant messages interleaved)
- Conversation deletion cascades to messages (ON DELETE CASCADE)
- Messages fetched in chronological order for chat history

### User → Tasks (1:N)
- Existing relationship from Phase II, unchanged
- Tasks table not modified in Phase III
- MCP tools operate on this relationship

---

## Database Migration Strategy

### Migration File

**Filename**: `[timestamp]_add_conversations_and_messages_tables.py`

**Generated via**:
```bash
alembic revision --autogenerate -m "add conversations and messages tables for chatbot"
```

### Migration Content

```python
"""Add conversations and messages tables for chatbot

Revision ID: [auto-generated]
Revises: e1fe1dd186cb (OAuth fields migration)
Create Date: 2025-12-21
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'], unique=False, postgresql_using='btree', postgresql_ops={'updated_at': 'DESC'})

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

### Migration Execution

```bash
# Generate migration
alembic revision --autogenerate -m "add conversations and messages tables for chatbot"

# Review migration file
cat backend/alembic/versions/[timestamp]_add_conversations_and_messages_tables.py

# Apply migration
alembic upgrade head

# Verify tables created
# (via Neon dashboard or SQL query: SELECT tablename FROM pg_tables WHERE schemaname = 'public';)
```

---

## Data Integrity Rules

### Referential Integrity
1. **user_id in conversations must exist in users table**: Enforced by foreign key constraint
2. **user_id in messages must exist in users table**: Enforced by foreign key constraint
3. **conversation_id in messages must exist in conversations table**: Enforced by foreign key constraint

### Cascade Delete Behavior
1. **Delete user → Delete conversations → Delete messages**: Full cleanup on user deletion
2. **Delete conversation → Delete messages**: Cleanup conversation thread
3. **Delete task → No effect on conversations**: Tasks and conversations are independent

### Data Validation
1. **role must be 'user' or 'assistant'**: CHECK constraint + application validation
2. **content cannot be empty**: NOT NULL constraint + application validation (min 1 character)
3. **tool_calls must be valid JSON if present**: Application validation before save
4. **Timestamps auto-managed**: created_at set on INSERT, updated_at refreshed on conversation update

### Immutability
- Messages are append-only (no UPDATE operations)
- Message deletion not exposed via API (only CASCADE from conversation/user deletion)
- Conversation updated_at is only field that changes (reflects last message time)

---

## Query Patterns

### Common Queries

**Get User's Recent Conversations**:
```sql
SELECT id, created_at, updated_at
FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20;

-- Uses index: idx_conversations_user_id + idx_conversations_updated_at
-- Expected performance: < 50ms
```

**Get Conversation History**:
```sql
SELECT id, role, content, tool_calls, created_at
FROM messages
WHERE conversation_id = :conversation_id
  AND user_id = :user_id  -- User isolation
ORDER BY created_at ASC
LIMIT 50;

-- Uses index: idx_messages_conversation_id + idx_messages_created_at
-- Expected performance: < 100ms for 50 messages
```

**Create New Conversation**:
```sql
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES (:user_id, NOW(), NOW())
RETURNING id;

-- Expected performance: < 50ms
```

**Save Message**:
```sql
INSERT INTO messages (user_id, conversation_id, role, content, tool_calls, created_at)
VALUES (:user_id, :conversation_id, :role, :content, :tool_calls, NOW())
RETURNING id;

UPDATE conversations
SET updated_at = NOW()
WHERE id = :conversation_id;

-- Expected performance: < 100ms (two queries in transaction)
```

**Count User's Messages**:
```sql
SELECT COUNT(*) as message_count
FROM messages
WHERE user_id = :user_id;

-- Uses index: idx_messages_user_id
-- Expected performance: < 50ms
```

### Security Queries

All queries MUST include user_id filter to enforce isolation:

```python
# ✅ CORRECT: Always filter by authenticated user_id
messages = await session.execute(
    select(Message)
    .where(Message.conversation_id == conv_id)
    .where(Message.user_id == authenticated_user_id)  # CRITICAL!
    .order_by(Message.created_at.asc())
)

# ❌ WRONG: Missing user_id check (security vulnerability)
messages = await session.execute(
    select(Message)
    .where(Message.conversation_id == conv_id)
    # Missing: .where(Message.user_id == authenticated_user_id)
)
```

---

## Data Lifecycle

### Conversation Lifecycle

```
[Created] ──→ [Active] ──→ [Idle] ──→ [Deleted]
    │            │           │           │
    │            │           │           │
User sends  Multiple    No activity  User/system
first msg   exchanges   (no delete   deletes or
            over time   in Phase III) user removed
```

**States**:
- **Created**: conversation_id generated, created_at set
- **Active**: messages being exchanged, updated_at refreshed
- **Idle**: No new messages, conversation exists indefinitely (no auto-deletion in Phase III)
- **Deleted**: CASCADE from user deletion (only deletion mechanism in Phase III)

### Message Lifecycle

```
[User types] ──→ [Saved to DB] ──→ [Displayed in history]
                       │
                       ├──→ [Agent processes]
                       │
                       └──→ [Agent response saved] ──→ [Displayed in history]
```

**Immutability**: Once saved, messages never change (append-only log)

---

## Storage Estimates

### Per-Message Storage

**User Message**:
- Metadata: ~50 bytes (id, user_id, conversation_id, role, created_at)
- Content: Average 100 bytes (typical task-related message)
- Total: ~150 bytes per user message

**Assistant Message**:
- Metadata: ~50 bytes
- Content: Average 200 bytes (AI responses tend to be wordier)
- Tool calls: Average 100 bytes JSON (tool name, parameters, result)
- Total: ~350 bytes per assistant message

**Conversation Metadata**:
- ~100 bytes per conversation (id, user_id, timestamps)

### Scale Estimates

**Per User** (10,000 messages max per spec):
- ~5,000 user messages × 150 bytes = 750 KB
- ~5,000 assistant messages × 350 bytes = 1.75 MB
- ~500 conversations × 100 bytes = 50 KB
- **Total: ~2.5 MB per user**

**100 Users**:
- ~250 MB total storage
- Well within Neon free tier limits

**1,000 Users**:
- ~2.5 GB total storage
- Still manageable on free tier with conversation pruning strategy (future phase)

---

## Performance Considerations

### Index Strategy

**Primary Indexes** (automatically created):
- conversations.id (primary key) - Point lookups
- messages.id (primary key) - Point lookups

**Secondary Indexes** (explicitly created):
- conversations.user_id - Filter by user (frequent)
- conversations.updated_at DESC - Sort by recent activity (frequent)
- messages.conversation_id - Fetch history (very frequent)
- messages (conversation_id, created_at) - Chronological ordering (very frequent)
- messages.user_id - User isolation filtering (frequent)

### Query Optimization

**Conversation History Fetch** (most frequent query):
```sql
-- Optimized with composite index
SELECT * FROM messages
WHERE conversation_id = 123 AND user_id = 'user456'
ORDER BY created_at ASC
LIMIT 50;

-- Index used: idx_messages_created_at (conversation_id, created_at)
-- Scan: 50 rows (LIMIT applied)
-- Expected: < 100ms
```

**Recent Conversations List**:
```sql
-- Optimized with two indexes
SELECT * FROM conversations
WHERE user_id = 'user456'
ORDER BY updated_at DESC
LIMIT 20;

-- Indexes used: idx_conversations_user_id, idx_conversations_updated_at
-- Scan: ~20 rows (LIMIT applied)
-- Expected: < 50ms
```

### Connection Pooling

Reuse existing Phase II connection pool configuration:
- pool_size: 5
- max_overflow: 10
- pool_pre_ping: True

No changes needed - conversation queries add minimal load.

---

## Data Consistency

### Atomic Operations

**Message Save Pattern** (user + assistant messages saved together):
```python
async with session.begin():
    # Save user message
    user_msg = Message(user_id=user_id, conversation_id=conv_id, role="user", content=user_text)
    session.add(user_msg)

    # Process with agent
    response = await agent.run(user_text)

    # Save assistant message
    assistant_msg = Message(user_id=user_id, conversation_id=conv_id, role="assistant", content=response.text)
    session.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    # Commit all or rollback all (atomic)
    await session.commit()
```

**Failure Scenarios**:
- If agent.run() fails: Rollback, user message not saved (idempotent retry possible)
- If database commit fails: Rollback, entire conversation state unchanged
- If OpenAI API fails: Return error, no database changes

### Concurrency Handling

**Scenario**: User sends message while previous message still processing

**Solution**: Database transactions handle concurrency
- updated_at uses database NOW() (not application time)
- Message ordering guaranteed by created_at (database time)
- No race conditions due to stateless architecture (each request independent)

---

## Privacy & Security

### User Isolation

**Rule**: Users can ONLY access their own conversations and messages

**Enforcement**:
1. **API Layer**: JWT validation, user_id from URL must match token
2. **Application Layer**: All queries filter by authenticated_user_id
3. **Database Layer**: Foreign keys enforce ownership, indexes optimize filtered queries

**Test Cases**:
- User A cannot fetch User B's conversation_id (403 Forbidden)
- User A cannot send message to User B's conversation_id (filtered out, effectively 404)
- Admin can view conversations only via separate admin endpoint (not via chat API)

### Sensitive Data

**Conversation Content**:
- Messages may contain personal task information
- Stored in database with same security as tasks (encrypted at rest by Neon)
- Not exposed in logs (sanitize before logging)

**Tool Call Metadata**:
- tool_calls column may contain task IDs and parameters
- Treated as sensitive (same isolation as message content)
- Used for debugging and audit trail

---

## Testing Data

### Sample Conversation

```sql
-- Conversation
INSERT INTO conversations (id, user_id, created_at, updated_at)
VALUES (1, 'user-123', '2025-12-21 10:00:00', '2025-12-21 10:05:00');

-- Messages
INSERT INTO messages (id, user_id, conversation_id, role, content, tool_calls, created_at) VALUES
(1, 'user-123', 1, 'user', 'Show my tasks', NULL, '2025-12-21 10:00:00'),
(2, 'user-123', 1, 'assistant', 'You have 2 tasks: 1. Buy milk (incomplete), 2. Call dentist (complete)', '[{"tool": "list_tasks", "params": {}, "result": {"tasks": [...]}}]', '2025-12-21 10:00:05'),
(3, 'user-123', 1, 'user', 'Add buy groceries', NULL, '2025-12-21 10:05:00'),
(4, 'user-123', 1, 'assistant', 'Task "Buy groceries" added successfully!', '[{"tool": "add_task", "params": {"title": "Buy groceries"}, "result": {"success": true, "task_id": 10}}]', '2025-12-21 10:05:02');
```

### Test Queries

**Fetch Conversation History**:
```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = 1 AND user_id = 'user-123'
ORDER BY created_at ASC;

-- Expected result: 4 rows in chronological order
```

**List User's Conversations**:
```sql
SELECT id, created_at, updated_at
FROM conversations
WHERE user_id = 'user-123'
ORDER BY updated_at DESC;

-- Expected result: 1 conversation
```

---

## Validation Rules

### Application-Level Validation

**Conversation Creation**:
```python
def validate_conversation_create(user_id: str):
    if not user_id:
        raise ValueError("user_id required")
    if not is_valid_uuid(user_id):
        raise ValueError("user_id must be valid UUID")
```

**Message Creation**:
```python
def validate_message(role: str, content: str, tool_calls: str = None):
    if role not in ["user", "assistant"]:
        raise ValueError("role must be 'user' or 'assistant'")
    if not content or len(content.strip()) == 0:
        raise ValueError("content cannot be empty")
    if len(content) > 10000:
        raise ValueError("content exceeds 10,000 character limit")
    if role == "user" and tool_calls is not None:
        raise ValueError("user messages cannot have tool_calls")
    if tool_calls and not is_valid_json(tool_calls):
        raise ValueError("tool_calls must be valid JSON")
```

---

## Summary

**New Tables**: 2 (Conversations, Messages)
**New Columns**: 11 total (4 in conversations, 7 in messages)
**New Indexes**: 5 (2 on conversations, 3 on messages)
**Foreign Keys**: 3 (conversations→users, messages→users, messages→conversations)
**Storage Impact**: ~2.5 MB per user (10,000 messages)
**Migration**: Single Alembic migration file
**Backward Compatibility**: Full (no changes to existing tables)
**Phase II Impact**: Zero (existing endpoints unaffected)

This data model enables stateless conversation architecture while maintaining Phase II's security and performance standards.
