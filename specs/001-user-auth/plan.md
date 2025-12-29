# Implementation Plan: Multi-User Authentication System

**Branch**: `001-user-auth` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-user-auth/spec.md`

## Summary

Implement a complete authentication system for Phase II full-stack web application with multi-user support, JWT-based stateless authentication, and strict user data isolation. The system enables user signup, signin, signout, persistent sessions, and enforces that users can only access their own data. This feature is the foundation for all Phase II functionality—without authentication, the multi-user architecture cannot function.

**Technical Approach**: Use Better Auth library for frontend authentication with JWT plugin, implement JWT validation middleware in FastAPI backend, store user credentials in Neon PostgreSQL with Better Auth managing the users table, and enforce user_id matching between JWT tokens and URL paths to prevent cross-user data access.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**:
- Frontend: Next.js 16+, React 19, Better Auth (with JWT plugin), Tailwind CSS
- Backend: FastAPI, SQLModel, Alembic, PyJWT (or python-jose), Pydantic
- Database: Neon Serverless PostgreSQL

**Storage**: Neon PostgreSQL (serverless, cloud-hosted)
**Testing**: Manual testing via Postman/Thunder Client (API endpoints), browser DevTools (responsive UI), multi-user scenarios (2+ accounts)
**Target Platform**: Web (Linux server for backend, browser for frontend)
**Project Type**: Web application (monorepo with frontend/ and backend/ directories)
**Performance Goals**: Signup <2s, Signin <2s, JWT verification <50ms, API response <200ms (excluding network)
**Constraints**:
- 7-day JWT token expiry (configurable)
- 1000+ concurrent users supported
- HTTPS required in production
- httpOnly cookies preferred for token storage (XSS protection)

**Scale/Scope**: Phase II multi-user web application serving 100-1000 users initially, horizontally scalable via JWT stateless design

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Production-Ready Web Architecture ✅
- **Status**: PASS
- **Evidence**: Monorepo structure with frontend/ and backend/ directories. Frontend communicates with backend via REST API only. Backend is stateless (JWT tokens, no server sessions). Neon PostgreSQL for persistent storage. Each layer independently deployable.

### Principle II: Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Complete spec.md exists with 5 user stories, 20 functional requirements, 12 success criteria. This plan.md follows spec completion. tasks.md will be generated next. All API contracts documented in spec before implementation.

### Principle III: Test-First Development ✅
- **Status**: PASS
- **Evidence**: Spec includes 21 acceptance scenarios defining expected behavior before implementation. Each task will include API testing (Postman), multi-user testing (2+ accounts), responsive testing (mobile/desktop), and authentication flow testing (signup, signin, token validation).

### Principle IV: Data Model Integrity with User Isolation ✅
- **Status**: PASS
- **Evidence**: User table (id: string UUID, email: unique, password_hash, name, timestamps). Task table with user_id foreign key. All queries filtered by authenticated user_id. SQLModel for type-safe ORM. Alembic for migrations.

### Principle V: Input Validation and Error Handling ✅
- **Status**: PASS
- **Evidence**: Frontend validation (required fields, email format, password length). Backend Pydantic models for request validation. Proper HTTP status codes (401, 403, 400, 500). Security-conscious error messages (generic "Invalid email or password").

### Principle VI: Clean Code and Multi-Language Standards ✅
- **Status**: PASS
- **Evidence**: Backend follows PEP 8, type hints, async/await, Pydantic/SQLModel. Frontend uses TypeScript strict mode, Server Components default, Tailwind utilities only. Functions small and focused.

### Principle VII: Windows via WSL 2 Only ✅
- **Status**: PASS (Informational)
- **Evidence**: Development environment uses WSL 2 for Windows users. Python 3.13+, Node.js 20+, UV package manager installed.

### Principle VIII: User Isolation and Data Security (NON-NEGOTIABLE) ✅
- **Status**: PASS - CRITICAL
- **Evidence**: JWT required on all endpoints except signup/signin. JWT user_id must match URL {user_id}. Database queries filtered by authenticated user_id. 403 returned on user_id mismatch. 401 on missing/invalid token. No cross-user data access possible.

### Principle IX: RESTful API Design ✅
- **Status**: PASS
- **Evidence**: URL structure `/api/auth/signup`, `/api/auth/signin`. HTTP methods: POST (signup, signin). JSON request/response. Consistent error format `{"error": "message"}`. Status codes: 200, 201, 400, 401, 403, 500.

### Principle X: Authentication-First Approach ✅
- **Status**: PASS - CRITICAL
- **Evidence**: This feature implements authentication BEFORE any other Phase II features. User table created first. JWT middleware built before task endpoints. Every future endpoint will require JWT validation.

### Principle XI: Mobile-First Responsive Design ✅
- **Status**: PASS
- **Evidence**: Signup/signin forms designed for mobile (375px) first. Tailwind responsive utilities (sm:, md:, lg:). Touch targets 44x44px minimum. Keyboard navigation supported.

### Principle XII: Cloud-Native Deployment ✅
- **Status**: PASS
- **Evidence**: Environment variables for all secrets (BETTER_AUTH_SECRET, DATABASE_URL). HTTPS in production. No file system dependencies. Stateless backend enables horizontal scaling. Vercel (frontend), Render (backend), Neon (database).

**Overall Gate Status**: ✅ **PASSED** - All 12 constitutional principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-user-auth/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (API endpoint specs)
│   ├── signup.md        # POST /api/auth/signup
│   ├── signin.md        # POST /api/auth/signin
│   └── signout.md       # POST /api/auth/signout
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (monorepo)
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── models.py                  # SQLModel database models (User, Task)
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── auth.py                    # JWT validation middleware
│   ├── database.py                # Database connection and session
│   └── routers/
│       ├── __init__.py
│       ├── auth.py                # Authentication endpoints (signup, signin, signout)
│       └── tasks.py               # Task endpoints (future - require JWT)
├── alembic/
│   ├── versions/                  # Database migration files
│   ├── env.py                     # Alembic configuration
│   └── script.py.mako             # Migration template
├── tests/                         # Backend tests (manual Postman for Phase II)
├── .env                           # Backend environment variables (not committed)
├── alembic.ini                    # Alembic config file
├── pyproject.toml                 # Python dependencies (UV)
└── README.md                      # Backend setup instructions

frontend/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home/landing page
│   ├── auth/
│   │   ├── signin/page.tsx        # Sign in page
│   │   ├── signup/page.tsx        # Sign up page
│   │   └── signout/page.tsx       # Sign out handler (optional)
│   └── dashboard/
│       └── page.tsx               # Protected dashboard (requires auth)
├── components/
│   ├── AuthForm.tsx               # Reusable auth form component
│   ├── ErrorMessage.tsx           # Error display component
│   └── LoadingSpinner.tsx         # Loading state component
├── lib/
│   ├── auth.ts                    # Better Auth configuration
│   ├── api-client.ts              # Centralized API client with JWT header
│   └── types.ts                   # TypeScript types/interfaces
├── middleware.ts                  # Protected route middleware
├── public/                        # Static assets
├── .env.local                     # Frontend environment variables (not committed)
├── next.config.ts                 # Next.js configuration
├── tailwind.config.ts             # Tailwind configuration
├── tsconfig.json                  # TypeScript configuration
└── package.json                   # Frontend dependencies

# Shared configuration
.gitignore                         # Ignore .env files, node_modules, etc.
README.md                          # Project overview and monorepo setup
CLAUDE.md                          # Claude Code instructions (updated for Phase II)
docker-compose.yml                 # Optional local development setup
```

**Structure Decision**: Web application monorepo selected based on Phase II requirements. Frontend and backend are separate services but share same repository for coordinated development. Frontend deployed on Vercel, backend on Render, database on Neon. Clear separation of concerns while maintaining single source of truth for specifications and documentation.

## Complexity Tracking

*No constitution violations requiring justification. All principles satisfied.*

## Phase 0: Research & Technology Decisions

**Objective**: Resolve all technical uncertainties and establish concrete technology choices for authentication implementation.

### Research Questions

1. **Better Auth Configuration**: How to configure Better Auth in Next.js 16+ with JWT plugin?
2. **JWT Verification in FastAPI**: Which library (PyJWT vs python-jose) and how to implement middleware?
3. **Neon PostgreSQL Integration**: How to configure Neon with SQLModel and Alembic?
4. **Token Storage Strategy**: httpOnly cookies vs localStorage—security tradeoffs and implementation?
5. **CORS Configuration**: How to configure FastAPI CORS for production Vercel domain?

### Decisions & Rationale

*(These will be documented in research.md during Phase 0 execution)*

- **Better Auth Setup**: Installation, configuration file structure, JWT plugin activation
- **JWT Library Choice**: PyJWT vs python-jose comparison, recommendation with rationale
- **Database Connection**: Neon connection string format, SQLModel engine setup, async support
- **Token Storage**: httpOnly cookie vs localStorage security analysis, final recommendation
- **CORS Setup**: FastAPI CORSMiddleware configuration, allowed origins for development/production

## Phase 1: Data Model & API Contracts

**Prerequisites**: Phase 0 research complete

### Data Model (data-model.md)

**User Entity** (Managed by Better Auth):
- `id`: TEXT (UUID), primary key
- `email`: TEXT, unique, not null
- `name`: TEXT, not null
- `password_hash`: TEXT, not null (bcrypt, managed by Better Auth)
- `created_at`: TIMESTAMP, default NOW()
- `updated_at`: TIMESTAMP, default NOW()

**Relationships**: One-to-many with Task entity (one user has many tasks)

**Task Entity** (For reference—not part of auth feature, but needed for foreign key):
- `id`: INTEGER, primary key, auto-increment
- `user_id`: TEXT, foreign key → users.id, not null
- `title`: TEXT, 1-200 chars, not null
- `description`: TEXT, max 1000 chars, nullable
- `completed`: BOOLEAN, default false, not null
- `created_at`: TIMESTAMP, default NOW()
- `updated_at`: TIMESTAMP, default NOW()

**Indexes**:
- `users.email` (unique index, Better Auth manages this)
- `tasks.user_id` (for efficient user-scoped queries)
- `tasks.created_at` (for sorting)

**Validation Rules**:
- Email: RFC 5322 format, unique across users
- Password: Minimum 8 characters (Better Auth enforces)
- Name: 1-100 characters, no whitespace-only strings
- User_id: Must exist in users table (foreign key constraint)

### API Contracts (contracts/)

**POST /api/auth/signup** (signup.md):
```
Request:
{
  "name": "string (1-100 chars, required)",
  "email": "string (valid email, unique, required)",
  "password": "string (min 8 chars, required)"
}

Response (201 Created):
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "User Name"
  },
  "token": "jwt-token-string"
}

Error Responses:
- 400: {"error": "Email already registered"} (duplicate email)
- 400: {"error": "Password must be at least 8 characters"} (short password)
- 400: {"error": "Please enter a valid email"} (invalid format)
- 400: {"error": "Name is required"} (missing name)
- 500: {"error": "Service temporarily unavailable, please try again"} (database failure)
```

**POST /api/auth/signin** (signin.md):
```
Request:
{
  "email": "string (required)",
  "password": "string (required)"
}

Response (200 OK):
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "User Name"
  },
  "token": "jwt-token-string"
}

Error Responses:
- 400: {"error": "Invalid email or password"} (wrong credentials)
- 400: {"error": "Email is required"} (missing email)
- 400: {"error": "Password is required"} (missing password)
- 500: {"error": "Service temporarily unavailable, please try again"} (database failure)
```

**POST /api/auth/signout** (signout.md):
```
Request:
{
  "token": "jwt-token-string"
}

Response (200 OK):
{
  "message": "Signed out successfully"
}

Note: Frontend handles token removal from storage. Backend can optionally
invalidate token (for Phase III if token blacklist implemented).

Error Responses:
- 401: {"error": "Authentication required"} (missing token)
```

### JWT Middleware Design

**Function**: `verify_jwt(authorization: str) -> str`

**Logic**:
1. Extract token from "Bearer {token}" format
2. Verify token signature using BETTER_AUTH_SECRET
3. Decode token payload
4. Check expiry (reject if expired)
5. Extract user_id from payload
6. Return user_id if valid
7. Raise HTTPException(401) if invalid/expired/missing

**Usage Pattern** (all protected endpoints):
```python
@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    authenticated_user: str = Depends(verify_jwt)
):
    if user_id != authenticated_user:
        raise HTTPException(403, "Access denied to this resource")

    # Query tasks filtered by authenticated_user
    tasks = await db.query(Task).filter(Task.user_id == authenticated_user).all()
    return tasks
```

### Environment Variables

**Frontend (.env.local)**:
```
BETTER_AUTH_SECRET=your-32-char-random-secret-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env)**:
```
BETTER_AUTH_SECRET=your-32-char-random-secret-here
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.vercel.app
```

**CRITICAL**: Both frontend and backend MUST use identical BETTER_AUTH_SECRET for JWT signature validation.

### Quickstart (quickstart.md)

**Development Setup**:
1. Clone repository and checkout `001-user-auth` branch
2. Install dependencies (frontend: npm install, backend: uv install)
3. Configure environment variables (.env.local for frontend, .env for backend)
4. Generate BETTER_AUTH_SECRET: `openssl rand -base64 32`
5. Create Neon database and get connection string
6. Run database migrations: `alembic upgrade head`
7. Start backend: `uvicorn app.main:app --reload`
8. Start frontend: `npm run dev`
9. Test signup at http://localhost:3000/auth/signup

**Testing Checklist**:
- [ ] Signup with valid credentials (redirects to dashboard)
- [ ] Signup with duplicate email (shows error)
- [ ] Signin with correct credentials (redirects to dashboard)
- [ ] Signin with wrong password (shows error)
- [ ] Access protected route without signin (redirects to signin)
- [ ] Refresh page while signed in (stays signed in)
- [ ] Signout (removes token, redirects to signin)
- [ ] Create 2 users, verify User A cannot access User B's data

## Implementation Sequence

**Phase 0 (Research)**: ✅ Complete research.md with all technology decisions

**Phase 1 (Design)**:
- ✅ Create data-model.md with User and Task entities
- ✅ Create contracts/ directory with signup.md, signin.md, signout.md
- ✅ Create quickstart.md with setup and testing instructions
- ✅ Update agent context (CLAUDE.md) with Phase II authentication patterns

**Phase 2 (Tasks)**: Run `/sp.tasks` to generate detailed implementation tasks

**Phase 3 (Implementation)**: Execute tasks sequentially with test-first approach

**Phase 4 (Validation)**: Multi-user testing, responsive testing, deployment validation

## Next Steps

1. ✅ Complete this plan.md
2. ⏳ Generate research.md (Phase 0)
3. ⏳ Generate data-model.md (Phase 1)
4. ⏳ Generate API contracts (Phase 1)
5. ⏳ Generate quickstart.md (Phase 1)
6. ⏳ Update agent context
7. ⏳ Run `/sp.tasks` to generate implementation tasks
8. ⏳ Begin implementation following tasks.md

**Estimated Timeline**:
- Phase 0 (Research): Immediate (part of /sp.plan)
- Phase 1 (Design): Immediate (part of /sp.plan)
- Phase 2 (Task Generation): Run `/sp.tasks` after plan approval
- Phase 3 (Implementation): 2-3 days (depends on development velocity)
- Phase 4 (Testing & Deployment): 1 day

**Success Criteria Met When**:
- All 21 acceptance scenarios pass
- Multi-user testing confirms zero cross-user data access
- Responsive testing passes on mobile (375px) and desktop (1024px+)
- All 12 success criteria from spec.md satisfied
- Frontend deployed on Vercel, backend on Render, database on Neon

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 0 & Phase 1 execution

**Constitutional Compliance**: ✅ ALL PRINCIPLES SATISFIED

**Next Command**: Continue with Phase 0 and Phase 1 artifact generation
