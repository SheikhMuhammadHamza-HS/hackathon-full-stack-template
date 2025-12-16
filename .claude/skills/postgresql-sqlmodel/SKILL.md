---
name: postgresql-sqlmodel
description: PostgreSQL database and SQLModel ORM skill for Python applications. Use when working with databases, SQL queries, SQLModel models, relationships, CRUD operations, migrations, or Neon PostgreSQL. Triggers on keywords like database, SQL, model, table, query, postgres, SQLModel, relationship, migration.
---

# PostgreSQL & SQLModel Skill

## Overview

This skill covers PostgreSQL database operations and SQLModel ORM for Python applications. SQLModel combines SQLAlchemy and Pydantic, providing seamless integration with FastAPI.

## SQLModel Basics

### Installation

```bash
pip install sqlmodel
# For async support
pip install sqlmodel asyncpg
```

### Model Definition

```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

# Base model (shared fields - NOT a table)
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(index=True)
    is_active: bool = Field(default=True)

# Table model (database table)
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")

# Create request model (API input)
class UserCreate(UserBase):
    password: str

# Public response model (API output - no password)
class UserPublic(UserBase):
    id: int
    created_at: datetime

# Update model (all fields optional)
class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
```

### Field Options

```python
from sqlmodel import Field

class Example(SQLModel, table=True):
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Indexed field (faster queries)
    email: str = Field(index=True)

    # Unique constraint
    username: str = Field(unique=True)

    # Default value
    is_active: bool = Field(default=True)

    # Nullable field
    bio: Optional[str] = Field(default=None)

    # Max length (validation)
    name: str = Field(max_length=100)

    # Foreign key
    user_id: int = Field(foreign_key="user.id")

    # Custom column name
    full_name: str = Field(sa_column_kwargs={"name": "full_name_column"})
```

## Database Connection

### Sync Engine (SQLite/PostgreSQL)

```python
from sqlmodel import create_engine, Session, SQLModel

# SQLite
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# PostgreSQL
postgres_url = "postgresql://user:password@localhost:5432/dbname"
engine = create_engine(postgres_url, echo=True)  # echo=True for SQL logging

# Neon PostgreSQL
neon_url = "postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(neon_url)

# Create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Session dependency for FastAPI
def get_session():
    with Session(engine) as session:
        yield session
```

### Async Engine (Recommended for Production)

```python
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Async PostgreSQL URL (note: postgresql+asyncpg)
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"

# Neon Async
DATABASE_URL = "postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/neondb?ssl=require"

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,
    max_overflow=10
)

# Async session maker
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create tables
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Async session dependency
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

## CRUD Operations

### Create (INSERT)

```python
# Sync
def create_user(session: Session, user: UserCreate) -> User:
    # Hash password (example)
    hashed_password = hash_password(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Get generated ID
    return db_user

# Async
async def create_user_async(session: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

# Bulk insert
def create_many_users(session: Session, users: list[UserCreate]) -> list[User]:
    db_users = [User(**user.model_dump()) for user in users]
    session.add_all(db_users)
    session.commit()
    return db_users
```

### Read (SELECT)

```python
from sqlmodel import select

# Get by ID
def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)

# Async get by ID
async def get_user_async(session: AsyncSession, user_id: int) -> Optional[User]:
    return await session.get(User, user_id)

# Get by field
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

# Get all with pagination
def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()

# Async get all
async def get_users_async(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()

# Filter with multiple conditions
def search_users(session: Session, query: str, is_active: bool = True) -> list[User]:
    statement = select(User).where(
        User.is_active == is_active,
        User.username.contains(query)  # LIKE %query%
    )
    return session.exec(statement).all()

# Order by
def get_users_ordered(session: Session) -> list[User]:
    statement = select(User).order_by(User.created_at.desc())
    return session.exec(statement).all()
```

### Update

```python
def update_user(session: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = session.get(User, user_id)
    if not db_user:
        return None

    # Only update provided fields
    user_data = user_update.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Async update
async def update_user_async(session: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = await session.get(User, user_id)
    if not db_user:
        return None

    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
```

### Delete

```python
def delete_user(session: Session, user_id: int) -> bool:
    db_user = session.get(User, user_id)
    if not db_user:
        return False

    session.delete(db_user)
    session.commit()
    return True

# Async delete
async def delete_user_async(session: AsyncSession, user_id: int) -> bool:
    db_user = await session.get(User, user_id)
    if not db_user:
        return False

    await session.delete(db_user)
    await session.commit()
    return True

# Soft delete (recommended)
def soft_delete_user(session: Session, user_id: int) -> bool:
    db_user = session.get(User, user_id)
    if not db_user:
        return False

    db_user.is_active = False
    db_user.deleted_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    return True
```

## Relationships

### One-to-Many

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

# Parent (One side)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # One user has many tasks
    tasks: list["Task"] = Relationship(back_populates="user")

# Child (Many side)
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id")

    # Many tasks belong to one user
    user: Optional[User] = Relationship(back_populates="tasks")

# Usage
def create_task_for_user(session: Session, user_id: int, title: str) -> Task:
    task = Task(title=title, user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_user_with_tasks(session: Session, user_id: int) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    # Access tasks: user.tasks
    return user
```

### Many-to-Many

```python
# Link table (association table)
class TaskTagLink(SQLModel, table=True):
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    tags: list["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTagLink
    )

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    tasks: list[Task] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )

# Usage
def add_tag_to_task(session: Session, task_id: int, tag_id: int):
    task = session.get(Task, task_id)
    tag = session.get(Tag, tag_id)
    if task and tag:
        task.tags.append(tag)
        session.add(task)
        session.commit()
```

### Cascade Delete

```python
from sqlalchemy import Column
from sqlalchemy.orm import relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Cascade delete - when user deleted, delete all tasks
    tasks: list["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

## PostgreSQL Specific Features

### SQL Commands Reference

```sql
-- SELECT with conditions
SELECT * FROM users WHERE is_active = true ORDER BY created_at DESC LIMIT 10;

-- JOIN
SELECT u.name, t.title
FROM users u
JOIN tasks t ON u.id = t.user_id
WHERE u.is_active = true;

-- Aggregate functions
SELECT user_id, COUNT(*) as task_count
FROM tasks
GROUP BY user_id
HAVING COUNT(*) > 5;

-- Subquery
SELECT * FROM users
WHERE id IN (SELECT user_id FROM tasks WHERE completed = true);

-- UPSERT (INSERT ON CONFLICT)
INSERT INTO users (email, username)
VALUES ('test@example.com', 'testuser')
ON CONFLICT (email) DO UPDATE SET username = EXCLUDED.username;

-- Transactions
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Index creation
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);

-- Full text search
SELECT * FROM tasks
WHERE to_tsvector('english', title || ' ' || description) @@ to_tsquery('english', 'search_term');
```

### Raw SQL in SQLModel

```python
from sqlmodel import text

# Execute raw SQL
def execute_raw_sql(session: Session):
    statement = text("SELECT * FROM users WHERE is_active = :is_active")
    result = session.exec(statement, {"is_active": True})
    return result.all()

# Complex query
def complex_query(session: Session, user_id: int):
    statement = text("""
        SELECT t.*, u.name as user_name
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        WHERE t.user_id = :user_id
        ORDER BY t.created_at DESC
    """)
    result = session.exec(statement, {"user_id": user_id})
    return result.mappings().all()
```

### PostgreSQL Data Types

```python
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON, ARRAY, String
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional
import uuid

class AdvancedModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # UUID
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # JSON/JSONB
    metadata: dict = Field(default={}, sa_column=Column(JSON))

    # Array
    tags: list[str] = Field(default=[], sa_column=Column(ARRAY(String)))

    # Decimal (for money)
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    # Date/Time types
    created_at: datetime = Field(default_factory=datetime.utcnow)
    birth_date: Optional[date] = None
    start_time: Optional[time] = None

    # Enum (store as string)
    status: str = Field(default="pending")  # Use Literal or Enum
```

## Alembic Migrations

### Setup

```bash
pip install alembic
alembic init alembic
```

### Configure `alembic/env.py`

```python
from sqlmodel import SQLModel
from app.models import *  # Import all models

target_metadata = SQLModel.metadata
```

### Migration Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show history
alembic history
```

### Manual Migration Example

```python
# alembic/versions/xxxx_add_users_table.py
from alembic import op
import sqlalchemy as sa
import sqlmodel

def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_user_email', 'user', ['email'])

def downgrade():
    op.drop_index('ix_user_email', 'user')
    op.drop_table('user')
```

## Query Optimization

### Indexing Strategy

```python
class OptimizedModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Index frequently queried fields
    email: str = Field(index=True, unique=True)
    status: str = Field(index=True)

    # Composite index via sa_column_kwargs
    user_id: int = Field(foreign_key="user.id", index=True)

# Create composite index manually
from sqlalchemy import Index
Index('idx_task_user_status', Task.user_id, Task.status)
```

### Eager Loading (Prevent N+1)

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

# Eager load relationships
def get_users_with_tasks(session: Session) -> list[User]:
    statement = select(User).options(selectinload(User.tasks))
    return session.exec(statement).all()

# Join load (single query)
def get_user_with_tasks_joined(session: Session, user_id: int) -> Optional[User]:
    statement = (
        select(User)
        .options(joinedload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Extra connections allowed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True     # Check connection health
)
```

## Best Practices

### 1. Model Organization

```
app/
├── models/
│   ├── __init__.py      # Export all models
│   ├── base.py          # Base model classes
│   ├── user.py          # User models
│   └── task.py          # Task models
├── crud/
│   ├── __init__.py
│   ├── user.py          # User CRUD operations
│   └── task.py          # Task CRUD operations
└── db/
    ├── __init__.py
    └── session.py       # Database session setup
```

### 2. Separate Models Pattern

```python
# models/user.py

# Database model
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# API models (no table=True)
class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int

class UserUpdate(SQLModel):
    email: Optional[str] = None
```

### 3. Transaction Management

```python
from contextlib import contextmanager

@contextmanager
def transaction(session: Session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

# Usage
with transaction(session) as tx:
    user = create_user(tx, user_data)
    create_profile(tx, user.id, profile_data)
```

### 4. Error Handling

```python
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def create_user_safe(session: Session, user: UserCreate) -> User:
    try:
        db_user = User(**user.model_dump())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
```

## Neon PostgreSQL Specific

### Connection String

```python
# Pooled connection (recommended)
DATABASE_URL = "postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require"

# Direct connection (for migrations)
DIRECT_URL = "postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
```

### Serverless Considerations

```python
# Short connection timeout for serverless
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,      # Recycle every 5 min (Neon idle timeout)
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30s query timeout
    }
)
```

## Quick Reference

| Operation | Sync | Async |
|-----------|------|-------|
| Get by ID | `session.get(Model, id)` | `await session.get(Model, id)` |
| Query | `session.exec(select(...))` | `await session.exec(select(...))` |
| Add | `session.add(obj)` | `session.add(obj)` |
| Commit | `session.commit()` | `await session.commit()` |
| Refresh | `session.refresh(obj)` | `await session.refresh(obj)` |
| Delete | `session.delete(obj)` | `await session.delete(obj)` |

## Resources

- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Neon Docs](https://neon.tech/docs)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
