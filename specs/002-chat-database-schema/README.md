# Chat Conversation Persistence

## Overview

Database schema and persistence layer for chat conversations and messages. This feature provides **database tables ONLY** - no API endpoints, no UI, no AI logic.

## What This Feature Provides

### Database Tables
- **conversations**: Stores chat sessions (id, user_id, timestamps)
- **messages**: Stores individual messages (content, role, tool_calls)

### Models
- **Conversation** SQLModel class
- **Message** SQLModel class
- Relationships and cascade deletes

### Migration
- Alembic migration file
- Table creation SQL
- Index creation
- Foreign key constraints

## What This Feature Does NOT Include

❌ Chat API endpoints → See `003-ai-agent`
❌ AI agent logic → See `003-ai-agent`
❌ Chat UI components → See `004-chat-ui`
❌ MCP tools → See `003-ai-agent`

This is **pure database layer** - just tables and models.

## Files in This Specification

| File | Purpose |
|------|---------|
| `spec.md` | Requirements for conversation persistence |
| `data-model.md` | Conversation and Message entity definitions |
| `plan.md` | Architecture decisions and design rationale |
| `research.md` | Technical decisions (cascade deletes, indexes, JSON storage) |
| `tasks.md` | 32 implementation tasks (all completed) |
| `quickstart.md` | Database verification guide |
| `README.md` | This file - overview and navigation |

## Dependencies

**Requires**:
- 001-user-auth (User model must exist)
- Neon PostgreSQL database
- SQLModel + Alembic

**Provides To**:
- 003-ai-agent (saves messages to these tables)
- 004-chat-ui (fetches messages from these tables)

## Status

✅ **IMPLEMENTED** - Tables exist in database, models defined, migration applied

## Quick Verification

```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt" | grep conversations
psql $DATABASE_URL -c "\dt" | grep messages
```

## Navigation

- [View Specification](./spec.md)
- [Data Model Details](./data-model.md)
- [Implementation Tasks](./tasks.md)
- [Architecture Plan](./plan.md)
- [Technical Research](./research.md)
- [Verification Guide](./quickstart.md)
