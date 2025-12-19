"""Pydantic schemas for request validation and response serialization."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


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


# Task Schemas
class TaskCreate(BaseModel):
    """Request schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Trim whitespace and reject empty titles."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError('Title cannot be empty or whitespace-only')
        return trimmed


class TaskUpdate(BaseModel):
    """Request schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None

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


class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
