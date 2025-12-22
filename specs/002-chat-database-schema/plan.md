# Implementation Plan: Chat Conversation Persistence

**Feature**: 002-chat-database-schema
**Created**: 2025-12-22
**Status**: Implemented (documented after completion)

## Overview

Database persistence layer for chat conversations and messages, enabling conversation history to survive server restarts and support multi-device access.

## Architecture

### Database Design

**Two-Table Structure**:

```
┌─────────────────────┐
│   conversations     │
│─────────────────────│
│ id (PK)             │
│ user_id (FK)        │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │ 1:N
           ▼
┌─────────────────────┐
│     messages        │
│─────────────────────│
│ id (PK)             │
│ user_id (FK)        │
│ conversation_id (FK)│
│ role                │
│ content             │
│ tool_calls (JSON)   │
│ created_at          │
└─────────────────────┘
```

**Why This Design**:
- Conversations group related messages
- Messages redundantly store user_id for fast filtering
- Timestamps enable "most recent" sorting
- tool_calls stored as JSON for flexibility

---

## Key Decisions

### Decision 1: Redundant user_id in Messages

**Choice**: Store user_id in both Conversation AND Message tables

**Rationale**:
- Fast filtering without JOIN: `WHERE user_id = X`
- Security: Double-check message ownership
- Query optimization: Can filter messages directly

**Trade-off**: Slight data redundancy for significant performance gain

---

### Decision 2: Append-Only Messages (Immutable)

**Choice**: Messages cannot be edited or updated after creation

**Rationale**:
- Audit trail: Complete conversation history
- Simplicity: No UPDATE logic needed
- Security: Cannot tamper with past messages

**Implementation**: No UPDATE endpoint for messages

---

### Decision 3: Cascade Delete from Conversations

**Choice**: Deleting conversation deletes all its messages

**Rationale**:
- Privacy: User can remove conversation completely
- Data cleanup: No orphaned messages
- Simplicity: One delete operation

**Implementation**: SQLAlchemy cascade relationship

---

### Decision 4: Tool Calls as JSON Text

**Choice**: Store tool_calls as TEXT column with JSON content

**Rationale**:
- Flexible: Can store any tool call structure
- Simple: No separate tool_calls table needed
- PostgreSQL: Can query JSON if needed later

**Format**:
```json
[
  {
    "tool": "add_task",
    "parameters": {"title": "Buy milk"},
    "result": {"success": true, "task_id": 5}
  }
]
```

---

## Implementation Phases

### Phase 1: Schema Design (30 min)
- Define Conversation entity
- Define Message entity
- Design relationships
- Plan indexes

### Phase 2: SQLModel Implementation (1 hour)
- Add Conversation model to models.py
- Add Message model to models.py
- Define relationships
- Test model validation

### Phase 3: Database Migration (30 min)
- Generate Alembic migration
- Review migration SQL
- Apply to Neon database
- Verify tables created

### Phase 4: Testing (1 hour)
- Test conversation creation
- Test message storage
- Test cascade deletes
- Test user isolation

---

## Files Implemented

### Backend
- `backend/app/models.py`: Conversation and Message models
- `backend/alembic/versions/0038046a8779_*.py`: Migration
- Database: Neon PostgreSQL with new tables

### No Frontend Changes
This is pure database layer - no UI components in this feature.

---

## Testing Strategy

### Database Integrity Tests
- Foreign key constraints enforced
- Cascade deletes work correctly
- Indexes improve query performance

### User Isolation Tests
- User A cannot query User B's conversations
- Cross-user message access blocked
- URL manipulation prevented

### Performance Tests
- Conversation list query < 200ms
- Message history query < 500ms
- Message insert < 100ms

---

## Success Metrics

- ✅ Conversations table created
- ✅ Messages table created
- ✅ All indexes present
- ✅ Foreign keys enforced
- ✅ Cascade deletes working
- ✅ User isolation verified
- ✅ No data loss on server restart

---

## Dependencies

**Requires**:
- 001-user-auth (User model)
- SQLModel library
- Alembic migrations
- Neon PostgreSQL

**Blocks**:
- 003-ai-agent (needs tables to save messages)
- 004-chat-ui (needs tables to load history)

---

## Risk Mitigation

### Risk: Message Table Growth
**Mitigation**:
- Index on created_at for efficient cleanup queries
- Future: Implement message retention policy (delete old conversations)

### Risk: Concurrent Message Writes
**Mitigation**:
- Database handles concurrency with transactions
- Auto-increment IDs prevent conflicts

### Risk: JSON Tool Calls Schema Changes
**Mitigation**:
- JSON is flexible
- No schema validation at database level
- Application validates structure
