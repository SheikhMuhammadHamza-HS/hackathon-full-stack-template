---
name: fastapi
description: FastAPI Python web framework skill for building REST APIs. Use when creating API endpoints, routes, request/response handling, validation, authentication, middleware, or backend services. Triggers on keywords like FastAPI, API, endpoint, route, REST, backend, Pydantic, validation, OAuth, JWT.
---

# FastAPI Skill

## Overview

FastAPI is a modern, high-performance Python web framework for building APIs. It is built on Starlette (ASGI) and Pydantic (validation).

**Key Features:**
- Automatic OpenAPI/Swagger documentation
- Type hints based validation
- Async support
- Dependency injection
- OAuth2/JWT security built-in

## Installation

```bash
# Full installation (recommended)
pip install "fastapi[standard]"

# Minimal installation
pip install fastapi uvicorn

# With async database support
pip install fastapi uvicorn sqlmodel asyncpg
```

## Quick Start

### Basic Application

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API description here",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Run Server

```bash
# Development (auto-reload)
fastapi dev main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Path Parameters

```python
from fastapi import FastAPI, Path

app = FastAPI()

# Basic path parameter
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# With validation
@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(
        ...,
        title="Item ID",
        description="The ID of the item to get",
        ge=1,  # greater than or equal
        le=1000  # less than or equal
    )
):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/tasks/{task_id}")
async def get_user_task(user_id: int, task_id: int):
    return {"user_id": user_id, "task_id": task_id}

# String path with validation
@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    return {"file_path": file_path}
```

## Query Parameters

```python
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()

# Basic query parameters
@app.get("/items/")
async def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Optional parameters
@app.get("/users/")
async def get_users(
    q: Optional[str] = None,
    is_active: bool = True
):
    return {"q": q, "is_active": is_active}

# With validation
@app.get("/search/")
async def search(
    q: str = Query(
        ...,  # Required
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9 ]+$",
        title="Search Query",
        description="Search term to filter results"
    ),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100)
):
    return {"q": q, "page": page, "size": size}

# List query parameters
@app.get("/items/filter/")
async def filter_items(
    tags: List[str] = Query(default=[])
):
    # URL: /items/filter/?tags=tag1&tags=tag2
    return {"tags": tags}
```

## Request Body (Pydantic Models)

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

app = FastAPI()

# Request model
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "secretpassword",
                "full_name": "John Doe"
            }
        }

# Response model
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # For ORM compatibility

# Update model (all optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None

# Endpoints
@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # user is automatically validated
    return {"id": 1, **user.model_dump(), "created_at": datetime.utcnow()}

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    # Only update provided fields
    update_data = user.model_dump(exclude_unset=True)
    return {"id": user_id, **update_data}
```

### Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class Tag(BaseModel):
    name: str
    color: Optional[str] = "blue"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tags: List[Tag] = []
    address: Optional[Address] = None

@app.post("/tasks/")
async def create_task(task: TaskCreate):
    return task
```

## Response Models

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float
    secret_code: str  # Won't be returned

class ItemPublic(BaseModel):
    id: int
    name: str
    price: float

# Single response
@app.get("/items/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int):
    return {"id": item_id, "name": "Test", "price": 10.5, "secret_code": "hidden"}

# List response
@app.get("/items/", response_model=List[ItemPublic])
async def get_items():
    return [
        {"id": 1, "name": "Item 1", "price": 10.5, "secret_code": "hidden"},
        {"id": 2, "name": "Item 2", "price": 20.0, "secret_code": "hidden"}
    ]

# Response with exclude
@app.get("/items/{item_id}/full", response_model=Item, response_model_exclude={"secret_code"})
async def get_item_full(item_id: int):
    return {"id": item_id, "name": "Test", "price": 10.5, "secret_code": "hidden"}

# Union response types
from typing import Union

class ErrorResponse(BaseModel):
    error: str
    detail: str

@app.get("/data/{item_id}", response_model=Union[ItemPublic, ErrorResponse])
async def get_data(item_id: int):
    if item_id < 0:
        return {"error": "Invalid ID", "detail": "ID must be positive"}
    return {"id": item_id, "name": "Test", "price": 10.5}
```

## HTTP Methods & Status Codes

```python
from fastapi import FastAPI, status

app = FastAPI()

# GET - Read
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

# POST - Create
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: dict):
    return item

# PUT - Full update
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: dict):
    return {"item_id": item_id, **item}

# PATCH - Partial update
@app.patch("/items/{item_id}")
async def partial_update_item(item_id: int, item: dict):
    return {"item_id": item_id, **item}

# DELETE
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    return None

# Common status codes
# 200 OK - Default for GET, PUT, PATCH
# 201 Created - POST
# 204 No Content - DELETE
# 400 Bad Request - Invalid input
# 401 Unauthorized - Not authenticated
# 403 Forbidden - Not authorized
# 404 Not Found - Resource not found
# 422 Unprocessable Entity - Validation error
# 500 Internal Server Error - Server error
```

## Error Handling

```python
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# Basic HTTPException
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID must be positive"
        )
    if item_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
            headers={"X-Error": "Item not found"}
        )
    return {"item_id": item_id}

# Custom exception class
class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": f"Item {exc.item_id} not found"}
    )

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": str(exc)}
    )
```

## Dependency Injection

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Annotated

app = FastAPI()

# Simple dependency
async def common_parameters(
    skip: int = 0,
    limit: int = 100,
    q: str | None = None
):
    return {"skip": skip, "limit": limit, "q": q}

CommonParams = Annotated[dict, Depends(common_parameters)]

@app.get("/items/")
async def get_items(commons: CommonParams):
    return commons

# Class-based dependency
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/users/")
async def get_users(pagination: Pagination = Depends()):
    return {"skip": pagination.skip, "limit": pagination.limit}

# Dependency with sub-dependency
async def verify_token(x_token: str = Header(...)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token

async def get_current_user(token: str = Depends(verify_token)):
    return {"user": "johndoe", "token": token}

@app.get("/me/")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Database session dependency
from sqlmodel import Session
from app.db import engine

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/items/{item_id}")
async def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Authentication & Security

### OAuth2 with Password (JWT)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Annotated

# Configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user dependency
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Login endpoint
@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
```

### API Key Authentication

```python
from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-api-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/secure/", dependencies=[Security(verify_api_key)])
async def secure_endpoint():
    return {"message": "You have access!"}
```

## Middleware

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response
```

## Routers (Modular Structure)

### Project Structure

```
app/
├── main.py
├── routers/
│   ├── __init__.py
│   ├── users.py
│   └── tasks.py
├── models/
│   ├── __init__.py
│   └── user.py
└── dependencies.py
```

### Router Definition

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[UserResponse])
async def get_users():
    return []

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {"id": user_id, "name": "Test"}

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    return None
```

### Include Routers in Main

```python
# app/main.py
from fastapi import FastAPI
from app.routers import users, tasks

app = FastAPI(title="My API")

# Include routers
app.include_router(users.router)
app.include_router(tasks.router)

# With prefix
app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["v1"]
)
```

## Background Tasks

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(email: str, message: str):
    # Simulate sending email
    import time
    time.sleep(5)
    print(f"Email sent to {email}: {message}")

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification will be sent in the background"}

# Multiple background tasks
@app.post("/process/")
async def process_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(task1)
    background_tasks.add_task(task2, arg1="value")
    return {"message": "Processing started"}
```

## File Upload

```python
from fastapi import FastAPI, File, UploadFile
from typing import List

app = FastAPI()

# Single file upload
@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# Multiple files
@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}

# With form data
from fastapi import Form

@app.post("/upload-with-data/")
async def upload_with_data(
    file: UploadFile,
    description: str = Form(...)
):
    return {"filename": file.filename, "description": description}

# Save file
import aiofiles

@app.post("/save-file/")
async def save_file(file: UploadFile):
    async with aiofiles.open(f"uploads/{file.filename}", "wb") as f:
        content = await file.read()
        await f.write(content)
    return {"filename": file.filename, "saved": True}
```

## WebSockets

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

## Testing

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "username": "testuser", "password": "secret123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404

# Async tests
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

# Override dependencies for testing
from app.dependencies import get_db

def override_get_db():
    return TestingSessionLocal()

app.dependency_overrides[get_db] = override_get_db
```

## Complete CRUD Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated, List

app = FastAPI()

# Dependencies
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# CREATE
@app.post("/tasks/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# READ ALL
@app.get("/tasks/", response_model=List[TaskPublic])
async def get_tasks(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None
):
    statement = select(Task).offset(skip).limit(limit)
    if completed is not None:
        statement = statement.where(Task.completed == completed)
    return session.exec(statement).all()

# READ ONE
@app.get("/tasks/{task_id}", response_model=TaskPublic)
async def get_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# UPDATE
@app.patch("/tasks/{task_id}", response_model=TaskPublic)
async def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# DELETE
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None
```

## Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## Best Practices

### 1. Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app instance
├── config.py            # Settings/configuration
├── dependencies.py      # Shared dependencies
├── routers/
│   ├── __init__.py
│   ├── users.py
│   └── tasks.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── task.py
├── schemas/             # Pydantic schemas (if separate from models)
├── crud/                # Database operations
├── services/            # Business logic
└── utils/               # Helper functions
```

### 2. Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    debug: bool = False
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Async Best Practices

```python
# Use async for I/O operations
@app.get("/items/")
async def get_items(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Item))
    return result.all()

# Use sync for CPU-bound operations
@app.get("/compute/")
def compute_heavy():
    return heavy_computation()
```

## Quick Reference

| Decorator | HTTP Method | Common Use |
|-----------|-------------|------------|
| `@app.get()` | GET | Read data |
| `@app.post()` | POST | Create data |
| `@app.put()` | PUT | Full update |
| `@app.patch()` | PATCH | Partial update |
| `@app.delete()` | DELETE | Delete data |

| Status Code | Meaning | When to Use |
|-------------|---------|-------------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Not authorized |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable | Validation error |

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Starlette Docs](https://www.starlette.io/)
