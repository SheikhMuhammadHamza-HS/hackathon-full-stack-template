<!--
Sync Impact Report:
- Version Change: 1.0.0 → 2.0.0 (MAJOR)
- Modified Principles:
  * I. "Learning Foundation First" → "Production-Ready Web Architecture"
  * II. "Spec-Driven Development" (UNCHANGED - still non-negotiable)
  * III. "Test-First Development" → Adapted for full-stack testing
  * IV. "Data Model Integrity" → Expanded for relational database with user isolation
  * V. "Input Validation and Error Handling" → Expanded for API layer validation
  * VI. "Clean Code and Python Standards" → Expanded to include TypeScript/Next.js standards
  * VII. "Windows via WSL 2 Only" (UNCHANGED)
- New Principles Added:
  * VIII. User Isolation and Data Security (NEW)
  * IX. RESTful API Design (NEW)
  * X. Authentication-First Approach (NEW)
  * XI. Mobile-First Responsive Design (NEW)
  * XII. Cloud-Native Deployment (NEW)
- Removed Sections: None (Phase I principles preserved for context but marked as superseded)
- Templates Requiring Updates:
  ✅ plan-template.md (Constitution Check must reference new security and API principles)
  ✅ spec-template.md (Requirements must include auth, API contracts, responsive UI)
  ✅ tasks-template.md (Tasks must include API testing, multi-user testing, deployment)
- Follow-up TODOs: None (all placeholders filled for Phase II context)
-->

# Phase II Full-Stack Web Application Constitution

## Phase Transition Context

**Phase I (Console App)**: Established fundamental CRUD operations, clean code practices, and spec-driven development methodology using in-memory storage and console interface.

**Phase II (Full-Stack Web App)**: Transitions to production-ready, multi-user web application with persistent database, authentication, REST API, responsive UI, and cloud deployment. This phase builds on Phase I fundamentals while introducing real-world architectural patterns required for scalable web applications.

**Why This Transition Matters**: Console applications teach fundamentals, but modern software engineering requires understanding distributed systems, user authentication, API design, database persistence, and deployment. Phase II bridges the gap between learning exercises and production software that serves real users at scale.

## Core Principles

### I. Production-Ready Web Architecture

Phase II implements a full-stack web architecture with clear separation of concerns: frontend (Next.js), backend (FastAPI), and database (Neon PostgreSQL). This is NOT a learning exercise—this is production-grade architecture following industry best practices for scalability, security, and maintainability.

**Rationale**: Modern web applications require multi-layer architecture to separate concerns, enable independent scaling, support multiple clients, and maintain security boundaries. This architecture pattern is used by companies from startups to enterprises.

**Rules**:
- MUST use monorepo structure with separate frontend/ and backend/ directories
- Frontend MUST communicate with backend exclusively via REST API (no direct database access)
- Backend MUST be stateless (all state in database or JWT tokens)
- Database MUST be Neon Serverless PostgreSQL (no other database engines)
- NO localStorage or sessionStorage for application state (React state and database only)
- Each layer MUST be independently deployable and testable

### II. Spec-Driven Development (NON-NEGOTIABLE)

All code MUST be preceded by written specifications. No implementation may begin without approved spec.md, plan.md, and tasks.md files. This principle remains unchanged from Phase I and is even more critical in Phase II's complex multi-service architecture.

**Rationale**: Spec-driven development prevents architectural misalignment, catches integration issues early, ensures security requirements are considered upfront, and creates living documentation for multi-layer systems.

**Rules**:
- Specification (spec.md) MUST exist before plan.md
- Implementation plan (plan.md) MUST exist before tasks.md
- Task list (tasks.md) MUST exist before any code
- API contracts MUST be documented in spec before implementation
- Security requirements MUST be explicit in spec (auth, authorization, data isolation)
- Code changes MUST reference specific task IDs
- Claude Code MUST be used for all code generation (no manual coding)

### III. Test-First Development

Tests MUST be written or defined before implementation code. For Phase II, this includes API endpoint testing (via Postman/Thunder Client), multi-user testing scenarios, responsive UI testing (mobile/desktop), and authentication flow testing. Each task MUST include "How to Test" steps that verify the feature works correctly.

**Rationale**: Test-first development forces clear thinking about API contracts, user workflows, edge cases, and failure modes. In multi-service architectures, testing validates not just individual components but also integration points and security boundaries.

**Rules**:
- Each task MUST include specific test steps for both frontend and backend
- API endpoints MUST be testable via HTTP client tools before frontend integration
- Multi-user scenarios MUST be tested (create 2+ users, verify data isolation)
- Authentication flow MUST be tested (signup, signin, token validation, unauthorized access)
- Responsive design MUST be tested on mobile (375px) and desktop (1024px+) viewports
- Error cases MUST have defined test scenarios (invalid tokens, missing data, non-existent IDs)
- All tests MUST pass before marking task complete

### IV. Data Model Integrity with User Isolation

Database schema MUST maintain referential integrity, enforce user isolation at the data layer, and use SQLModel for type-safe ORM. Every user-scoped table MUST include user_id foreign key. All queries MUST filter by authenticated user_id to prevent data leakage.

**Rationale**: Multi-user systems require strict data isolation to prevent security breaches. Database-level isolation (enforced via foreign keys and query filters) provides defense-in-depth against application-layer bugs. SQLModel combines Pydantic validation with SQLAlchemy ORM for type safety.

**Rules**:
- User table managed by Better Auth (id: string, email: string, name: string, created_at: timestamp)
- Task table MUST include: id (int, auto), user_id (string, FK to users.id), title (str, 1-200 chars), description (str, 0-1000 chars), completed (bool, default false), created_at (timestamp), updated_at (timestamp)
- Every query MUST filter by authenticated user_id from JWT token
- Use SQLModel models for all database entities
- Foreign keys MUST enforce referential integrity (CASCADE delete where appropriate)
- Indexes MUST be added for frequently queried columns (user_id, created_at)
- Timestamps (created_at, updated_at) MUST be included on all tables
- Use Alembic for all schema migrations (no manual schema changes)
- Validation rules: title required (1-200 chars), description optional (max 1000 chars), user_id must exist in users table

### V. Input Validation and Error Handling

All user input MUST be validated at BOTH frontend and backend. API endpoints MUST use Pydantic models for request validation. Errors MUST be handled gracefully with proper HTTP status codes and user-friendly messages. Security-sensitive errors (auth failures) MUST NOT leak implementation details.

**Rationale**: Client-side validation improves UX by providing immediate feedback. Server-side validation is security-critical (never trust client). Proper HTTP status codes enable correct error handling in frontend. User-friendly error messages improve accessibility without compromising security.

**Rules**:
- Frontend MUST validate forms before submission (required fields, length limits, format)
- Backend MUST validate ALL inputs using Pydantic models (never trust client)
- Use proper HTTP status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Internal Server Error)
- Error responses MUST use consistent JSON format: `{"error": "message"}`
- Auth errors MUST return 401 with generic message (no "user not found" vs "wrong password" distinction)
- Validation errors MUST specify which field failed and why
- Internal errors MUST be logged but return generic 500 to client (no stack traces)
- Use FastAPI's HTTPException for error handling
- Frontend MUST display error messages in user-friendly manner

### VI. Clean Code and Multi-Language Standards

Code MUST follow language-specific conventions and clean code principles. Backend (Python) follows PEP 8. Frontend (TypeScript) follows strict TypeScript standards. Functions MUST be small, focused, and well-named. Code MUST be readable without excessive comments.

**Rationale**: Consistent code standards improve maintainability, enable code reviews, prevent bugs through type safety, and make onboarding faster. Multi-language projects require discipline to maintain quality across technology stacks.

**Backend (Python/FastAPI) Rules**:
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Use type hints for all function signatures
- Use Pydantic models for request/response schemas
- Use SQLModel for database models
- Async/await for all I/O operations (database, external APIs)
- Maximum function length: 30 lines (excluding docstrings)
- Docstrings for all public functions (Google style)

**Frontend (TypeScript/Next.js) Rules**:
- TypeScript strict mode MUST be enabled
- Use Server Components by default (Client Components only when needed for state, events, browser APIs)
- Use Server Actions for mutations (no direct API calls from Client Components)
- Follow Next.js App Router conventions (app/ directory structure)
- Use Tailwind CSS core utility classes only (no custom CSS)
- Component files MUST be single-purpose (one component per file)
- Maximum component length: 200 lines (excluding imports and types)
- Props MUST be typed with TypeScript interfaces

### VII. Windows via WSL 2 Only

Windows users MUST use Windows Subsystem for Linux (WSL 2) with Ubuntu. Direct Windows execution is not supported for this project.

**Rationale**: WSL 2 provides a consistent Linux environment, eliminating platform-specific issues and aligning with professional development practices where Linux is standard. This is especially important for Docker, shell scripts, and deployment tooling.

**Rules**:
- Windows development MUST occur in WSL 2
- WSL 2 MUST have Python 3.13+ and Node.js 20+ installed
- UV package manager MUST be installed for Python dependencies
- Docker Desktop MUST be integrated with WSL 2
- File paths MUST use Linux conventions within WSL

### VIII. User Isolation and Data Security (NEW)

Every API endpoint MUST require JWT authentication. The authenticated user_id from the JWT MUST match the {user_id} in the URL path. Users MUST only access their own data—no cross-user data access permitted. This principle is NON-NEGOTIABLE for security compliance.

**Rationale**: Multi-user systems are targets for privilege escalation attacks. Enforcing user_id matching at both API and database layers provides defense-in-depth. JWT tokens establish identity; URL validation prevents confused deputy attacks; database filters prevent SQL injection-based data leakage.

**Rules**:
- Every API endpoint (except public health check) MUST verify JWT token
- JWT MUST be validated using shared BETTER_AUTH_SECRET
- Decoded JWT user_id MUST match {user_id} in URL path (e.g., /api/{user_id}/tasks)
- Return 401 if token invalid or missing
- Return 403 if token valid but user_id mismatch
- Database queries MUST filter by authenticated user_id (e.g., `WHERE user_id = {authenticated_user}`)
- Never use URL user_id directly in queries (always use JWT user_id)
- Prepared statements ONLY (SQLModel handles this automatically)
- No sensitive data in URLs (task content, email addresses, etc.)
- CORS MUST be configured to allow only frontend domain

### IX. RESTful API Design (NEW)

API MUST follow RESTful conventions with consistent URL structure, proper HTTP methods, JSON payloads, and predictable behavior. This enables frontend/backend teams to work independently and makes the API self-documenting.

**Rationale**: RESTful conventions provide a shared language between frontend and backend teams. Consistency reduces bugs, improves cache-ability, enables tooling (OpenAPI, Postman collections), and makes APIs easier to learn and use.

**Rules**:
- URL structure: `/api/{user_id}/{resource}` (e.g., `/api/user123/tasks`)
- HTTP methods: GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove)
- Request/response MUST be JSON format
- POST creates resources and returns 201 with created resource
- PUT/PATCH updates resources and returns 200 with updated resource
- DELETE returns 204 (No Content) on success
- GET collection returns array: `[{task1}, {task2}]`
- GET single resource returns object: `{id, title, ...}`
- Use plural nouns for collections: `/tasks` not `/task`
- Filtering via query params: `/tasks?completed=true`
- Error responses in consistent format: `{"error": "message"}`

### X. Authentication-First Approach (NEW)

Authentication and authorization MUST be designed and implemented BEFORE building features. Better Auth handles user management; JWT tokens authenticate API requests. Every feature MUST consider auth requirements from the start.

**Rationale**: Retrofitting auth into existing systems leads to security gaps. Designing auth-first ensures every endpoint is protected, every query is user-scoped, and security reviews happen during design (not after deployment). Better Auth provides production-ready user management without reinventing authentication.

**Rules**:
- Use Better Auth for user management (signup, signin, session management)
- Better Auth MUST be configured with shared BETTER_AUTH_SECRET
- Frontend MUST include JWT token in Authorization header: `Bearer <token>`
- Backend MUST validate JWT on every request (except public endpoints)
- JWT MUST contain user_id and expiration (exp)
- Token expiration MUST be enforced (default: 24 hours)
- Frontend MUST handle 401 errors by redirecting to login
- Backend MUST never accept user_id from request body (always use JWT)
- Password requirements: minimum 8 characters (Better Auth handles this)
- No password reset in Phase II (out of scope; add in Phase III if needed)

### XI. Mobile-First Responsive Design (NEW)

UI MUST be responsive and functional on mobile devices (375px minimum width) and desktop (1024px+). Design mobile layout first, then enhance for larger screens. Use Tailwind's responsive utilities (sm:, md:, lg:) for breakpoint-specific styling.

**Rationale**: Mobile traffic dominates modern web usage. Mobile-first design ensures core functionality works on constrained screens, prevents desktop-centric assumptions (hover states, large click targets), and improves accessibility (larger touch targets benefit everyone).

**Rules**:
- Design for mobile (375px width) first, then tablet (768px), then desktop (1024px+)
- Touch targets MUST be minimum 44x44px (Apple/Android guidelines)
- Use Tailwind responsive prefixes: `sm:`, `md:`, `lg:`, `xl:`
- Test on mobile viewport during development (browser DevTools)
- Forms MUST be usable on mobile (large inputs, clear labels, appropriate input types)
- Loading states MUST be visible (spinners, skeletons)
- Error messages MUST be readable on small screens
- Empty states MUST guide users on what to do next
- Navigation MUST work on mobile (hamburger menu if needed)
- No horizontal scrolling on mobile (except intentional carousels)

### XII. Cloud-Native Deployment (NEW)

Application MUST be designed for cloud deployment from the start. Frontend deployed on Vercel, backend on Railway/Render, database on Neon. Use environment variables for all secrets and configuration. No localhost assumptions.

**Rationale**: Cloud deployment enables scalability, high availability, automated backups, and global distribution. Designing for cloud from the start (vs. retrofitting) prevents localhost assumptions (hardcoded URLs, file system dependencies) and ensures configuration is externalized (12-factor app principles).

**Rules**:
- Frontend MUST be deployed on Vercel (free tier)
- Backend MUST be deployed on Railway or Render (free tier)
- Database MUST be Neon Serverless PostgreSQL (free tier)
- Environment variables MUST be used for all configuration:
  - `DATABASE_URL` (Neon connection string)
  - `BETTER_AUTH_SECRET` (shared between frontend/backend)
  - `NEXT_PUBLIC_API_URL` (backend URL for frontend)
  - `ALLOWED_ORIGINS` (CORS configuration)
- Secrets MUST NEVER be committed to git (use .env.local, .gitignore)
- CORS MUST be configured for production frontend domain
- Use HTTPS in production (Vercel/Railway provide this automatically)
- No file system dependencies (no writing to disk on backend)
- No localhost hardcoded URLs (use environment variables)

## Scope and Constraints

### In Scope (Phase II)
- Full-stack web application with Next.js frontend and FastAPI backend
- User authentication (signup, signin) via Better Auth with JWT
- Multi-user support with strict data isolation
- Six REST API endpoints: GET /tasks, POST /tasks, GET /tasks/{id}, PATCH /tasks/{id}, DELETE /tasks/{id}, POST /tasks/{id}/complete
- Persistent storage in Neon PostgreSQL via SQLModel ORM
- Responsive UI (mobile 375px+, desktop 1024px+) using Tailwind CSS
- Task CRUD operations (same five features as Phase I, now multi-user)
- Input validation (frontend and backend)
- Error handling with proper HTTP status codes
- Cloud deployment (Vercel + Railway/Render + Neon)
- Monorepo structure with clear frontend/backend separation
- API testing via Postman/Thunder Client
- Multi-user testing scenarios

### Out of Scope (Future Phases or Explicitly Excluded)
- AI chatbot interface (Phase III)
- Natural language task commands (Phase III)
- Task search/filtering beyond basic completed status
- Task priorities, categories, tags, due dates
- Collaborative features (shared tasks, teams)
- Email notifications
- Password reset functionality (add in Phase III if needed)
- OAuth providers (Google, GitHub) beyond email/password
- Real-time updates (WebSockets)
- File attachments
- Automated unit/integration tests (manual testing only for Phase II)
- CI/CD pipelines
- Advanced deployment (Kubernetes, load balancing)

### Technology Constraints
- Frontend: Next.js 16+ (App Router), React 19, TypeScript, Tailwind CSS
- Backend: Python 3.13+, FastAPI, SQLModel, Alembic
- Database: Neon Serverless PostgreSQL ONLY (no other databases)
- Auth: Better Auth with JWT tokens
- Deployment: Vercel (frontend), Railway or Render (backend), Neon (database)
- Package managers: npm (frontend), UV (backend)
- NO localStorage or sessionStorage for application state
- NO custom CSS (Tailwind utilities only)
- NO GraphQL (REST API only)
- NO Redis or other caching layers (Phase II simplicity)

## Project Structure

Phase II MUST follow this exact monorepo structure:

```
hackathon-full-stack-template/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # This file
│   └── templates/                   # SpecKit Plus templates
├── specs/
│   └── todo-web-app/
│       ├── spec.md                  # Feature specification
│       ├── plan.md                  # Implementation plan
│       └── tasks.md                 # Task breakdown
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home/landing page
│   │   ├── auth/
│   │   │   ├── signin/page.tsx      # Sign in page
│   │   │   └── signup/page.tsx      # Sign up page
│   │   └── dashboard/
│   │       └── page.tsx             # Task dashboard (authenticated)
│   ├── components/
│   │   ├── TaskList.tsx             # Task list component
│   │   ├── TaskForm.tsx             # Add/edit task form
│   │   └── TaskItem.tsx             # Single task item
│   ├── lib/
│   │   ├── api-client.ts            # Centralized API client
│   │   └── auth.ts                  # Better Auth configuration
│   ├── public/                      # Static assets
│   ├── .env.local                   # Frontend environment variables (not committed)
│   ├── next.config.ts               # Next.js configuration
│   ├── tailwind.config.ts           # Tailwind configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── package.json                 # Frontend dependencies
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── models.py                # SQLModel database models
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── crud.py                  # Database operations
│   │   ├── auth.py                  # JWT validation middleware
│   │   └── routers/
│   │       └── tasks.py             # Task API endpoints
│   ├── alembic/
│   │   ├── versions/                # Database migration files
│   │   └── env.py                   # Alembic configuration
│   ├── .env                         # Backend environment variables (not committed)
│   ├── alembic.ini                  # Alembic config file
│   ├── pyproject.toml               # Python project config (UV)
│   └── README.md                    # Backend setup instructions
├── history/
│   ├── prompts/                     # Prompt History Records
│   └── adr/                         # Architecture Decision Records
├── .gitignore                       # Git ignore (includes .env files)
├── README.md                        # Project overview and setup
├── CLAUDE.md                        # Claude Code instructions
└── docker-compose.yml               # Optional local development setup
```

**Structure Rationale**: Monorepo enables shared configuration and coordinated deployments while maintaining clear frontend/backend separation. Each service can be independently deployed and scaled. Centralized specs/ and history/ directories support spec-driven development across both services.

## Development Workflow

### Specification Phase
1. User provides feature description
2. Claude Code generates spec.md with:
   - User stories
   - Acceptance criteria
   - API contracts (endpoints, request/response schemas)
   - Data model (database tables, relationships)
   - Security requirements (auth, authorization, user isolation)
   - UI mockups/wireframes (text descriptions acceptable)
   - Responsive design requirements
3. User reviews and approves specification
4. Specification frozen before planning

### Planning Phase
1. Claude Code generates plan.md with:
   - Architecture decisions (frontend/backend interaction, data flow)
   - Technology choices (justified by requirements)
   - API contract details (full endpoint specs)
   - Database schema (SQLModel models, migrations)
   - Security implementation (JWT validation, CORS, user isolation)
   - Deployment strategy (environment variables, hosting platforms)
   - Constitution Check section (references relevant principles)
2. User reviews and approves plan
3. Plan frozen before task breakdown

### Task Phase
1. Claude Code generates tasks.md with:
   - Database setup tasks (Neon project, connection, models, migrations)
   - Backend tasks (API endpoints with auth, validation, error handling)
   - Frontend tasks (UI components, API integration, auth flows)
   - Testing tasks (API testing, multi-user testing, responsive testing)
   - Deployment tasks (environment variables, Vercel, Railway/Render)
2. Each task MUST include:
   - Implementation steps (what code to write)
   - Test steps (how to verify it works)
   - Acceptance criteria (what "done" looks like)
3. User reviews and approves task list
4. Tasks executed sequentially with test-first approach

### Implementation Phase
1. For each task:
   - Read task requirements and acceptance criteria
   - Write or prepare test steps (API calls, UI interactions)
   - Implement feature (backend first, then frontend)
   - Execute test steps manually
   - Verify acceptance criteria met
   - Mark task complete if tests pass
2. Commit after each completed task with descriptive message
3. Create Prompt History Record (PHR) for significant milestones

### Validation Phase
1. API Endpoint Testing:
   - Test all six endpoints via Postman/Thunder Client
   - Verify proper HTTP status codes
   - Verify error handling (invalid tokens, missing data, etc.)
   - Verify request/response schemas match API contract
2. Multi-User Testing:
   - Create 2+ user accounts
   - Verify each user sees only their own tasks
   - Verify unauthorized access is blocked (401/403)
3. Responsive Testing:
   - Test UI at 375px (mobile), 768px (tablet), 1024px+ (desktop)
   - Verify touch targets are minimum 44x44px
   - Verify no horizontal scrolling on mobile
4. Authentication Flow Testing:
   - Test signup with valid/invalid inputs
   - Test signin with correct/incorrect credentials
   - Verify JWT token is stored and sent on API calls
   - Verify 401 redirects to login page
5. Deployment Validation:
   - Verify frontend deployed on Vercel (accessible via HTTPS)
   - Verify backend deployed on Railway/Render (health check endpoint responds)
   - Verify database connected (API returns data, no connection errors)
   - Verify environment variables configured correctly
   - Verify CORS allows frontend domain

## Success Criteria

Phase II is complete when ALL of the following are true:

### Functional Completeness
- ✅ User can sign up with email/password via Better Auth
- ✅ User can sign in and receive JWT token
- ✅ Authenticated user can view their tasks (empty state handled)
- ✅ Authenticated user can add tasks with title and optional description
- ✅ Authenticated user can update task title and description
- ✅ Authenticated user can toggle task completion status
- ✅ Authenticated user can delete tasks
- ✅ Users cannot access other users' tasks (verified with 2+ users)
- ✅ All API endpoints require valid JWT token (401 if missing/invalid)
- ✅ Frontend handles errors gracefully (user-friendly messages, no crashes)

### API Quality
- ✅ All six REST endpoints implemented: GET /tasks, POST /tasks, GET /tasks/{id}, PATCH /tasks/{id}, DELETE /tasks/{id}, POST /tasks/{id}/complete
- ✅ All endpoints use proper HTTP methods and status codes
- ✅ Request/response schemas match API contract in spec.md
- ✅ JWT validation on all endpoints (except health check)
- ✅ User_id from JWT matches {user_id} in URL (403 if mismatch)
- ✅ Database queries filtered by authenticated user_id
- ✅ CORS configured for frontend domain
- ✅ Error responses use consistent JSON format

### Frontend Quality
- ✅ UI is responsive on mobile (375px), tablet (768px), desktop (1024px+)
- ✅ Tailwind CSS used for all styling (no custom CSS)
- ✅ TypeScript strict mode enabled (no `any` types)
- ✅ Server Components used by default (Client Components only when needed)
- ✅ Loading states shown during async operations
- ✅ Error messages displayed in user-friendly manner
- ✅ Forms validate inputs before submission
- ✅ Empty states guide users on next actions

### Backend Quality
- ✅ FastAPI follows async/await patterns for I/O
- ✅ SQLModel used for all database models
- ✅ Pydantic used for request/response validation
- ✅ Type hints on all function signatures
- ✅ JWT middleware validates tokens on all protected endpoints
- ✅ HTTPException used for error responses
- ✅ No hardcoded secrets (environment variables only)

### Database Quality
- ✅ Neon PostgreSQL project created and connected
- ✅ SQLModel models defined (User, Task) with proper relationships
- ✅ Foreign key constraints enforced (user_id → users.id)
- ✅ Indexes added for performance (user_id, created_at)
- ✅ Alembic migrations created and applied
- ✅ Timestamps (created_at, updated_at) on all tables
- ✅ Data persists correctly (create task, close browser, reopen → task still there)

### Security Quality
- ✅ Better Auth configured with shared BETTER_AUTH_SECRET
- ✅ JWT tokens validated on every API request
- ✅ Users can only access their own data (enforced at API and database layers)
- ✅ No sensitive data in URLs or error messages
- ✅ CORS restricted to frontend domain only
- ✅ No localStorage used for application state
- ✅ Environment variables used for all secrets

### Documentation
- ✅ spec.md exists with API contracts, data model, security requirements
- ✅ plan.md exists with architecture decisions and Constitution Check
- ✅ tasks.md exists with all tasks marked complete
- ✅ README.md provides setup instructions for frontend and backend
- ✅ Frontend README includes deployment instructions (Vercel)
- ✅ Backend README includes deployment instructions (Railway/Render)
- ✅ Environment variable documentation (.env.example files)

### Testing
- ✅ API endpoints tested via Postman/Thunder Client (all pass)
- ✅ Multi-user testing completed (2+ users, data isolated)
- ✅ Authentication flow tested (signup, signin, token validation)
- ✅ Responsive design tested (mobile, tablet, desktop)
- ✅ Error scenarios tested (invalid tokens, missing data, non-existent IDs)
- ✅ Edge cases tested (empty task lists, very long titles/descriptions)

### Deployment
- ✅ Frontend deployed on Vercel (publicly accessible via HTTPS)
- ✅ Backend deployed on Railway or Render (health check responds)
- ✅ Database on Neon (connected and storing data)
- ✅ Environment variables configured on all platforms
- ✅ CORS configured for production frontend domain
- ✅ Demo video created showing all features working

### Code Quality
- ✅ Backend follows PEP 8 conventions
- ✅ Frontend follows TypeScript strict mode
- ✅ Functions are focused and appropriately sized
- ✅ No global state (React state and database only)
- ✅ Error handling uses try-except (backend) and error boundaries (frontend)
- ✅ Code is readable without excessive comments

## Governance

### Amendment Process
Constitution changes MUST be documented with:
- Clear rationale for the change
- Version increment following semantic versioning
- Update to dependent templates (spec, plan, tasks)
- Sync Impact Report (HTML comment at top of file)
- Approval before taking effect

### Version Semantics
- MAJOR: Principle removal, fundamental architectural change, scope redefinition (e.g., Phase I → Phase II)
- MINOR: New principle added, significant expansion of existing principle
- PATCH: Clarifications, examples, formatting improvements, typo fixes

### Compliance
- All spec.md files MUST reference relevant constitution principles
- All plan.md files MUST include "Constitution Check" section validating adherence
- All code reviews MUST verify constitutional compliance (especially security principles)
- PHR (Prompt History Records) MUST document any principle violations with justification
- Security principles (VIII, IX, X) are NON-NEGOTIABLE—no exceptions without explicit written approval

### Non-Compliance Handling
If a principle violation is necessary (e.g., temporarily disable CORS for local development):
1. Document in plan.md "Complexity Tracking" or "Security Exceptions" section
2. Provide clear justification for why violation is needed
3. Explain why compliant alternatives were insufficient
4. Define remediation steps (how to restore compliance)
5. Get explicit user approval before proceeding
6. Record decision in ADR if architecturally significant
7. Add TODO comments in code marking the violation
8. Ensure violation is not deployed to production (local dev only)

### Compliance Review Checklist
Before marking Phase II complete, verify:
- [ ] Every API endpoint validates JWT (Principle VIII)
- [ ] Every database query filters by user_id (Principle IV, VIII)
- [ ] API follows RESTful conventions (Principle IX)
- [ ] UI is responsive on mobile (Principle XI)
- [ ] No secrets committed to git (Principle XII)
- [ ] Environment variables used for configuration (Principle XII)
- [ ] Better Auth configured correctly (Principle X)
- [ ] CORS configured for production (Principle VIII, XII)
- [ ] Spec → Plan → Tasks → Implementation flow followed (Principle II)
- [ ] Multi-user testing completed (Principle VIII)

**Version**: 2.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
