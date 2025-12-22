# Data Model: Chat Conversation Persistence

**Feature**: 002-chat-database-schema
**Created**: 2025-12-22
**Status**: Implemented

## Database Schema

### Conversations Table

Stores chat sessions between users and AI assistant.

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| `user_id` | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Owner of conversation |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation started |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `idx_conversations_user_id` - Fast lookup of user's conversations
- `idx_conversations_updated_at` - Sort by most recent activity

**Foreign Keys**:
- `user_id` → `users.id` with CASCADE DELETE
  - When user deleted, all conversations deleted automatically

---

### Messages Table

Stores individual messages within conversations.

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at ASC);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| `user_id` | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Message owner (for filtering) |
| `conversation_id` | INTEGER | NOT NULL, FOREIGN KEY → conversations.id | Which conversation this belongs to |
| `role` | VARCHAR(20) | NOT NULL, CHECK ('user' or 'assistant') | Who sent the message |
| `content` | TEXT | NOT NULL | Message text content |
| `tool_calls` | TEXT | NULL | JSON array of tool calls (for assistant messages) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

**Indexes**:
- `idx_messages_conversation_id` - Fast message lookup by conversation
- `idx_messages_user_id` - Fast filtering by user
- `idx_messages_created_at` - Chronological ordering

**Foreign Keys**:
- `user_id` → `users.id` with CASCADE DELETE
- `conversation_id` → `conversations.id` with CASCADE DELETE
  - Deleting conversation removes all its messages

---

## SQLModel Definitions

### Conversation Model

**File**: `backend/app/models.py`

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
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Message Model

**File**: `backend/app/models.py`

```python
from sqlalchemy import Column, Text

class Message(SQLModel, table=True):
    """Message in a conversation (user or assistant)."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")
```

---

## Entity Relationships

```
User (1) ──────< Conversations (N)
                      │
                      │ 1
                      │
                      │ N
                 Messages (N) >────── User (1)
```

**Key Points**:
- One user has many conversations
- One conversation has many messages
- Messages redundantly reference user_id for efficient filtering
- CASCADE DELETE from User → Conversations → Messages

---

## Data Validation

### Conversation
- `user_id`: Must exist in users table
- `created_at`: Auto-set, cannot be modified
- `updated_at`: Auto-updated on new message

### Message
- `user_id`: Must exist in users table
- `conversation_id`: Must exist in conversations table
- `role`: Must be 'user' or 'assistant'
- `content`: Cannot be empty
- `tool_calls`: Valid JSON or NULL
- `created_at`: Auto-set, immutable

---

## Migration

**File**: `backend/alembic/versions/0038046a8779_add_conversations_and_messages_tables_.py`

**Generated via**:
```bash
alembic revision --autogenerate -m "add conversations and messages tables"
alembic upgrade head
```

**Creates**:
- conversations table
- messages table
- All indexes
- Foreign key constraints

---

## Query Patterns

### Get User's Conversations
```python
conversations = await session.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
)
```

### Get Conversation Messages
```python
messages = await session.execute(
    select(Message)
    .where(
        Message.conversation_id == conv_id,
        Message.user_id == user_id  # Security: double-check ownership
    )
    .order_by(Message.created_at.asc())
)
```

### Create New Message
```python
message = Message(
    user_id=user_id,
    conversation_id=conv_id,
    role="user",
    content="Hello AI",
    created_at=datetime.utcnow()
)
session.add(message)
await session.commit()
```

---

## Security Considerations

### User Isolation
- All conversation queries filter by user_id
- All message queries filter by user_id
- Cannot access other users' conversations via URL manipulation

### Data Integrity
- Foreign keys prevent orphaned messages
- CASCADE DELETE ensures cleanup
- CHECK constraint on role field

### Immutability
- Messages are append-only (no UPDATE allowed)
- Conversation history is immutable audit trail
- Only deletion supported (for privacy)

---

## Performance Optimizations

### Indexes
- `idx_conversations_user_id` - O(log n) user lookup
- `idx_messages_conversation_id` - O(log n) message lookup
- `idx_messages_created_at` - Fast chronological ordering

### Query Limits
- Limit conversation list to 20 most recent
- Consider pagination for messages if > 100

---

## Implementation Files

**Models**: `backend/app/models.py`
- Conversation class
- Message class

**Migration**: `backend/alembic/versions/0038046a8779_*.py`
- Table creation
- Index creation
- Constraints

**Database**: Neon PostgreSQL
- Project: hackathon_twp
- Tables: conversations, messages
