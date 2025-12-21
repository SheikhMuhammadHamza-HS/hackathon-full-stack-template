"""SQLModel database models for authentication system."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
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

    Demonstrates user data isolation pattern for Phase II.
    All queries MUST filter by authenticated user_id.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
