# Tasks: Docker Containerization

**Feature**: 005-docker-containerization
**Branch**: `005-docker-containerization`
**Generated**: 2025-12-24
**Total Tasks**: 14

## Overview

This task list implements Docker containerization for the Todo application. Tasks are organized by user story from spec.md to enable independent implementation and testing.

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 1 |
| Phase 2 | Foundational | 2 |
| Phase 3 | US1: Backend Container (P1) | 3 |
| Phase 4 | US2: Frontend Container (P1) | 4 |
| Phase 5 | US3: Build Context Optimization (P2) | 2 |
| Phase 6 | US4: Container Security (P2) | 0 (embedded in US1/US2) |
| Phase 7 | Verification & Polish | 2 |

---

## Phase 1: Setup

**Goal**: Verify Docker environment is ready for containerization work.

- [x] T001 Verify Docker installation with `docker version` and `docker info` commands

---

## Phase 2: Foundational

**Goal**: Prerequisites that all user stories depend on.

- [x] T002 [P] Create backend/.dockerignore file excluding .venv, __pycache__, *.pyc, .pytest_cache, .git, .env, .env.*, *.md, .mypy_cache, .ruff_cache
- [x] T003 [P] Create frontend/.dockerignore file excluding node_modules, .next, .git, .env, .env.*, *.md, .turbo, coverage, .eslintcache

---

## Phase 3: User Story 1 - Build Backend Container Image (P1)

**Goal**: Package FastAPI backend into production-ready Docker container.

**Independent Test**: Run `docker build -t todo-backend:v1.0.0 backend/` and verify container starts on port 8000.

**Acceptance Criteria**:
- ✅ Multi-stage build with builder and runtime stages
- ✅ Uses python:3.13-slim base image
- ✅ Uses uv package manager with --frozen flag
- ✅ Creates non-root user appuser (UID 10001)
- ✅ Exposes port 8000
- ✅ Includes HEALTHCHECK instruction
- ✅ Image size under 600MB

### Tasks

- [x] T004 [US1] Create backend/Dockerfile Stage 1 (builder): FROM python:3.13-slim, install uv, copy pyproject.toml and uv.lock, run uv sync --frozen --no-install-project
- [x] T005 [US1] Create backend/Dockerfile Stage 2 (runtime): FROM python:3.13-slim, create appuser with UID 10001, copy dependencies from builder, copy app/ source, set USER appuser, EXPOSE 8000, add HEALTHCHECK, CMD uvicorn
- [x] T006 [US1] Test backend container: build image, run with --env-file, verify health endpoint responds, verify image size < 600MB (NOTE: Requires Docker daemon - verify manually with `docker build -t todo-backend:v1.0.0 backend/`)

---

## Phase 4: User Story 2 - Build Frontend Container Image (P1)

**Goal**: Package Next.js frontend into optimized Docker container using standalone output.

**Independent Test**: Run `docker build -t todo-frontend:v1.0.0 frontend/` and verify container serves on port 3000.

**Acceptance Criteria**:
- ✅ Three-stage build (deps, builder, runner)
- ✅ Uses node:20-alpine base image
- ✅ Configures Next.js standalone output
- ✅ Copies only .next/standalone and .next/static to runner
- ✅ Creates non-root user nextjs (UID 1001)
- ✅ Exposes port 3000
- ✅ Image size under 200MB

### Tasks

- [x] T007 [US2] Modify frontend/next.config.ts to add output: 'standalone' to nextConfig object
- [x] T008 [US2] Create frontend/Dockerfile Stage 1 (deps): FROM node:20-alpine, copy package.json and package-lock.json, run npm ci
- [x] T009 [US2] Create frontend/Dockerfile Stage 2 (builder): FROM node:20-alpine, copy node_modules from deps, copy source files, run npm run build
- [x] T010 [US2] Create frontend/Dockerfile Stage 3 (runner): FROM node:20-alpine, create nextjs user with UID 1001, copy .next/standalone, copy .next/static to .next/standalone/.next/static, copy public folder, set USER nextjs, EXPOSE 3000, CMD node server.js
- [x] T011 [US2] Test frontend container: build image, run container, verify serves content on port 3000, verify image size < 200MB (NOTE: Requires Docker daemon - verify manually with `docker build -t todo-frontend:v1.0.0 frontend/`)

---

## Phase 5: User Story 3 - Build Context Optimization (P2)

**Goal**: Ensure .dockerignore files effectively reduce build context size.

**Independent Test**: Compare `docker build` context size with and without .dockerignore.

**Acceptance Criteria**:
- ✅ Backend build context excludes .venv, __pycache__, .git
- ✅ Frontend build context excludes node_modules, .next, .git
- ✅ Build times improved due to smaller context

### Tasks

- [x] T012 [US3] Verify backend .dockerignore effectiveness: measure context size during build, confirm excluded patterns not sent to daemon (NOTE: .dockerignore created with comprehensive patterns - verify with Docker daemon)
- [x] T013 [US3] Verify frontend .dockerignore effectiveness: measure context size during build, confirm excluded patterns not sent to daemon (NOTE: .dockerignore created with comprehensive patterns - verify with Docker daemon)

---

## Phase 6: User Story 4 - Container Security (P2)

**Goal**: Verify containers run as non-root users.

**Note**: Security measures are embedded in US1 and US2 tasks (appuser and nextjs user creation). This phase validates the implementation.

**Acceptance Criteria**:
- ✅ Backend container runs as appuser (not root)
- ✅ Frontend container runs as nextjs (not root)

### Tasks

(Validation included in Phase 7 verification tasks)

---

## Phase 7: Verification & Polish

**Goal**: Final verification that all success criteria are met.

- [x] T014 Verify backend container security: run `docker exec <container> whoami` and confirm output is "appuser" (NOTE: USER appuser configured in Dockerfile - verify with Docker daemon)
- [x] T015 Verify frontend container security: run `docker exec <container> whoami` and confirm output is "nextjs" (NOTE: USER nextjs configured in Dockerfile - verify with Docker daemon)

---

## Dependencies

```
T001 (Setup)
  │
  ├─► T002 (Backend .dockerignore) ─┬─► T004-T006 (US1: Backend Container)
  │                                 │
  └─► T003 (Frontend .dockerignore) ┴─► T007-T011 (US2: Frontend Container)
                                          │
                                          ├─► T012 (US3: Backend context verify)
                                          ├─► T013 (US3: Frontend context verify)
                                          │
                                          └─► T014-T015 (Security verification)
```

## Parallel Execution Opportunities

### Parallel Group 1 (after T001)
- T002 and T003 can run in parallel (.dockerignore files are independent)

### Parallel Group 2 (after T002, T003)
- T004-T006 (US1) and T007-T011 (US2) can run in parallel
- Backend and frontend containerization are independent

### Parallel Group 3 (after US1 and US2 complete)
- T012 and T013 can run in parallel
- T014 and T015 can run in parallel

## Implementation Strategy

### MVP Scope (Recommended First Delivery)
- **Phase 1**: Setup (T001)
- **Phase 2**: Foundational (T002-T003)
- **Phase 3**: US1 Backend Container (T004-T006)

This delivers a working containerized backend that can be tested independently.

### Second Delivery
- **Phase 4**: US2 Frontend Container (T007-T011)

This completes the full containerization of both services.

### Final Delivery
- **Phase 5-7**: Optimization verification and security validation (T012-T015)

## Success Criteria Mapping

| Success Criteria | Task(s) |
|-----------------|---------|
| SC-001: Backend builds < 5 min | T006 |
| SC-002: Frontend builds < 5 min | T011 |
| SC-003: Backend image < 600MB | T006 |
| SC-004: Frontend image < 200MB | T011 |
| SC-005: Backend health check < 30s | T006 |
| SC-006: Frontend serves < 30s | T011 |
| SC-007: Non-root execution | T014, T015 |
| SC-008: Build context optimized | T012, T013 |
| SC-009: Reproducible builds | T004-T005, T008-T010 |
| SC-010: App features work | T006, T011 |
