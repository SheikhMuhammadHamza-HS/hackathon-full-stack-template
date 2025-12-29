"""Pydantic schemas for request validation and response serialization."""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Trim whitespace and reject empty names."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Name cannot be empty or whitespace-only')
        return trimmed

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Convert email to lowercase for case-insensitive matching."""
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password has uppercase, lowercase, and number."""
        if not v:
            raise ValueError('Password cannot be empty')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain uppercase, lowercase, and number')

        return v


class SigninRequest(BaseModel):
    """Request schema for user signin."""
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=1)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Convert email to lowercase for case-insensitive matching."""
        return v.lower()


class UserResponse(BaseModel):
    """Response schema for user data (without sensitive fields)."""
    id: str
    email: str
    name: str
    oauth_provider: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication endpoints (signup, signin)."""
    user: UserResponse
    token: str


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    details: Optional[str] = None


# Task Enums
class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurringInterval(str, Enum):
    """Recurring task intervals."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Task Schemas
class TaskCreate(BaseModel):
    """Request schema for creating a new task.

    Implements: T002 - Advanced task fields validation
    Fields:
        - title: Required, 1-200 chars
        - description: Optional, max 1000 chars
        - priority: Optional, defaults to 'medium' (low, medium, high)
        - tags: Optional, list of strings, max 10 items
        - due_date: Optional, datetime with timezone
        - is_recurring: Optional, defaults to False
        - recurring_interval: Required if is_recurring=True (daily, weekly, monthly)
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    is_recurring: bool = Field(default=False)
    recurring_interval: Optional[RecurringInterval] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Trim whitespace and reject empty titles."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Title cannot be empty or whitespace-only')
        return trimmed

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags: max 10 items, strip whitespace, remove empty tags."""
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        # Strip whitespace and filter out empty tags
        cleaned_tags = [tag.strip() for tag in v if tag.strip()]
        return cleaned_tags

    @model_validator(mode='after')
    def validate_recurring_interval(self):
        """Validate recurring_interval is required if is_recurring=True."""
        if self.is_recurring and self.recurring_interval is None:
            raise ValueError('recurring_interval is required when is_recurring is True')
        if not self.is_recurring and self.recurring_interval is not None:
            raise ValueError('recurring_interval must be None when is_recurring is False')
        return self


class TaskUpdate(BaseModel):
    """Request schema for updating an existing task.

    Implements: T002 - Advanced task fields validation
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurring_interval: Optional[RecurringInterval] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace and reject empty titles if provided."""
        if v is None:
            return v
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Title cannot be empty or whitespace-only')
        return trimmed

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags: max 10 items, strip whitespace, remove empty tags."""
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        # Strip whitespace and filter out empty tags
        cleaned_tags = [tag.strip() for tag in v if tag.strip()]
        return cleaned_tags

    @model_validator(mode='after')
    def validate_recurring_interval(self):
        """Validate recurring_interval is required if is_recurring=True."""
        # Only validate if both fields are being updated
        if self.is_recurring is not None:
            if self.is_recurring and self.recurring_interval is None:
                raise ValueError('recurring_interval is required when is_recurring is True')
            if not self.is_recurring and self.recurring_interval is not None:
                raise ValueError('recurring_interval must be None when is_recurring is False')
        return self


class TaskResponse(BaseModel):
    """Response schema for task data.

    Implements: T002 - Advanced task fields in response

    Note: task_number is the user-specific ID (1, 2, 3...) shown to users.
          id is the global database ID used internally.
    """
    id: int
    task_number: int  # User-specific task number (starts from 1 per user)
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    is_recurring: bool
    recurring_interval: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas (Phase III)


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Trim whitespace and reject empty messages."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Message cannot be empty or whitespace-only')
        return trimmed


class ToolCallInfo(BaseModel):
    """Information about a tool call made by the agent."""
    tool: str
    parameters: dict
    result: dict


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    reply: str
    conversation_id: int
    tool_calls: List[ToolCallInfo] = []
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response schema for conversation data."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageHistoryResponse(BaseModel):
    """Response schema for message history."""
    id: int
    role: str
    content: str
    tool_calls: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dapr State Store Schemas (Phase V - 008-dapr-state-chatbot)


class ToolCallStateInfo(BaseModel):
    """Tool call information stored in conversation state."""
    tool: str
    parameters: dict
    result: dict


class MessageEntry(BaseModel):
    """Single message entry in conversation state."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    tool_calls: Optional[List[ToolCallStateInfo]] = None


class ConversationState(BaseModel):
    """Full conversation state stored in Dapr State Store.

    Key pattern: chat:{user_id}:{conversation_id}
    """
    conversation_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageEntry] = []

    class Config:
        from_attributes = True


class DegradedModeWarning(BaseModel):
    """Warning response when operating in degraded mode."""
    warning: str = "Chat history unavailable - operating in degraded mode"
    reason: str = "Dapr State Store is unreachable"
