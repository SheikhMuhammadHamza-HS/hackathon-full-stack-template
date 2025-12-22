# Quickstart: Chat Conversation Persistence

**Feature**: 002-chat-database-schema
**Status**: Implemented

## Overview

Database tables for storing chat conversations and messages. This feature provides the persistence layer only - no API endpoints or UI.

## Prerequisites

- ✅ User model exists (from 001-user-auth)
- ✅ Neon PostgreSQL database configured
- ✅ Backend environment running

## Verification Steps

### 1. Check Tables Exist

```bash
# Connect to your Neon database or use Neon console
psql $DATABASE_URL
```

```sql
-- List tables
\dt

-- Should show:
-- conversations
-- messages
```

### 2. Verify Schema

```sql
-- Check conversations table
\d conversations

-- Expected columns:
-- id | integer | primary key
-- user_id | varchar(255) | foreign key → users.id
-- created_at | timestamp
-- updated_at | timestamp
```

```sql
-- Check messages table
\d messages

-- Expected columns:
-- id | integer | primary key
-- user_id | varchar(255) | foreign key → users.id
-- conversation_id | integer | foreign key → conversations.id
-- role | varchar(20)
-- content | text
-- tool_calls | text (nullable)
-- created_at | timestamp
```

### 3. Check Indexes

```sql
-- List indexes
SELECT indexname, tablename FROM pg_indexes
WHERE tablename IN ('conversations', 'messages');

-- Should show:
-- idx_conversations_user_id
-- idx_messages_conversation_id
-- idx_messages_user_id
```

### 4. Test Foreign Keys

```sql
-- Try to create message without valid conversation (should fail)
INSERT INTO messages (user_id, conversation_id, role, content, created_at)
VALUES ('fake-user-id', 9999, 'user', 'test', NOW());

-- Should get error: foreign key constraint violation
```

### 5. Test Cascade Delete

```sql
-- Create test conversation
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES ('test-user-id', NOW(), NOW())
RETURNING id;

-- Create test message
INSERT INTO messages (user_id, conversation_id, role, content, created_at)
VALUES ('test-user-id', <conversation_id>, 'user', 'test message', NOW());

-- Delete conversation
DELETE FROM conversations WHERE id = <conversation_id>;

-- Verify message also deleted
SELECT * FROM messages WHERE conversation_id = <conversation_id>;
-- Should return 0 rows
```

## Implementation Files

### Models
**File**: `backend/app/models.py`

Key additions:
- `class Conversation(SQLModel, table=True)`: Lines ~50-60
- `class Message(SQLModel, table=True)`: Lines ~60-75
- Relationships defined with back_populates

### Migration
**File**: `backend/alembic/versions/0038046a8779_add_conversations_and_messages_tables_.py`

Generated with:
```bash
cd backend
alembic revision --autogenerate -m "add conversations and messages tables"
alembic upgrade head
```

## Quick Reference

### Create Conversation (Python)
```python
from app.models import Conversation
from datetime import datetime

conversation = Conversation(
    user_id="user-uuid",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
session.add(conversation)
await session.commit()
```

### Create Message (Python)
```python
from app.models import Message

message = Message(
    user_id="user-uuid",
    conversation_id=1,
    role="user",
    content="Hello AI",
    created_at=datetime.utcnow()
)
session.add(message)
await session.commit()
```

### Query Conversations (Python)
```python
from sqlmodel import select

# Get user's conversations
result = await session.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
)
conversations = result.scalars().all()
```

### Query Messages (Python)
```python
# Get conversation messages
result = await session.execute(
    select(Message)
    .where(
        Message.conversation_id == conv_id,
        Message.user_id == user_id
    )
    .order_by(Message.created_at.asc())
)
messages = result.scalars().all()
```

## Common Issues

### Issue: Migration Already Applied
**Symptom**: `alembic upgrade head` says "Target database is not up to date"
**Solution**: Migration already applied, check with `alembic current`

### Issue: Foreign Key Violation
**Symptom**: "violates foreign key constraint conversations_user_id_fkey"
**Cause**: Trying to create conversation for non-existent user
**Fix**: Ensure user exists in users table first

### Issue: Cannot Delete User
**Symptom**: "violates foreign key constraint" when deleting user
**Cause**: User has conversations that reference them
**Fix**: Delete conversations first, or ensure CASCADE DELETE is set

## Next Steps

After verifying this database layer:
1. Proceed to 003-ai-agent (uses these tables to save messages)
2. Proceed to 004-chat-ui (uses these tables to display history)

## Related Specifications

- Previous: 001-user-auth (provides User model)
- Next: 003-ai-agent (consumes these tables)
- Next: 004-chat-ui (displays data from these tables)
