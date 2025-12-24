---
id: "0001"
title: "Docker Containerization Spec"
stage: spec
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-docker-containerization
branch: 005-docker-containerization
user: SheikhMuhammadHamza
command: /sp.specify
labels: ["docker", "containerization", "phase-iv", "dockerfile", "multi-stage-build"]
links:
  spec: specs/005-docker-containerization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-docker-containerization/spec.md
  - specs/005-docker-containerization/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

@Docker Agent (or System: Act as the Docker & Containerization Specialist)

We are executing Phase IV. Your task is to implement the **Containerization** layer.

## Your Goal
Create production-ready `Dockerfile`s and `.dockerignore` files for both Frontend and Backend.

## Strict Implementation Rules

### 1. Backend (FastAPI)
- **File:** `backend/Dockerfile`
- **Technique:** Multi-stage build.
- **Dependency Manager:** You MUST use `uv`.
  - Copy `pyproject.toml` and `uv.lock`.
  - Run `uv sync --frozen --no-install-project`.
- **Base Image:** `python:3.13-slim`.
- **Security:** Create and run as user `appuser`.
- **Port:** Expose 8000.

### 2. Frontend (Next.js)
- **File:** `frontend/Dockerfile`
- **Technique:** Multi-stage build (deps → builder → runner).
- **Optimization (CRITICAL):**
  - First, edit `frontend/next.config.ts` (or .js) and add `output: 'standalone'` inside the config object.
  - In the Dockerfile, copy ONLY the `.next/standalone` folder and `.next/static` folder to the runner stage.
- **Base Image:** `node:20-alpine`.
- **Security:** Create and run as user `nextjs`.
- **Port:** Expose 3000.

### 3. Context Management
- **File:** Create `.dockerignore` in root (or per service).
- **Exclude:** `node_modules`, `.venv`, `.git`, `.next`, `__pycache__`, `.env`.

## Response snapshot

Created comprehensive specification for Phase IV Docker containerization:

1. **Branch Created**: `005-docker-containerization`
2. **Spec File**: `specs/005-docker-containerization/spec.md`

**Specification Includes**:
- 4 User Stories (P1-P2 priority)
  - Backend container image build (P1)
  - Frontend container image build (P1)
  - Build context optimization (P2)
  - Container security hardening (P2)
- 20 Functional Requirements covering:
  - Backend Dockerfile (FR-001 to FR-009)
  - Frontend Dockerfile (FR-010 to FR-017)
  - Context management (FR-018 to FR-020)
- 10 Success Criteria (measurable outcomes)
- Edge cases and error handling scenarios
- Assumptions and out-of-scope items

**Quality Checklist**: All 12 validation items passed.

## Outcome

- ✅ Impact: Created complete specification for Docker containerization layer
- 🧪 Tests: N/A (specification phase)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, then `/sp.tasks` for task breakdown
- 🧠 Reflection: User provided detailed requirements - no clarifications needed

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist - PASS (12/12 items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
