# Data Model: Docker Containerization

**Feature**: 005-docker-containerization
**Date**: 2025-12-24

## Overview

This feature does not introduce traditional database entities. Instead, it defines **infrastructure artifacts** (Dockerfiles, .dockerignore files) that package existing application code into container images.

## Artifact Model

### 1. Backend Dockerfile

**Location**: `backend/Dockerfile`

**Structure**:
```
┌─────────────────────────────────────────┐
│ Stage: builder                          │
├─────────────────────────────────────────┤
│ Base Image: python:3.13-slim            │
│ Working Dir: /app                       │
│ Installed: uv package manager           │
│ Copied: pyproject.toml, uv.lock         │
│ Action: uv sync --frozen                │
└─────────────────────────────────────────┘
                    │
                    ▼ (COPY dependencies)
┌─────────────────────────────────────────┐
│ Stage: runtime                          │
├─────────────────────────────────────────┤
│ Base Image: python:3.13-slim            │
│ Working Dir: /app                       │
│ User: appuser (UID 10001)               │
│ Copied: /app from builder               │
│ Copied: app/ source code                │
│ Exposed: Port 8000                      │
│ Healthcheck: curl /health               │
│ Entrypoint: uvicorn app.main:app        │
└─────────────────────────────────────────┘
```

**Validation Rules**:
- Base image MUST be `python:3.13-slim`
- User MUST NOT be root
- Port MUST be 8000
- HEALTHCHECK MUST be present

### 2. Frontend Dockerfile

**Location**: `frontend/Dockerfile`

**Structure**:
```
┌─────────────────────────────────────────┐
│ Stage: deps                             │
├─────────────────────────────────────────┤
│ Base Image: node:20-alpine              │
│ Working Dir: /app                       │
│ Copied: package.json, package-lock.json │
│ Action: npm ci                          │
└─────────────────────────────────────────┘
                    │
                    ▼ (COPY node_modules)
┌─────────────────────────────────────────┐
│ Stage: builder                          │
├─────────────────────────────────────────┤
│ Base Image: node:20-alpine              │
│ Working Dir: /app                       │
│ Copied: node_modules from deps          │
│ Copied: All source files                │
│ Action: npm run build                   │
└─────────────────────────────────────────┘
                    │
                    ▼ (COPY .next/standalone)
┌─────────────────────────────────────────┐
│ Stage: runner                           │
├─────────────────────────────────────────┤
│ Base Image: node:20-alpine              │
│ Working Dir: /app                       │
│ User: nextjs (UID 1001)                 │
│ Copied: .next/standalone from builder   │
│ Copied: .next/static from builder       │
│ Copied: public/ folder                  │
│ Exposed: Port 3000                      │
│ Entrypoint: node server.js              │
└─────────────────────────────────────────┘
```

**Validation Rules**:
- Base image MUST be `node:20-alpine`
- MUST use 3-stage build (deps, builder, runner)
- Runner MUST only contain standalone output
- User MUST NOT be root
- Port MUST be 3000

### 3. Backend .dockerignore

**Location**: `backend/.dockerignore`

**Excluded Patterns**:
| Pattern | Reason |
|---------|--------|
| `.venv/` | Local virtual environment |
| `__pycache__/` | Python bytecode cache |
| `*.pyc` | Compiled Python files |
| `.pytest_cache/` | Test cache |
| `.git/` | Version control |
| `.env` | Environment secrets |
| `.env.*` | Environment variants |
| `*.md` | Documentation |
| `tests/` | Test files (optional) |
| `.mypy_cache/` | Type checker cache |
| `.ruff_cache/` | Linter cache |

### 4. Frontend .dockerignore

**Location**: `frontend/.dockerignore`

**Excluded Patterns**:
| Pattern | Reason |
|---------|--------|
| `node_modules/` | Dependencies (reinstalled in container) |
| `.next/` | Build output (rebuilt in container) |
| `.git/` | Version control |
| `.env` | Environment secrets |
| `.env.*` | Environment variants |
| `*.md` | Documentation |
| `.turbo/` | Turborepo cache |
| `coverage/` | Test coverage |
| `.eslintcache` | Linter cache |

### 5. Next.js Configuration Change

**Location**: `frontend/next.config.ts`

**Modification**:
```typescript
// Add to nextConfig object:
output: 'standalone'
```

**Effect**: Enables standalone output mode that creates a minimal server.js with only required dependencies.

## State Transitions

### Docker Image Lifecycle

```
Source Code
    │
    ▼ (docker build)
Docker Image (immutable)
    │
    ▼ (docker run)
Container (running instance)
    │
    ├─── Healthy (health check passes)
    │
    └─── Unhealthy (health check fails)
            │
            ▼ (auto-restart or manual intervention)
        Container (restarted)
```

### Build Context Flow

```
Repository Files
    │
    ▼ (apply .dockerignore)
Filtered Build Context
    │
    ▼ (send to Docker daemon)
Build Process
    │
    ▼ (multi-stage build)
Final Image
```

## Relationships

```
┌──────────────────┐     ┌──────────────────┐
│ backend/         │     │ frontend/        │
│ Dockerfile       │     │ Dockerfile       │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ todo-backend     │     │ todo-frontend    │
│ :v1.0.0 image    │     │ :v1.0.0 image    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │    ┌───────────────────┘
         │    │
         ▼    ▼
┌──────────────────────────────────────────┐
│           Docker Network                  │
│  (containers communicate via service     │
│   names in Kubernetes/docker-compose)    │
└──────────────────────────────────────────┘
```
