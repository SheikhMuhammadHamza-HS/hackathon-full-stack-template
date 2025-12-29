"""SQLModel database models for authentication system and AI chatbot.

Phase II: User and Task models for authentication and todo management.
Phase III: Conversation and Message models for AI chatbot feature.
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional, List
import uuid


class User(SQLModel, table=True):
    """User model for authentication system.

    This model is used for user data storage and Alembic migrations.
    Passwords are hashed using bcrypt in the authentication endpoints.
    OAuth fields support social authentication (Google, GitHub).
    """
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    email: str = Field(unique=True, index=True, min_length=1, max_length=254)
    name: str = Field(min_length=1, max_length=100)
    password_hash: Optional[str] = Field(default=None, max_length=255)  # Optional for OAuth users

    # OAuth fields
    oauth_provider: Optional[str] = Field(default=None, max_length=50, index=True)  # 'google', 'github', etc.
    oauth_id: Optional[str] = Field(default=None, max_length=255)  # Provider's unique user ID
    profile_picture: Optional[str] = Field(default=None, max_length=500)  # Profile picture URL

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """Task model representing user-owned todo items.

    Phase II: Basic task management with user isolation.
    Phase V: Extended with advanced task management fields (priority, tags, due dates, recurring).
    All queries MUST filter by authenticated user_id.

    Task Numbering:
        - task_number: User-specific sequential number (1, 2, 3... per user)
        - id: Global database ID (used internally)
        - Chatbot and UI should display task_number, not id

    Advanced Features:
        - priority: Task priority level (low, medium, high)
        - tags: JSON array of tags for categorization
        - due_date: Optional deadline with timezone for reminders
        - is_recurring: Boolean flag for repeating tasks
        - recurring_interval: Repeat frequency (daily, weekly, monthly)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    task_number: int = Field(default=1, index=True)  # User-specific task number (starts from 1)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

    # Phase V: Advanced task management fields
    priority: str = Field(default="medium", max_length=10)  # 'low', 'medium', 'high'
    tags: Optional[str] = Field(default="[]", sa_column=Column(Text))  # JSON array as string
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurring_interval: Optional[str] = Field(default=None, max_length=20)  # 'daily', 'weekly', 'monthly'

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session between user and AI assistant.

    Phase III: Supports stateless conversation architecture for AI chatbot.
    Groups related messages together for context and organization.
    All queries MUST filter by authenticated user_id for security.

    Relationships:
        - One user has many conversations (1:N)
        - One conversation has many messages (1:N)
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model representing a single message in a conversation.

    Phase III: Stores individual messages sent by user or AI assistant.
    Messages are append-only (immutable once created) for audit trail.
    All queries MUST filter by authenticated user_id for security.

    Attributes:
        role: Must be 'user' or 'assistant' (enforced by CHECK constraint)
        content: Message text content (stored as TEXT for large messages)
        tool_calls: JSON string containing tool execution metadata (assistant only)

    Relationships:
        - Many messages belong to one conversation (N:1)
        - Messages also reference user_id for efficient user isolation queries
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
