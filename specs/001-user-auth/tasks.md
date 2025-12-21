# Tasks: Multi-User Authentication System

**Input**: Design documents from `/specs/001-user-auth/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (complete)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`, `frontend/lib/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize monorepo structure, install dependencies, configure development environment

- [X] T001 Create backend directory structure with app/, alembic/, tests/ subdirectories
- [X] T002 [P] Create frontend directory structure with app/, components/, lib/ subdirectories
- [X] T003 [P] Initialize backend Python project with pyproject.toml (UV package manager)
- [X] T004 [P] Initialize frontend Next.js project with package.json, tsconfig.json, tailwind.config.ts
- [X] T005 [P] Create backend .env.example with DATABASE_URL, BETTER_AUTH_SECRET, ALLOWED_ORIGINS placeholders
- [X] T006 [P] Create frontend .env.local.example with BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL, DATABASE_URL placeholders
- [X] T007 Update .gitignore to exclude .env, .env.local, node_modules/, __pycache__/, .venv/
- [X] T008 Install backend dependencies in backend/pyproject.toml: fastapi, uvicorn, sqlmodel, alembic, pyjwt, pydantic, asyncpg
- [X] T009 [P] Install frontend dependencies in frontend/package.json: next, react, react-dom, better-auth, tailwindcss, typescript

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Set up database connection, Neon project, Alembic migrations, and core configuration required by all user stories

- [X] T010 Create Neon PostgreSQL project named "hackathon-todo-app" and obtain connection string
- [X] T011 Configure backend database connection in backend/app/database.py with async SQLModel engine
- [X] T012 [P] Initialize Alembic in backend/alembic/ with env.py configured to use DATABASE_URL from environment
- [X] T013 [P] Create backend/app/models.py with User and Task SQLModel models per data-model.md schema
- [X] T014 Generate Alembic migration for users and tasks tables: alembic revision --autogenerate -m "Create users and tasks"
- [X] T015 Apply Alembic migration: alembic upgrade head (verify tables created in Neon Console)
- [X] T016 Create backend/app/schemas.py with Pydantic request/response models (SignupRequest, SigninRequest, UserResponse, TokenResponse)
- [X] T017 Create backend/app/auth.py with verify_jwt() middleware function using PyJWT per research.md decision
- [X] T018 Create backend/app/main.py FastAPI app with CORS middleware configured per research.md
- [X] T019 [P] Configure Better Auth in frontend/lib/auth.ts with JWT plugin, 7-day expiry, PostgreSQL provider
- [X] T020 [P] Create frontend/lib/api-client.ts with base fetch wrapper including JWT Authorization header

---

## Phase 3: User Story 1 - New User Account Creation (Priority P1)

**Story Goal**: Enable new users to create accounts with email/password and access their dashboard

**Independent Test**: Visit signup page, enter valid credentials, verify account created in database and redirected to dashboard with active session

**Acceptance Criteria from Spec**:
- Account created with valid name, unique email, password (min 8 chars)
- Duplicate email shows "Email already registered"  error
- Short password shows "Password must be at least 8 characters" error
- Invalid email shows "Please enter a valid email" error
- Empty fields show field-level error messages

### Backend Implementation

- [X] T021 [US1] Create backend/app/routers/auth.py with POST /api/auth/signup endpoint per contracts/signup.md
- [X] T022 [US1] Implement signup logic in backend/app/routers/auth.py: validate email uniqueness, create user via Better Auth, generate JWT
- [X] T023 [US1] Add email validation in signup endpoint: RFC 5322 format check, lowercase normalization
- [X] T024 [US1] Add password validation in signup endpoint: minimum 8 characters, Better Auth hashing
- [X] T025 [US1] Add name validation in signup endpoint: 1-100 characters, whitespace trimming
- [X] T026 [US1] Implement error handling in signup: 400 for duplicate email, validation errors, 500 for database failures
- [X] T027 [US1] Include auth router in backend/app/main.py: app.include_router(auth_router, prefix="/api/auth")

### Frontend Implementation

- [X] T028 [P] [US1] Create frontend/app/auth/signup/page.tsx with signup form (name, email, password fields)
- [X] T029 [P] [US1] Create frontend/components/AuthForm.tsx reusable form component with Tailwind styling
- [X] T030 [US1] Implement form validation in signup page: required fields, email format, password length (client-side)
- [X] T031 [US1] Implement signup form submission: call POST /api/auth/signup, store token in localStorage, redirect to /dashboard
- [X] T032 [US1] Add error message display in signup form for server validation errors (duplicate email, etc.)
- [X] T033 [US1] Add loading state to signup form (disable button, show spinner during API request)
- [X] T034 [P] [US1] Create frontend/components/ErrorMessage.tsx component for displaying validation errors
- [X] T035 [P] [US1] Create frontend/components/LoadingSpinner.tsx component for async operation indicators

### Testing

- [X] T036 [US1] Test signup with valid credentials via Postman: verify 201 response with user object and JWT token
- [X] T037 [US1] Test signup with duplicate email via Postman: verify 400 error "Email already registered"
- [X] T038 [US1] Test signup with invalid email via Postman: verify 400 error "Please enter a valid email"
- [X] T039 [US1] Test signup with short password via Postman: verify 400 error "Password must be at least 8 characters"
- [X] T040 [US1] Test signup form in browser: verify client-side validation prevents submission with empty/invalid fields
- [X] T041 [US1] Test signup form in browser: verify successful signup redirects to /dashboard with token stored in localStorage
- [X] T042 [US1] Verify user record created in Neon database with correct UUID, hashed password, timestamps

---

## Phase 4: User Story 2 - Returning User Sign In (Priority P1)

**Story Goal**: Enable registered users to sign in with credentials and access their existing data

**Independent Test**: Create account, sign out, sign in with correct credentials (access dashboard), sign in with wrong password (see error)

**Acceptance Criteria from Spec**:
- Signin with correct credentials redirects to dashboard
- Wrong password shows "Invalid email or password" error
- Non-existent email shows "Invalid email or password" error
- Empty fields show field-level error messages
- Session persists after browser close (within 7 days)

### Backend Implementation

- [X] T043 [US2] Create POST /api/auth/signin endpoint in backend/app/routers/auth.py per contracts/signin.md
- [X] T044 [US2] Implement signin logic: retrieve user by email (case-insensitive), verify password via Better Auth
- [X] T045 [US2] Implement JWT token generation on successful signin: include user_id, email, name, 7-day expiry
- [X] T046 [US2] Implement generic error response for invalid credentials: "Invalid email or password" (don't reveal which field is wrong)
- [X] T047 [US2] Add validation for missing email/password fields: return specific error messages

### Frontend Implementation

- [X] T048 [P] [US2] Create frontend/app/auth/signin/page.tsx with signin form (email, password fields)
- [X] T049 [US2] Implement form validation in signin page: required fields, email format (client-side)
- [X] T050 [US2] Implement signin form submission: call POST /api/auth/signin, store token in localStorage, redirect to /dashboard
- [X] T051 [US2] Add error message display for signin failures: show "Invalid email or password" from backend
- [X] T052 [US2] Add loading state to signin form (disable button, show spinner during API request)
- [X] T053 [US2] Add "Don't have an account? Sign up" link to signin page (navigate to /auth/signup)
- [X] T054 [US2] Add "Already have account? Sign in" link to signup page (navigate to /auth/signin)

### Testing

- [X] T055 [US2] Test signin with correct credentials via Postman: verify 200 response with user object and JWT token
- [X] T056 [US2] Test signin with wrong password via Postman: verify 400 error "Invalid email or password"
- [X] T057 [US2] Test signin with non-existent email via Postman: verify 400 error "Invalid email or password"
- [X] T058 [US2] Test signin with missing email via Postman: verify 400 error "Email is required"
- [X] T059 [US2] Test signin form in browser: verify successful signin redirects to /dashboard
- [X] T060 [US2] Test signin form in browser: verify incorrect password shows error message
- [X] T061 [US2] Test session persistence: sign in, close browser, reopen, verify user still authenticated

---

## Phase 5: User Story 5 - Data Isolation Between Users (Priority P1)

**Story Goal**: Enforce that users can only access their own data through JWT validation and database filtering

**Independent Test**: Create 2 user accounts, add tasks to each, verify User A cannot access User B's tasks via URL manipulation

**Acceptance Criteria from Spec**:
- User A sees only their own tasks in task list
- User A accessing User B's task URL returns "Access denied"
- Tasks created by User A are associated with User A's user_id
- User A can only modify/delete their own tasks
- Unauthenticated access redirects to signin

**Note**: This story depends on Task CRUD endpoints (separate feature), but JWT middleware implementation belongs here

### Backend Implementation (JWT Middleware - Reusable for All Protected Endpoints)

- [X] T062 [US5] Implement verify_jwt() function in backend/app/auth.py: extract token from Authorization header
- [X] T063 [US5] Add JWT signature verification in verify_jwt(): use BETTER_AUTH_SECRET, algorithms=["HS256"]
- [X] T064 [US5] Add token expiry validation in verify_jwt(): check exp claim, raise 401 if expired
- [X] T065 [US5] Add user_id extraction in verify_jwt(): return user_id from JWT payload (or sub claim)
- [X] T066 [US5] Add error handling in verify_jwt(): raise HTTPException(401) for missing/invalid/expired tokens
- [X] T067 [US5] Create user_id validation helper function: verify_user_id_match(url_user_id, jwt_user_id) raises 403 on mismatch

### Frontend Implementation (Protected Route Guards)

- [X] T068 [P] [US5] Create frontend/middleware.ts with authentication check: redirect to /auth/signin if no token
- [X] T069 [P] [US5] Configure Next.js middleware to protect /dashboard and future /tasks routes
- [X] T070 [US5] Add 401 error handling in frontend/lib/api-client.ts: clear token, redirect to /auth/signin on unauthorized
- [X] T071 [US5] Add 403 error handling in frontend/lib/api-client.ts: show "Access denied" message
- [X] T072 [US5] Implement token inclusion in api-client: add Authorization: Bearer {token} header to all requests

### Testing (Multi-User Scenarios)

- [X] T073 [US5] Create User A account via signup API: save user_id_a and token_a
- [X] T074 [US5] Create User B account via signup API: save user_id_b and token_b
- [X] T075 [US5] Test User A accessing User A's endpoint with User A's token: verify 200 OK (when task endpoints exist)
- [X] T076 [US5] Test User A accessing User B's endpoint with User A's token: verify 403 "Access denied to this resource"
- [X] T077 [US5] Test accessing any endpoint without token: verify 401 "Authentication required"
- [X] T078 [US5] Test accessing any endpoint with invalid token: verify 401 "Invalid or malformed token"
- [X] T079 [US5] Test accessing any endpoint with expired token: verify 401 "Token expired, please log in again"

---

## Phase 6: User Story 3 - Secure Sign Out (Priority P2)

**Story Goal**: Enable users to sign out securely, removing authentication token and preventing access to protected routes

**Independent Test**: Sign in, click sign out button, verify token removed and protected routes redirect to signin

**Acceptance Criteria from Spec**:
- Sign out button removes token and redirects to signin page
- After signout, accessing protected routes redirects to signin
- Browser back button after signout does not access protected pages

### Backend Implementation

- [X] T080 [US3] Create POST /api/auth/signout endpoint in backend/app/routers/auth.py per contracts/signout.md
- [X] T081 [US3] Implement signout logic: return success message (Phase II client-side only, no token blacklist)
- [X] T082 [US3] Add comment in signout endpoint: "Phase III enhancement: add token to blacklist (Redis) for server-side invalidation"

### Frontend Implementation

- [X] T083 [P] [US3] Create frontend/app/auth/signout/page.tsx or add signout function to layout component
- [X] T084 [US3] Implement signout logic in frontend: remove token from localStorage, clear user data
- [X] T085 [US3] Add redirect to /auth/signin after signout
- [X] T086 [US3] Create "Sign Out" button in dashboard layout (visible when authenticated)

### Testing

- [X] T087 [US3] Test signout in browser: click button, verify redirect to /auth/signin
- [X] T088 [US3] Test signout in browser: after signout, access /dashboard, verify redirect to /auth/signin
- [X] T089 [US3] Test signout in browser: after signout, browser back button, verify cannot access protected pages
- [X] T090 [US3] Verify token removed from localStorage after signout

---

## Phase 7: User Story 4 - Persistent Session (Priority P2)

**Story Goal**: Maintain user authentication across page refreshes and browser sessions within token expiry period

**Independent Test**: Sign in, refresh page, verify user stays authenticated and dashboard accessible

**Acceptance Criteria from Spec**:
- Refresh page → user remains signed in
- Navigate between pages → authentication persists
- Expired token → redirect to signin with message

### Frontend Implementation

- [X] T091 [US4] Implement auth state management in frontend/app/layout.tsx: check localStorage for token on mount
- [X] T092 [US4] Create auth context or state to track authenticated user across components
- [X] T093 [US4] Implement token validation on app load: if token exists, verify user is authenticated
- [X] T094 [US4] Add token expiry handling: catch 401 errors, show "Token expired, please log in again" message, redirect to signin
- [X] T095 [US4] Preserve originally requested URL in sessionStorage when redirecting to signin (for return after login)
- [X] T096 [US4] Restore original URL after successful signin if returnUrl exists in sessionStorage

### Testing

- [X] T097 [US4] Test session persistence: sign in, refresh page, verify user still authenticated
- [X] T098 [US4] Test navigation persistence: sign in, navigate to different pages, verify token persists
- [X] T099 [US4] Test browser close/reopen: sign in, close browser, reopen within 7 days, verify still authenticated
- [X] T100 [US4] Test expired token handling: manually modify token expiry, access protected route, verify redirect to signin
- [X] T101 [US4] Test return URL preservation: access /dashboard (redirect to signin), signin, verify redirect back to /dashboard

---

## Phase 8: Dashboard & Landing Pages

**Purpose**: Create landing page, protected dashboard, and basic navigation structure

- [X] T102 [P] Create frontend/app/page.tsx landing page with "Sign In" and "Sign Up" buttons
- [X] T103 [P] Create frontend/app/dashboard/page.tsx protected dashboard (placeholder for future task features)
- [X] T104 Add authentication check to dashboard page: redirect to /auth/signin if not authenticated
- [X] T105 [P] Create frontend/app/layout.tsx with conditional navigation (show "Sign Out" if authenticated)
- [X] T106 Add responsive styling to landing page: mobile (375px) and desktop (1024px+) using Tailwind

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, responsive design verification, error handling improvements, documentation

- [X] T107 [P] Verify all forms are responsive on mobile (375px width): signup, signin forms scale correctly
- [X] T108 [P] Verify touch targets are minimum 44x44px on mobile: buttons, input fields
- [X] T109 Add keyboard navigation support to all forms: tab order, enter to submit
- [X] T110 [P] Add loading states to all async operations: signup, signin, API requests show spinners
- [X] T111 [P] Verify error messages are user-friendly and security-conscious: no stack traces, no implementation details
- [X] T112 Create backend/README.md with setup instructions from quickstart.md (backend section)
- [X] T113 [P] Create frontend/README.md with setup instructions from quickstart.md (frontend section)
- [X] T114 [P] Create .env.example files with placeholder values (never commit actual secrets)
- [X] T115 [P] Update root README.md with monorepo structure overview and link to quickstart.md
- [X] T116 Verify CORS configuration allows frontend domain: test from browser at http://localhost:3000
- [X] T117 [P] Add health check endpoint in backend/app/main.py: GET /health returns {"status": "ok"}

---

## Dependencies & Execution Order

### Story Completion Order (by Priority)

```
Phase 1 (Setup) → Phase 2 (Foundational)
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    Phase 3 (US1)  Phase 4 (US2)  Phase 5 (US5)
    [Signup - P1]  [Signin - P1]  [Isolation - P1]
         ↓             ↓             ↓
         └─────────────┼─────────────┘
                       ↓
                  Phase 6 (US3)
                  [Signout - P2]
                       ↓
                  Phase 7 (US4)
                  [Persistence - P2]
                       ↓
                  Phase 8 (Dashboard)
                       ↓
                  Phase 9 (Polish)
```

### Inter-Story Dependencies

- **US1 (Signup) + US2 (Signin) → US5 (Isolation)**: JWT middleware (US5) is used by signup/signin to return tokens
- **US1 + US2 → US3 (Signout)**: Cannot sign out without ability to sign in
- **US1 + US2 → US4 (Persistence)**: Session persistence requires signin to create session
- **US1 + US2 + US5 → Dashboard**: Dashboard requires authentication (US1/US2) and uses JWT middleware (US5)

**Recommendation**: Implement in this order:
1. **Phase 3 (US1 - Signup)**: Create accounts
2. **Phase 4 (US2 - Signin)**: Access existing accounts
3. **Phase 5 (US5 - Isolation)**: Enforce security (JWT middleware can be implemented alongside US1/US2)
4. **Phase 6 (US3 - Signout)**: Logout functionality
5. **Phase 7 (US4 - Persistence)**: Session persistence
6. **Phase 8 (Dashboard)**: UI polish
7. **Phase 9 (Polish)**: Final touches

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - Parallelizable Tasks
- T002 (frontend structure) || T003 (backend pyproject.toml) || T004 (frontend config)
- T005 (backend .env.example) || T006 (frontend .env.local.example)
- T008 (backend dependencies) || T009 (frontend dependencies)

**Benefit**: Setup can be done in ~5 minutes with parallel execution vs ~15 minutes sequential

### Phase 2 (Foundational) - Parallelizable Tasks
- T012 (Alembic init) || T013 (SQLModel models)
- T019 (Better Auth config) || T020 (API client)

**Benefit**: Backend and frontend foundations can be built simultaneously

### Phase 3 (US1) - Parallelizable Tasks
- T028 (signup page) || T029 (AuthForm component) || T034 (ErrorMessage) || T035 (LoadingSpinner)

**Benefit**: Frontend components can be built in parallel while backend endpoints are being implemented

### Phase 8 (Dashboard) - Parallelizable Tasks
- T102 (landing page) || T103 (dashboard page) || T105 (layout)

**Benefit**: All pages can be created simultaneously

### Phase 9 (Polish) - Parallelizable Tasks
- T107 (responsive verification) || T108 (touch targets) || T110 (loading states) || T111 (error messages)
- T112 (backend README) || T113 (frontend README) || T114 (.env.example) || T115 (root README)

**Benefit**: Documentation and UX polish can be done in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Deliver User Story 1 + User Story 2 + User Story 5 FIRST** (All Priority P1):
- Tasks T001-T079 (Phases 1-5)
- Delivers: Signup, Signin, JWT security, user isolation
- **Independent Test**: Users can create accounts, sign in, and their data is isolated
- **Value**: Core authentication working, multi-user foundation complete

**Then Add User Story 3 + User Story 4** (Priority P2):
- Tasks T080-T101 (Phases 6-7)
- Delivers: Signout, session persistence
- **Independent Test**: Users can sign out and sessions persist across refreshes
- **Value**: Complete authentication UX

**Finally Add Dashboard + Polish** (Priority P3):
- Tasks T102-T117 (Phases 8-9)
- Delivers: Landing page, dashboard, responsive design, documentation
- **Independent Test**: Full user journey from landing page to dashboard
- **Value**: Production-ready UI

### Incremental Delivery

1. **Sprint 1** (MVP): T001-T079 (US1 + US2 + US5)
   - Outcome: Authentication working, API testable via Postman
   - Demo: Show signup/signin via Postman, verify JWT validation, show user isolation

2. **Sprint 2** (Complete Auth): T080-T101 (US3 + US4)
   - Outcome: Signout and session persistence working
   - Demo: Show full auth flow in browser UI

3. **Sprint 3** (Polish): T102-T117 (Dashboard + Polish)
   - Outcome: Production-ready UI, responsive design, documentation
   - Demo: Show complete user journey, mobile responsiveness

---

## Testing Strategy

### Unit Testing Scope (Manual - No Automated Tests in Phase II)

**Backend Testing (Postman/Thunder Client)**:
- All auth endpoints: signup, signin, signout
- JWT middleware: valid token, invalid token, expired token, missing token
- User_id validation: matching user_id, mismatched user_id
- Error scenarios: duplicate email, wrong password, missing fields

**Frontend Testing (Browser)**:
- Signup form: valid inputs, validation errors, loading states
- Signin form: valid inputs, wrong password, missing fields
- Signout: token removed, redirect to signin
- Protected routes: redirect when unauthenticated
- Session persistence: refresh, navigate, close/reopen browser

**Multi-User Testing**:
- Create 2+ user accounts
- Verify each user sees only their data
- Attempt cross-user access via URL manipulation (verify 403)

### Integration Testing Scope

- End-to-end auth flow: signup → signin → access dashboard → signout
- Error handling: network failures, database down, invalid inputs
- Responsive design: mobile (375px), tablet (768px), desktop (1024px+)

---

## Task Summary

**Total Tasks**: 117
**Parallelizable Tasks**: 24 (marked with [P])
**Estimated Effort**:
- Phase 1 (Setup): 1-2 hours
- Phase 2 (Foundational): 2-3 hours
- Phase 3 (US1 - Signup): 3-4 hours
- Phase 4 (US2 - Signin): 2-3 hours
- Phase 5 (US5 - Isolation): 3-4 hours
- Phase 6 (US3 - Signout): 1-2 hours
- Phase 7 (US4 - Persistence): 2-3 hours
- Phase 8 (Dashboard): 1-2 hours
- Phase 9 (Polish): 2-3 hours
- **Total**: 18-26 hours

**MVP Delivery**: Tasks T001-T079 (Phases 1-5) deliver core authentication in ~11-16 hours

**Story Breakdown**:
- User Story 1 (Signup): 22 tasks (T021-T042)
- User Story 2 (Signin): 19 tasks (T043-T061)
- User Story 3 (Signout): 11 tasks (T080-T090)
- User Story 4 (Persistence): 11 tasks (T091-T101)
- User Story 5 (Isolation): 18 tasks (T062-T079)
- Setup: 9 tasks (T001-T009)
- Foundational: 11 tasks (T010-T020)
- Dashboard: 5 tasks (T102-T106)
- Polish: 11 tasks (T107-T117)

---

---

## Phase 10: OAuth Integration (Google & GitHub)

**Purpose**: Add social authentication (OAuth) for Google and GitHub signup/signin alongside existing email/password authentication

**Note**: Frontend UI already exists. Only backend implementation is required.

### Backend OAuth Setup

- [X] T118 Install OAuth dependencies in backend/pyproject.toml: authlib, httpx (if not already present)
- [X] T119 Add OAuth environment variables to backend/.env.example: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, OAUTH_REDIRECT_URI
- [X] T120 Create backend/app/oauth.py with OAuth client configuration for Google and GitHub using authlib
- [X] T121 Configure Google OAuth client in oauth.py: set authorization endpoint, token endpoint, userinfo endpoint
- [X] T122 Configure GitHub OAuth client in oauth.py: set authorization endpoint, token endpoint, user endpoint

### Google OAuth Implementation

- [X] T123 Create GET /api/auth/google/login endpoint in backend/app/routers/auth.py: generate OAuth authorization URL with state parameter
- [X] T124 Create GET /api/auth/google/callback endpoint: exchange authorization code for access token
- [X] T125 Implement Google userinfo fetch in callback: retrieve email, name, profile picture from Google API
- [X] T126 Implement user lookup/creation in Google callback: check if user exists by email, create if new user
- [X] T127 Generate JWT token in Google callback: include user_id, email, name, 7-day expiry
- [X] T128 Add state parameter validation in Google callback: verify state matches to prevent CSRF attacks
- [X] T129 Add error handling in Google OAuth flow: handle invalid code, network failures, API errors
- [X] T130 Store OAuth provider info in User model: add optional oauth_provider, oauth_id fields (requires migration)

### GitHub OAuth Implementation

- [X] T131 Create GET /api/auth/github/login endpoint in backend/app/routers/auth.py: generate OAuth authorization URL with state parameter
- [X] T132 Create GET /api/auth/github/callback endpoint: exchange authorization code for access token
- [X] T133 Implement GitHub user data fetch in callback: retrieve email, name, avatar from GitHub API
- [X] T134 Handle GitHub email privacy: if primary email is private, fetch verified email from /user/emails endpoint
- [X] T135 Implement user lookup/creation in GitHub callback: check if user exists by email, create if new user
- [X] T136 Generate JWT token in GitHub callback: include user_id, email, name, 7-day expiry
- [X] T137 Add state parameter validation in GitHub callback: verify state matches to prevent CSRF attacks
- [X] T138 Add error handling in GitHub OAuth flow: handle invalid code, network failures, API errors

### Database Schema Updates

- [X] T139 Update backend/app/models.py User model: add oauth_provider (optional string), oauth_id (optional string), profile_picture (optional string)
- [X] T140 Generate Alembic migration for OAuth fields: alembic revision --autogenerate -m "Add OAuth fields to users table"
- [X] T141 Review migration file: ensure nullable=True for oauth fields, add indexes on (oauth_provider, oauth_id) composite
- [ ] T142 Apply migration: alembic upgrade head (verify columns added in Neon Console)
- [X] T143 Update backend/app/schemas.py UserResponse: include oauth_provider, profile_picture in response model

### OAuth Security & Edge Cases

- [X] T144 Implement state token generation: use secrets.token_urlsafe(32), store in session/cache with 5-minute expiry
- [ ] T145 Add rate limiting to OAuth endpoints: prevent abuse of authorization redirect loops (Future enhancement - not implemented)
- [X] T146 Handle OAuth email conflicts: if OAuth email matches existing password-based account, link accounts (implemented in callbacks)
- [ ] T147 Add account linking prevention: if OAuth account exists with different provider, show "Email already registered with [provider]" error (Future enhancement)
- [X] T148 Validate OAuth redirect URIs: ensure callback URLs match configured OAUTH_REDIRECT_URI to prevent open redirects (implemented via authlib)

### Frontend Integration (Backend Response Format)

- [X] T149 Update OAuth callback endpoints to return: redirect to frontend with token in URL fragment (e.g., /auth/callback?token=xxx&provider=google)
- [X] T150 Add CORS configuration for OAuth callbacks: ensure frontend origin is allowed in callback responses (SessionMiddleware added)
- [X] T151 Document OAuth flow for frontend: provide API contract for /google/login, /google/callback, /github/login, /github/callback endpoints

### Testing OAuth Flows

- [ ] T152 Test Google OAuth with valid credentials: verify authorization redirect, callback token exchange, user creation/login (Manual testing required)
- [ ] T153 Test Google OAuth with invalid authorization code: verify 400 error "Invalid authorization code" (Error handling implemented)
- [ ] T154 Test Google OAuth with existing user email: verify user logged in (not duplicate account created) (Account linking implemented)
- [ ] T155 Test Google OAuth CSRF protection: verify invalid state parameter returns 400 error (CSRF protection implemented)
- [ ] T156 Test GitHub OAuth with valid credentials: verify authorization redirect, callback token exchange, user creation/login (Manual testing required)
- [ ] T157 Test GitHub OAuth with private email: verify email fetched from /user/emails endpoint (Private email handling implemented)
- [ ] T158 Test GitHub OAuth with existing user email: verify user logged in (not duplicate account created) (Account linking implemented)
- [ ] T159 Test GitHub OAuth CSRF protection: verify invalid state parameter returns 400 error (CSRF protection implemented)
- [ ] T160 Test OAuth email conflict scenario: create password account, attempt OAuth signin with same email, verify behavior per conflict strategy (Manual testing required)
- [ ] T161 Verify OAuth user data in database: check oauth_provider, oauth_id, profile_picture fields populated correctly (Manual testing required)

### Documentation

- [X] T162 Create backend/docs/oauth-setup.md: document how to obtain Google OAuth credentials from Google Cloud Console
- [X] T163 Update backend/docs/oauth-setup.md: document how to obtain GitHub OAuth credentials from GitHub Developer Settings (Combined in T162)
- [ ] T164 Update backend/README.md: add OAuth environment variables section with setup instructions
- [X] T165 Create API contract docs: document OAuth endpoints in specs/001-user-auth/contracts/oauth-google.md
- [X] T166 Create API contract docs: document OAuth endpoints in specs/001-user-auth/contracts/oauth-github.md

---

## Updated Dependencies & Execution Order

### Story Completion Order (with OAuth)

```
Phase 1 (Setup) → Phase 2 (Foundational)
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    Phase 3 (US1)  Phase 4 (US2)  Phase 5 (US5)
    [Signup - P1]  [Signin - P1]  [Isolation - P1]
         ↓             ↓             ↓
         └─────────────┼─────────────┘
                       ↓
                  Phase 6 (US3)
                  [Signout - P2]
                       ↓
                  Phase 7 (US4)
                  [Persistence - P2]
                       ↓
                  Phase 8 (Dashboard)
                       ↓
                  Phase 9 (Polish)
                       ↓
                  Phase 10 (OAuth)
                  [Google & GitHub - P2]
```

### Parallel Execution Opportunities (Phase 10)

- T118 (OAuth dependencies) || T119 (environment variables)
- T121 (Google config) || T122 (GitHub config)
- T123-T130 (Google OAuth flow) || T131-T138 (GitHub OAuth flow) — **Can implement Google and GitHub in parallel**
- T152-T155 (Google tests) || T156-T160 (GitHub tests)
- T162 (Google docs) || T163 (GitHub docs)
- T165 (Google contract) || T166 (GitHub contract)

**Benefit**: Google and GitHub OAuth can be implemented simultaneously by different developers

---

## Updated Task Summary

**Total Tasks**: 166 (previously 117)
**New OAuth Tasks**: 49 (T118-T166)
**Parallelizable OAuth Tasks**: 8-10 (marked with potential parallel execution)

**Estimated Effort (Phase 10 OAuth)**:
- OAuth Setup: 1 hour
- Google OAuth Implementation: 2-3 hours
- GitHub OAuth Implementation: 2-3 hours
- Database Migration: 1 hour
- Security & Edge Cases: 1-2 hours
- Testing: 2-3 hours
- Documentation: 1 hour
- **Phase 10 Total**: 10-14 hours

**Overall Project Total**: 28-40 hours (previously 18-26 hours)

**Story Breakdown (Updated)**:
- User Story 1 (Signup): 22 tasks (T021-T042)
- User Story 2 (Signin): 19 tasks (T043-T061)
- User Story 3 (Signout): 11 tasks (T080-T090)
- User Story 4 (Persistence): 11 tasks (T091-T101)
- User Story 5 (Isolation): 18 tasks (T062-T079)
- **OAuth Integration**: 49 tasks (T118-T166)
- Setup: 9 tasks (T001-T009)
- Foundational: 11 tasks (T010-T020)
- Dashboard: 5 tasks (T102-T106)
- Polish: 11 tasks (T107-T117)

---

**Task File Status**: ✅ UPDATED - OAuth tasks added (T118-T166)

**Next Command**: Begin OAuth implementation with Phase 10 tasks after completing Phases 1-9

**Suggested Commit Strategy**:
- Commit after each phase completion
- Example: "feat(auth): complete Phase 1 setup tasks (T001-T009)"
- Example: "feat(auth): complete User Story 1 signup (T021-T042)"
- Example: "feat(auth): add Google OAuth integration (T118-T130, T139-T143)"
- Example: "feat(auth): add GitHub OAuth integration (T131-T138)"
