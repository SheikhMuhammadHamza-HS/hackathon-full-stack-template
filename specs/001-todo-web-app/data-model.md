# Data Model: Todo Web Application

**Feature**: 001-todo-web-app
**Created**: 2025-12-22

## Entity: Task

Represents a todo item that belongs to a user.

### Attributes

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique task identifier |
| `user_id` | String (UUID) | Foreign Key → users.id, NOT NULL, Indexed | Owner of the task |
| `title` | String (VARCHAR 200) | NOT NULL, Length: 1-200 | Task title |
| `description` | Text | NULL, Max: 1000 chars | Optional task details |
| `completed` | Boolean | NOT NULL, Default: false | Completion status |
| `created_at` | DateTime | NOT NULL, Auto-generated | Creation timestamp |
| `updated_at` | DateTime | NOT NULL, Auto-updated | Last modification timestamp |

### Relationships

- **Belongs to User**: `Task.user_id` → `User.id` (many-to-one)
  - Foreign key constraint with CASCADE on user deletion
  - Each task owned by exactly one user

### Indexes

```sql
-- Primary key index (automatic)
PRIMARY KEY (id)

-- Foreign key index for user_id (for efficient filtering)
INDEX idx_tasks_user_id ON tasks(user_id)

-- Composite index for common query pattern
INDEX idx_tasks_user_completed ON tasks(user_id, completed)
```

### Constraints

- `user_id` must reference existing user in users table
- `title` cannot be empty string (trimmed)
- `description` max length 1000 characters
- `completed` defaults to false on creation

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")
```

## Database Schema

### PostgreSQL Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

## Data Validation Rules

### Title Validation
- Required field
- Minimum length: 1 character (after trimming)
- Maximum length: 200 characters
- Whitespace trimmed before storage

### Description Validation
- Optional field
- Maximum length: 1000 characters
- Null allowed
- Whitespace trimmed before storage

### User ID Validation
- Must be valid UUID format
- Must exist in users table
- Automatically set from JWT token (not user input)

### Completion Status
- Boolean only (true/false)
- Defaults to false on creation
- Can be toggled unlimited times

## Security Considerations

### User Isolation
- All queries MUST filter by user_id
- User cannot access tasks belonging to other users
- user_id extracted from JWT token, not request body

### Data Integrity
- Foreign key ensures task always belongs to valid user
- Cascade delete removes tasks when user is deleted
- Timestamps cannot be manually set by user

## Migration Strategy

### Initial Migration
```bash
alembic revision --autogenerate -m "Create tasks table"
alembic upgrade head
```

### Schema Changes
- All schema changes MUST go through Alembic migrations
- No direct database schema modifications
- Migrations must be reversible (implement downgrade)
