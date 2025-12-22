# Tasks: Chat Conversation Persistence

**Input**: Implemented code in `backend/app/models.py` and migration files
**Status**: All tasks completed (spec written after implementation)

## Format: `- [x] [ID] Description`

All tasks marked complete as implementation already exists.

---

## Phase 1: Database Models

**Purpose**: Create SQLModel classes for Conversation and Message

- [x] T001 Add Conversation model to backend/app/models.py with user_id foreign key
- [x] T002 Add created_at and updated_at timestamp fields to Conversation
- [x] T003 Add relationship from Conversation to User (back_populates="conversations")
- [x] T004 Add relationship from Conversation to Messages (cascade delete)
- [x] T005 Add Message model to backend/app/models.py
- [x] T006 Add user_id, conversation_id foreign keys to Message
- [x] T007 Add role field to Message with 'user' or 'assistant' values
- [x] T008 Add content field to Message using Text column type
- [x] T009 Add tool_calls field to Message as nullable TEXT (JSON storage)
- [x] T010 Add created_at timestamp to Message
- [x] T011 Add relationships from Message to Conversation and User

**Implemented in**: `backend/app/models.py` (lines added to existing file)

---

## Phase 2: Database Migration

**Purpose**: Generate and apply Alembic migration to create tables

- [x] T012 Generate Alembic migration: `alembic revision --autogenerate -m "add conversations and messages tables"`
- [x] T013 Verify migration file created in backend/alembic/versions/
- [x] T014 Review migration SQL for correctness (tables, indexes, constraints)
- [x] T015 Apply migration: `alembic upgrade head`
- [x] T016 Verify conversations table created in Neon database
- [x] T017 Verify messages table created in Neon database
- [x] T018 Verify indexes created: idx_conversations_user_id, idx_messages_conversation_id
- [x] T019 Verify foreign key constraints working (test cascade delete)

**Implemented in**: `backend/alembic/versions/0038046a8779_add_conversations_and_messages_tables_.py`

---

## Phase 3: Data Access Patterns

**Purpose**: Ensure efficient query patterns are documented

- [x] T020 Document get-or-create conversation pattern for chat endpoint
- [x] T021 Document fetch conversation history pattern (messages ordered by created_at)
- [x] T022 Document list user conversations pattern (ordered by updated_at DESC)
- [x] T023 Document message save pattern (atomic with conversation update)
- [x] T024 Document cascade delete pattern (conversation deletion)

**Implemented in**: `backend/app/routers/chat.py` (various helper functions)

---

## Phase 4: Testing & Verification

**Purpose**: Verify database schema and constraints

- [x] T025 Test conversation creation: verify record saved in database
- [x] T026 Test message creation: verify record saved with correct foreign keys
- [x] T027 Test conversation listing: verify user sees only their conversations
- [x] T028 Test message history: verify chronological order (oldest first)
- [x] T029 Test cascade delete: delete conversation, verify messages also deleted
- [x] T030 Test user deletion cascade: delete user, verify conversations and messages deleted
- [x] T031 Test foreign key constraint: verify cannot create message for non-existent conversation
- [x] T032 Test user isolation: verify User A cannot query User B's conversations

**Verified via**: Manual testing with multiple users and conversation operations

---

## Dependencies & Execution Order

### Prerequisites (MUST exist before this feature)
- ✅ User model (from 001-user-auth)
- ✅ Neon PostgreSQL database configured
- ✅ SQLModel and Alembic installed
- ✅ Database connection working

### Provides To (Features that depend on this)
- 003-ai-agent: Needs tables to store chat messages
- 004-chat-ui: Needs tables to fetch conversation history

### Execution Order
1. Phase 1: Database Models (T001-T011) - MUST complete first
2. Phase 2: Migration (T012-T019) - Depends on Phase 1
3. Phase 3: Access Patterns (T020-T024) - Documentation only
4. Phase 4: Testing (T025-T032) - Verification after migration

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Models | 11 | SQLModel classes |
| Phase 2: Migration | 8 | Alembic migration |
| Phase 3: Patterns | 5 | Query patterns |
| Phase 4: Testing | 8 | Verification tests |
| **Total** | **32** | All completed ✅ |

---

## Implementation Evidence

### Files Created/Modified
- ✅ `backend/app/models.py` - Added Conversation and Message models
- ✅ `backend/alembic/versions/0038046a8779_*.py` - Migration file
- ✅ Database tables created in Neon PostgreSQL

### Database Verification
```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversations', 'messages');

-- Check foreign keys
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f'
AND conrelid::regclass::text IN ('conversations', 'messages');
```

### Success Criteria
- ✅ Conversations table exists with proper schema
- ✅ Messages table exists with proper schema
- ✅ All indexes created
- ✅ Foreign key constraints enforced
- ✅ Cascade deletes working
- ✅ User isolation tested and verified
