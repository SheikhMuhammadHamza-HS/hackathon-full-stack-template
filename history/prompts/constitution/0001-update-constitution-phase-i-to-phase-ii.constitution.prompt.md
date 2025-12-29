---
id: 0001
title: Update Constitution Phase I to Phase II
stage: constitution
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: system
command: /sp.constitution
labels: ["constitution", "phase-transition", "architecture", "security", "full-stack"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - Manual review of constitution principles
 - Template alignment verification
---

## Prompt

You are updating the Constitution file from Phase I to Phase II of the Todo application hackathon project.

## Context
Phase I (Console App) is complete. Now transitioning to Phase II: Full-Stack Web Application with persistent storage and multi-user authentication.

## What Changed from Phase I to Phase II

### Technology Evolution
**Phase I:**
- Python console app
- In-memory storage (dict/list)
- Single user
- No authentication
- Local execution only

**Phase II:**
- Full-stack web application
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- Database: Neon Serverless PostgreSQL
- Multi-user with Better Auth (JWT)
- Deployed on cloud (Vercel + Render)

### Architecture Changes
**Phase I:** Simple console interface → in-memory storage
**Phase II:** Web UI (Next.js) → REST API (FastAPI) → Database (Neon PostgreSQL)

### New Requirements for Phase II
1. **Multi-user support** - Each user has isolated data
2. **Authentication** - Better Auth with JWT tokens
3. **Persistent storage** - Neon PostgreSQL database
4. **REST API** - 6 endpoints with proper security
5. **Responsive UI** - Mobile and desktop support
6. **Monorepo structure** - Frontend and Backend in same repo
7. **Security** - JWT verification on all endpoints, user isolation
8. **Deployment** - Frontend on Vercel, Backend on cloud

## Your Task

Update the Constitution file to include:

### 1. Phase II Purpose
Why we're moving from console to web (scalability, accessibility, real-world app)

### 2. Updated Core Principles
- Spec-Driven Development (still mandatory)
- User isolation and data security (NEW)
- RESTful API design (NEW)
- Authentication-first approach (NEW)
- Mobile-first responsive design (NEW)
- Cloud-native deployment (NEW)
- Keep: Clean code, proper structure

### 3. New Technical Standards
**Backend Standards:**
- FastAPI conventions
- SQLModel for ORM
- Pydantic for validation
- JWT middleware for all routes
- User_id filtering on all queries
- Proper HTTP status codes
- Error handling with HTTPException

**Frontend Standards:**
- Next.js App Router patterns
- TypeScript required
- Tailwind CSS (core classes only)
- Server components by default
- API calls via centralized client
- No localStorage for state (React state only)
- Better Auth integration

**Database Standards:**
- SQLModel models
- Foreign key relationships
- Indexes for performance
- Timestamps on all tables
- User_id on all user data tables

### 4. Architecture Constraints for Phase II
- Monorepo structure (frontend + backend)
- REST API between frontend and backend
- JWT tokens for authentication
- Neon PostgreSQL only (no other DB)
- No localStorage/sessionStorage in artifacts
- All state in database or React state
- Better Auth for user management
- User isolation enforced at API level

### 5. Security Principles (NEW Section)
- Every API endpoint requires JWT token
- Token user_id must match URL {user_id}
- Users can only access their own data
- Shared BETTER_AUTH_SECRET between frontend and backend
- No sensitive data in URLs
- Prepared statements only (SQLModel handles this)
- CORS configured for frontend domain only

### 6. Data Model Rules (Updated)
**User Structure (Managed by Better Auth):**
- id: string (primary key)
- email: string (unique)
- name: string
- created_at: timestamp

**Task Structure:**
- id: integer (auto-generated)
- user_id: string (foreign key to users.id)
- title: string (1-200 chars, required)
- description: string (max 1000 chars, optional)
- completed: boolean (default false)
- created_at: timestamp
- updated_at: timestamp

**Validation Rules:**
- Title: required, 1-200 chars
- Description: optional, max 1000 chars
- User_id: must exist in users table
- All queries filtered by authenticated user_id

[Additional sections 7-13 omitted for brevity - see full prompt in command args]

## Output Format

Generate an updated Constitution file that:
- Clearly states this is Phase II (Full-Stack Web Application)
- Maintains Phase I principles that still apply
- Adds new principles for web, API, database, auth, deployment
- Provides clear guidance for multi-service architecture
- Emphasizes security and user isolation
- Remains actionable for AI agents

The Constitution should guide agents to build a secure, scalable, multi-user web application that serves as the foundation for Phase III (AI Chatbot).

Make it clear what changed from Phase I and why. Help agents understand the bigger picture.

## Response snapshot

Constitution successfully updated from version 1.0.0 to 2.0.0 (MAJOR version change).

**Key Changes:**

1. **Phase Transition Context Added**: Clear explanation of why Phase II exists and how it builds on Phase I fundamentals.

2. **Principles Updated (7 existing + 5 new = 12 total)**:
   - Principle I: "Learning Foundation First" → "Production-Ready Web Architecture"
   - Principle II: "Spec-Driven Development" (UNCHANGED - still non-negotiable)
   - Principle III: "Test-First Development" → Adapted for full-stack testing (API, multi-user, responsive)
   - Principle IV: "Data Model Integrity" → Expanded for relational database with user isolation
   - Principle V: "Input Validation and Error Handling" → Expanded for API layer validation
   - Principle VI: "Clean Code Standards" → Now covers both Python/FastAPI and TypeScript/Next.js
   - Principle VII: "Windows via WSL 2 Only" (UNCHANGED)
   - Principle VIII: "User Isolation and Data Security" (NEW - NON-NEGOTIABLE)
   - Principle IX: "RESTful API Design" (NEW)
   - Principle X: "Authentication-First Approach" (NEW)
   - Principle XI: "Mobile-First Responsive Design" (NEW)
   - Principle XII: "Cloud-Native Deployment" (NEW)

3. **Scope Redefined**: Now includes full-stack architecture, multi-user auth, persistent database, REST API, responsive UI, and cloud deployment.

4. **Technology Constraints Expanded**: Added Next.js, FastAPI, SQLModel, Alembic, Better Auth, Vercel, Render, Neon PostgreSQL.

5. **Project Structure Updated**: Monorepo structure with frontend/ and backend/ directories, shared specs/ and history/.

6. **Success Criteria Expanded**: Now includes functional, API, frontend, backend, database, security, documentation, testing, deployment, and code quality criteria.

7. **Compliance Section Enhanced**: Added Compliance Review Checklist with 10 specific checkpoints for Phase II.

**File Updated**: `.specify/memory/constitution.md`

**Templates Status**: No updates needed - existing templates (spec, plan, tasks) are generic and already support multi-service architectures.

**Sync Impact Report**: Added as HTML comment at top of constitution file documenting all changes.

## Outcome

- ✅ Impact: Constitution successfully transitioned from Phase I (console app) to Phase II (full-stack web app) with MAJOR version change (1.0.0 → 2.0.0). All principles updated or added to support multi-user, authenticated, cloud-deployed web application.
- 🧪 Tests: Manual verification of principle coherence, template alignment check (spec, plan, tasks templates confirmed generic and compatible).
- 📁 Files: Modified 1 file (.specify/memory/constitution.md). Created 1 PHR (this file).
- 🔁 Next prompts: Run `/sp.specify` to create Phase II feature specification for the full-stack todo web app, followed by `/sp.plan` for implementation planning.
- 🧠 Reflection: The constitution now provides clear guidance for building production-ready, multi-user web applications with security-first principles. The transition context helps agents understand why Phase II exists and how it builds on Phase I fundamentals.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update completed successfully with all placeholders filled and principles clearly articulated.
- Graders run and results (PASS/FAIL): Manual review PASS - all principles are actionable, measurable, and aligned with Phase II requirements.
- Prompt variant (if applicable): Standard /sp.constitution workflow with comprehensive Phase II context provided.
- Next experiment (smallest change to try): Consider adding ADR template updates to explicitly reference new security and API principles for architecturally significant decisions.
