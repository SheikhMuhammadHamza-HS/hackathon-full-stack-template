---
id: 0003
title: Add Conversation and Message SQLModel classes
stage: green
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-ai-chatbot
branch: 002-ai-chatbot
user: user
command: direct-request
labels: ["database", "sqlmodel", "models", "phase-iii"]
links:
  spec: specs/002-ai-chatbot/data-model.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models.py
tests:
  - null
---

## Prompt

You need to add two new SQLModel classes to the existing backend/app/models.py file for Phase III AI Chatbot feature.

**Context:**
- Feature: 002-ai-chatbot
- Existing models: User and Task (already in models.py)
- Data model spec: specs/002-ai-chatbot/data-model.md

**Task:**
Add these two models to backend/app/models.py:

1. **Conversation** model:
   - id: Optional[int] = Field(default=None, primary_key=True)
   - user_id: str = Field(foreign_key="users.id", index=True)
   - created_at: datetime = Field(default_factory=datetime.utcnow)
   - updated_at: datetime = Field(default_factory=datetime.utcnow)
   - Relationship: messages (back_populates="conversation")

2. **Message** model:
   - id: Optional[int] = Field(default=None, primary_key=True)
   - user_id: str = Field(foreign_key="users.id", index=True)
   - conversation_id: int = Field(foreign_key="conversations.id", index=True)
   - role: str = Field(max_length=20) - must be 'user' or 'assistant'
   - content: str = Field(sa_column=Column(Text))
   - tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text)) - JSON string for tool metadata
   - created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
   - Relationship: conversation (back_populates="messages")

**Requirements:**
- Add proper imports (List, Column, Text from sqlalchemy)
- Add Relationship import from sqlmodel
- Follow existing code style in models.py
- Add docstrings explaining each model
- Tables should be named "conversations" and "messages"

## Response snapshot

Added two new SQLModel classes to `backend/app/models.py` for Phase III AI Chatbot feature:

1. **Conversation model** - Represents chat sessions between user and AI assistant with:
   - Primary key (id), user_id foreign key with index
   - created_at and updated_at timestamps
   - Bidirectional relationship to Message model

2. **Message model** - Represents individual messages with:
   - Primary key (id), user_id and conversation_id foreign keys with indexes
   - role field (user/assistant), content as TEXT type
   - Optional tool_calls JSON field for AI tool execution metadata
   - created_at timestamp with index for chronological ordering
   - Bidirectional relationship back to Conversation

Updated imports to include:
- `Relationship` from sqlmodel
- `Column, Text` from sqlalchemy
- `List` from typing

All models follow existing code style with comprehensive docstrings explaining purpose, relationships, and security requirements (user_id filtering).

## Outcome

- Impact: Added 2 new SQLModel classes (Conversation, Message) enabling Phase III AI chatbot persistence
- Tests: No tests run (model definition only, migration pending)
- Files: 1 file modified (backend/app/models.py)
- Next prompts: Generate Alembic migration for new tables
- Reflection: Models match spec exactly with proper relationships and indexes defined

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (no automated graders)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
