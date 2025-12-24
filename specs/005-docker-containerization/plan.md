# Implementation Plan: Docker Containerization

**Branch**: `005-docker-containerization` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-docker-containerization/spec.md`

## Summary

Create production-ready Docker containerization for the Todo application's backend (FastAPI) and frontend (Next.js). This involves multi-stage Dockerfiles optimized for size and security, .dockerignore files for build context management, and non-root user execution. The backend uses `uv` for Python dependency management with `python:3.13-slim` base image. The frontend uses Next.js standalone output with `node:20-alpine` base image.

## Technical Context

**Language/Version**: Python 3.13 (backend), Node.js 20 (frontend)
**Primary Dependencies**: Docker Engine 20.10+, uv (Python), npm (Node.js)
**Storage**: N/A (containerization layer - database access via environment variables)
**Testing**: Manual docker build/run verification, health check endpoint testing
**Target Platform**: Linux containers (Docker Desktop on Windows/Mac, native on Linux)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Build time < 5 minutes, startup time < 30 seconds
**Constraints**: Backend image < 600MB, Frontend image < 200MB, non-root execution
**Scale/Scope**: 2 Dockerfiles, 2 .dockerignore files, 1 next.config.ts modification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Container-Native Architecture | Multi-stage builds, non-root users | ✅ PASS |
| II. Spec-Driven Development | Spec complete before implementation | ✅ PASS |
| III. Test-First Development | Container tests defined in spec | ✅ PASS |
| VI. Clean Code Standards | Dockerfiles must be commented | ✅ WILL COMPLY |
| VII. Windows via WSL 2 or Docker Desktop | Docker Desktop acceptable | ✅ PASS |
| VIII. Data Security | No secrets in images | ✅ WILL COMPLY |
| XVII. Container-First Architecture | All FR-001 to FR-020 align | ✅ PASS |
| XVIII. Declarative Infrastructure | Dockerfiles are declarative | ✅ PASS |
| XIX. Immutable Infrastructure | Images are immutable artifacts | ✅ PASS |
| XXI. Health Checks | HEALTHCHECK instruction required | ✅ WILL COMPLY |

**Gate Result**: ✅ PASS - All principles satisfied or will be satisfied during implementation.

## Project Structure

### Documentation (this feature)

```text
specs/005-docker-containerization/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output - Docker best practices
├── data-model.md        # Phase 1 output - Dockerfile structure
├── quickstart.md        # Phase 1 output - Build/run commands
├── contracts/           # N/A for containerization
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── Dockerfile           # NEW: Multi-stage FastAPI container
├── .dockerignore        # NEW: Exclude .venv, __pycache__, etc.
├── pyproject.toml       # Existing: Dependencies for uv
├── uv.lock              # Existing: Lock file for reproducibility
└── app/                 # Existing: FastAPI application

frontend/
├── Dockerfile           # NEW: Multi-stage Next.js container
├── .dockerignore        # NEW: Exclude node_modules, .next, etc.
├── next.config.ts       # MODIFY: Add output: 'standalone'
├── package.json         # Existing: Dependencies
└── app/                 # Existing: Next.js application
```

**Structure Decision**: Web application structure (Option 2). Dockerfiles placed in their respective service directories (`backend/Dockerfile`, `frontend/Dockerfile`) following Docker convention. Each service has its own `.dockerignore` for independent build context management.

## Complexity Tracking

No constitution violations requiring justification. Implementation follows standard Docker patterns.

## Architecture Decision: Multi-Stage Build Strategy

### Backend (FastAPI)

```
Stage 1: builder
├── Base: python:3.13-slim
├── Install: uv package manager
├── Copy: pyproject.toml, uv.lock
└── Run: uv sync --frozen --no-install-project

Stage 2: runtime
├── Base: python:3.13-slim
├── Copy: Dependencies from builder
├── Copy: Application code
├── User: appuser (UID 10001)
├── Expose: 8000
├── Healthcheck: curl /health
└── CMD: uvicorn app.main:app
```

### Frontend (Next.js)

```
Stage 1: deps
├── Base: node:20-alpine
├── Copy: package.json, package-lock.json
└── Run: npm ci

Stage 2: builder
├── Base: node:20-alpine
├── Copy: Dependencies from deps
├── Copy: Source code
└── Run: npm run build

Stage 3: runner
├── Base: node:20-alpine
├── Copy: .next/standalone from builder
├── Copy: .next/static from builder
├── Copy: public folder
├── User: nextjs (UID 1001)
├── Expose: 3000
└── CMD: node server.js
```

## Environment Variables (Runtime Injection)

### Backend Required Variables
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for AI agent
- `BETTER_AUTH_SECRET` - JWT signing secret
- `BETTER_AUTH_URL` - Auth service URL

### Frontend Required Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL (for client-side)

## Security Considerations

1. **Non-root execution**: Both containers run as non-root users
2. **No secrets in images**: All sensitive data injected at runtime
3. **Minimal attack surface**: Multi-stage builds exclude build tools from runtime
4. **Slim base images**: Reduced CVE exposure with slim/alpine variants
5. **Specific image tags**: No `:latest` tags for reproducibility

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `backend/Dockerfile` | CREATE | Multi-stage FastAPI container |
| `backend/.dockerignore` | CREATE | Exclude Python artifacts |
| `frontend/Dockerfile` | CREATE | Multi-stage Next.js container |
| `frontend/.dockerignore` | CREATE | Exclude Node artifacts |
| `frontend/next.config.ts` | MODIFY | Add `output: 'standalone'` |

## Verification Commands

```bash
# Backend
cd backend
docker build -t todo-backend:v1.0.0 .
docker run -p 8000:8000 --env-file ../.env todo-backend:v1.0.0
curl http://localhost:8000/health

# Frontend
cd frontend
docker build -t todo-frontend:v1.0.0 .
docker run -p 3000:3000 todo-frontend:v1.0.0
curl http://localhost:3000

# Verify non-root
docker exec <container_id> whoami  # Should NOT be root

# Check image sizes
docker images | grep todo
```
