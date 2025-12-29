# Research: Authentication Technology Decisions

**Feature**: Multi-User Authentication System
**Branch**: `001-user-auth`
**Date**: 2025-12-17
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing JWT-based authentication with Better Auth (frontend) and FastAPI (backend). All research questions from plan.md Phase 0 are resolved here.

## Research Question 1: Better Auth Configuration

**Question**: How to configure Better Auth in Next.js 16+ with JWT plugin?

**Decision**: Use Better Auth v1+ with JWT plugin enabled

**Rationale**:
- Better Auth is a modern, production-ready authentication library designed for Next.js
- JWT plugin provides stateless authentication perfect for horizontal scaling
- Integrates seamlessly with Next.js App Router and Server Components
- Handles password hashing (bcrypt), token generation, and user management automatically
- Active development and security updates

**Implementation Approach**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { jwtPlugin } from "better-auth/plugins"

export const auth = betterAuth({
  database: {
    // Better Auth manages users table
    provider: "postgres",
    url: process.env.DATABASE_URL,
  },
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwtPlugin({
      expiresIn: "7d", // 7-day token expiry
      algorithm: "HS256",
    }),
  ],
})
```

**Alternatives Considered**:
- **NextAuth.js**: Popular but more complex, sessions-based by default, heavier
- **Clerk**: Third-party service, vendor lock-in, costs money at scale
- **Custom implementation**: Reinventing the wheel, security risks, maintenance burden

**References**:
- Better Auth docs: https://www.better-auth.com/docs
- JWT plugin: https://www.better-auth.com/docs/plugins/jwt

---

## Research Question 2: JWT Verification in FastAPI

**Question**: Which library (PyJWT vs python-jose) and how to implement middleware?

**Decision**: Use **PyJWT** for JWT verification in FastAPI backend

**Rationale**:
- PyJWT is the most popular Python JWT library (used by major projects)
- Simple API: `jwt.decode(token, secret, algorithms=["HS256"])`
- Active maintenance, frequent security updates
- Smaller dependency footprint than python-jose
- Better error messages for debugging token issues

**Implementation Approach**:
```python
# app/auth.py
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token and extract user_id.

    Returns:
        user_id (str): Authenticated user's ID

    Raises:
        HTTPException 401: If token invalid, expired, or missing
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id") or payload.get("sub")

        if not user_id:
            raise HTTPException(401, "Invalid token: missing user_id")

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired, please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid or malformed token")
    except Exception as e:
        # Log error server-side, return generic message
        print(f"JWT verification error: {e}")
        raise HTTPException(401, "Authentication failed")
```

**Usage in Protected Endpoints**:
```python
@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    authenticated_user: str = Depends(verify_jwt)
):
    if user_id != authenticated_user:
        raise HTTPException(403, "Access denied to this resource")

    # Proceed with database query scoped to authenticated_user
    ...
```

**Alternatives Considered**:
- **python-jose**: More features (JWE support) but heavier, not needed for our use case
- **authlib**: Comprehensive OAuth/JWT library, overkill for simple JWT verification
- **Manual implementation**: Security risk, no reason to reinvent

**Dependencies**:
```toml
# pyproject.toml
[dependencies]
pyjwt = "^2.8.0"
```

**References**:
- PyJWT docs: https://pyjwt.readthedocs.io/
- FastAPI security: https://fastapi.tiangolo.com/tutorial/security/

---

## Research Question 3: Neon PostgreSQL Integration

**Question**: How to configure Neon with SQLModel and Alembic?

**Decision**: Use Neon connection string with SQLModel async engine and Alembic for migrations

**Rationale**:
- Neon provides serverless PostgreSQL with instant branching and scaling
- SQLModel combines Pydantic validation with SQLAlchemy ORM (type-safe)
- Alembic handles schema migrations (standard for SQLAlchemy/SQLModel)
- Async support for FastAPI's async/await pattern

**Implementation Approach**:

**1. Neon Connection String Format**:
```
postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**2. Database Configuration** (`app/database.py`):
```python
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Convert postgres:// to postgresql:// (Neon uses postgres://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Async engine for FastAPI async endpoints
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging during development
    future=True
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    """Dependency for FastAPI endpoints"""
    async with async_session() as session:
        yield session
```

**3. Alembic Configuration** (`alembic.ini`):
```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname  # Overridden by env.py
```

**4. Alembic Env** (`alembic/env.py`):
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app.models import *  # Import all SQLModel models

config = context.config

# Override URL with environment variable
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = SQLModel.metadata

# ... (rest of Alembic env.py standard configuration)
```

**5. Creating Migrations**:
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add users and tasks tables"

# Apply migrations
alembic upgrade head
```

**Alternatives Considered**:
- **Direct SQLAlchemy**: SQLModel provides Pydantic validation on top, better for FastAPI
- **Prisma ORM**: Node.js native, not ideal for Python backend
- **Tortoise ORM**: Less mature than SQLAlchemy ecosystem

**References**:
- Neon docs: https://neon.tech/docs/connect/connect-from-any-app
- SQLModel docs: https://sqlmodel.tiangolo.com/
- Alembic docs: https://alembic.sqlalchemy.org/

---

## Research Question 4: Token Storage Strategy

**Question**: httpOnly cookies vs localStorage—security tradeoffs and implementation?

**Decision**: Use **httpOnly cookies** for production, localStorage acceptable for Phase II development

**Rationale**:

**httpOnly Cookies (Recommended for Production)**:
- ✅ **XSS Protection**: JavaScript cannot access token (prevents XSS token theft)
- ✅ **Automatic inclusion**: Browser sends cookie with every request to domain
- ✅ **Secure flag**: Can enforce HTTPS-only transmission
- ✅ **SameSite attribute**: CSRF protection
- ❌ **CORS complexity**: Requires `credentials: 'include'` in fetch requests
- ❌ **Setup overhead**: Backend must set cookie headers, frontend must configure CORS

**localStorage (Acceptable for Phase II)**:
- ✅ **Simple implementation**: `localStorage.setItem('token', jwt)`
- ✅ **No CORS issues**: Just include in Authorization header
- ✅ **Explicit control**: Clear when needed, easy to debug
- ❌ **XSS vulnerability**: Malicious scripts can steal token
- ❌ **Manual inclusion**: Must manually add to every request

**Decision for Phase II**: Use **localStorage** for development speed, document httpOnly cookie migration for Phase III production hardening.

**Implementation (localStorage)**:
```typescript
// Frontend: lib/api-client.ts
const token = localStorage.getItem('auth_token')

fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
})
```

**Migration Path to httpOnly (Phase III)**:
```typescript
// Backend sets cookie on signin/signup:
response.set_cookie(
    key="auth_token",
    value=jwt_token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="lax",
    max_age=60*60*24*7  # 7 days
)

// Frontend automatically includes cookie (no code change needed)
fetch('/api/endpoint', {
  credentials: 'include',  // Include cookies in CORS requests
})
```

**Alternatives Considered**:
- **SessionStorage**: Cleared on browser close, inconvenient for persistent login
- **IndexedDB**: Overkill for simple token storage, same XSS risks as localStorage

**Security Note**: For Phase II, localStorage is acceptable given our threat model (learning/development). Production apps should migrate to httpOnly cookies to prevent XSS-based token theft.

**References**:
- OWASP JWT Storage: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- MDN httpOnly cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

---

## Research Question 5: CORS Configuration

**Question**: How to configure FastAPI CORS for production Vercel domain?

**Decision**: Use FastAPI `CORSMiddleware` with explicit allowed origins from environment variable

**Rationale**:
- FastAPI provides built-in CORS middleware
- Environment variables enable different configs for development vs production
- Explicit origin whitelist prevents unauthorized domains from making requests
- Required for frontend (Vercel) to call backend API (Render)

**Implementation Approach**:
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # List of allowed origins
    allow_credentials=True,  # Required for cookies (if using httpOnly)
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],  # JWT in Authorization header
    max_age=600,  # Cache preflight response for 10 minutes
)
```

**Environment Variable Configuration**:
```bash
# Development (.env)
ALLOWED_ORIGINS=http://localhost:3000

# Production (.env on Render)
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-preview.vercel.app
```

**CORS Preflight Handling**:
- Browser sends OPTIONS request before actual request (preflight)
- FastAPI middleware automatically handles OPTIONS responses
- `max_age` reduces preflight requests for better performance

**Security Notes**:
- **Never use** `allow_origins=["*"]` in production (allows any domain)
- **Never hardcode** production domains in code (use environment variables)
- **Verify origin** matches expected Vercel deployment domain

**Alternatives Considered**:
- **Manual CORS headers**: Error-prone, FastAPI middleware is standard
- **Reverse proxy CORS**: Adds complexity, middleware sufficient for our needs
- **Custom middleware**: Reinventing the wheel, no benefits

**Testing**:
```bash
# Test CORS preflight
curl -X OPTIONS http://localhost:8000/api/auth/signup \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Expected: Headers include Access-Control-Allow-Origin: http://localhost:3000
```

**References**:
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

## Summary of Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend Auth | Better Auth v1+ with JWT plugin | Modern, Next.js-native, handles user management |
| Backend JWT | PyJWT | Simple, popular, actively maintained |
| Database | Neon PostgreSQL | Serverless, instant branching, scales automatically |
| ORM | SQLModel + Alembic | Type-safe, Pydantic integration, migration support |
| Token Storage | localStorage (Phase II), httpOnly cookies (Phase III) | Development speed vs production security |
| CORS | FastAPI CORSMiddleware | Built-in, standard solution |

## Implementation Readiness

✅ **All research questions resolved**
✅ **Technology stack finalized**
✅ **Implementation patterns documented**
✅ **Security considerations identified**
✅ **Migration paths defined (localStorage → httpOnly)**

**Next Steps**: Proceed to Phase 1 (Data Model & API Contracts)
