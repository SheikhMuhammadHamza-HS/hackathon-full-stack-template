# Data Model: Dapr State Store for Chatbot

**Feature**: 008-dapr-state-chatbot
**Date**: 2025-12-25

## State Store Entities

### ConversationState

Primary entity stored in Dapr State Store. Replaces `conversations` and `messages` database tables.

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | string | Unique conversation identifier |
| user_id | string | Owner user ID (from JWT) |
| created_at | datetime | Conversation creation timestamp |
| updated_at | datetime | Last update timestamp |
| messages | MessageEntry[] | Array of conversation messages |

**State Key**: `chat:{user_id}:{conversation_id}`

**Constraints**:
- Max 200 messages per conversation
- TTL: 30 days (configurable)
- User isolation enforced via key pattern

---

### MessageEntry

Individual message within a conversation.

| Field | Type | Description |
|-------|------|-------------|
| role | enum | "user" or "assistant" |
| content | string | Message text (max 10000 chars) |
| timestamp | datetime | Message creation time |
| tool_calls | ToolCallInfo[] | Optional tool execution metadata |

**Constraints**:
- role MUST be "user" or "assistant"
- content MUST be non-empty string
- timestamp MUST be valid ISO 8601

---

### ToolCallInfo

Tool execution metadata for assistant messages.

| Field | Type | Description |
|-------|------|-------------|
| tool | string | Tool name (e.g., "add_task") |
| parameters | object | Tool input parameters |
| result | object | Tool execution result |

---

## State Store Component

### Dapr Component Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: database-credentials
      key: connection-string
  - name: tableName
    value: "dapr_state"
  - name: keyPrefix
    value: "name"
```

**Backend**: PostgreSQL (Neon)

**Table Created by Dapr**:
```sql
CREATE TABLE dapr_state (
    key TEXT PRIMARY KEY,
    value JSONB,
    isbinary BOOLEAN,
    insertdate TIMESTAMP,
    updatedate TIMESTAMP
);
```

---

## Migration: From Database Tables to State Store

### Source Tables (to be deprecated)

**conversations**:
| Column | Type |
|--------|------|
| id | integer PK |
| user_id | string FK |
| created_at | timestamp |
| updated_at | timestamp |

**messages**:
| Column | Type |
|--------|------|
| id | integer PK |
| user_id | string FK |
| conversation_id | integer FK |
| role | string |
| content | text |
| tool_calls | text (JSON) |
| created_at | timestamp |

### Migration Script Logic

```python
async def migrate_to_state_store():
    """Migrate existing conversations to Dapr State Store"""

    # 1. Fetch all conversations
    conversations = await db.execute(
        select(Conversation).order_by(Conversation.id)
    )

    for conv in conversations:
        # 2. Fetch messages for this conversation
        messages = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
        )

        # 3. Build state payload
        state = ConversationState(
            conversation_id=str(conv.id),
            user_id=conv.user_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[
                MessageEntry(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.created_at,
                    tool_calls=json.loads(msg.tool_calls) if msg.tool_calls else None
                )
                for msg in messages
            ]
        )

        # 4. Save to Dapr State Store
        key = f"chat:{conv.user_id}:{conv.id}"
        await state_store.save_state(key, state.dict())

        print(f"Migrated conversation {conv.id} for user {conv.user_id}")
```

### Post-Migration Alembic Script

```python
"""deprecate_chat_tables

Revision ID: xxx
"""

def upgrade():
    # Drop tables after migration verified
    op.drop_table('messages')
    op.drop_table('conversations')

def downgrade():
    # Recreate tables if rollback needed
    op.create_table('conversations', ...)
    op.create_table('messages', ...)
```

---

## Relationships

```
User (1) ──────────── (*) ConversationState
                            │
                            └── (*) MessageEntry
                                      │
                                      └── (*) ToolCallInfo
```

**Notes**:
- User isolation enforced via state key pattern
- No foreign key relationships (state store is document-based)
- Conversation ID included in state for backwards compatibility

---

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| ConversationState | user_id | Must match JWT claim |
| ConversationState | messages | Max 200 entries |
| MessageEntry | role | Must be "user" or "assistant" |
| MessageEntry | content | Non-empty, max 10000 chars |
| State Key | format | Must match `chat:{user_id}:{conversation_id}` |

---

## Indexes (Dapr PostgreSQL)

Dapr automatically creates:
- Primary key index on `key` column
- Automatic cleanup based on TTL metadata

No additional indexes needed - queries are by exact key only.
