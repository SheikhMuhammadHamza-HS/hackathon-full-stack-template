# Requirements Checklist: Chat Persistence

**Feature**: 002-chat-database-schema

## Database Schema

### Conversations Table
- [x] Table created in Neon PostgreSQL
- [x] id column (PRIMARY KEY, AUTO INCREMENT)
- [x] user_id column (FOREIGN KEY → users.id)
- [x] created_at column (TIMESTAMP)
- [x] updated_at column (TIMESTAMP)
- [x] Index on user_id
- [x] Index on updated_at DESC
- [x] CASCADE DELETE from users table

### Messages Table
- [x] Table created in Neon PostgreSQL
- [x] id column (PRIMARY KEY, AUTO INCREMENT)
- [x] user_id column (FOREIGN KEY → users.id)
- [x] conversation_id column (FOREIGN KEY → conversations.id)
- [x] role column (VARCHAR, 'user' or 'assistant')
- [x] content column (TEXT, NOT NULL)
- [x] tool_calls column (TEXT, NULLABLE, JSON format)
- [x] created_at column (TIMESTAMP)
- [x] Index on conversation_id
- [x] Index on user_id
- [x] Index on created_at
- [x] CASCADE DELETE from conversations table

## SQLModel Models

### Conversation Model
- [x] Conversation class defined in backend/app/models.py
- [x] All fields match database schema
- [x] Relationship to User defined
- [x] Relationship to Messages defined with cascade
- [x] Timestamps use default_factory=datetime.utcnow

### Message Model
- [x] Message class defined in backend/app/models.py
- [x] All fields match database schema
- [x] Relationship to Conversation defined
- [x] Relationship to User defined
- [x] Text columns use Column(Text) for large content

## Database Migration

- [x] Alembic migration file generated
- [x] Migration creates conversations table
- [x] Migration creates messages table
- [x] Migration creates all indexes
- [x] Migration creates foreign key constraints
- [x] Migration applied to Neon database
- [x] Downgrade function implemented for rollback

## Data Integrity

- [x] Foreign key from messages.conversation_id to conversations.id
- [x] Foreign key from messages.user_id to users.id
- [x] Foreign key from conversations.user_id to users.id
- [x] CASCADE DELETE from users → conversations
- [x] CASCADE DELETE from conversations → messages
- [x] No orphaned messages possible
- [x] No orphaned conversations possible

## Testing Verification

- [x] Can create conversation for valid user
- [x] Cannot create conversation for non-existent user
- [x] Can create message for valid conversation
- [x] Cannot create message for non-existent conversation
- [x] Deleting conversation deletes all messages
- [x] Deleting user deletes conversations and messages
- [x] User A cannot query User B's conversations
- [x] Queries return results in correct order

## Performance

- [x] Conversation list query < 200ms
- [x] Message history query < 500ms (100 messages)
- [x] Message insert < 100ms
- [x] Indexes improve query performance

## Documentation

- [x] spec.md created
- [x] data-model.md created
- [x] plan.md created
- [x] research.md created
- [x] tasks.md created
- [x] quickstart.md created
- [x] README.md created
- [x] checklists/requirements.md (this file)

## Success Criteria

- [x] All database tables exist
- [x] All models defined
- [x] All indexes created
- [x] All foreign keys enforced
- [x] Migration applied successfully
- [x] No data integrity issues
- [x] User isolation verified
- [x] Performance benchmarks met
