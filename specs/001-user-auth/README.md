# User Authentication Specification

## Overview

This folder contains specifications for the **User Authentication System** - signup, signin, signout, OAuth, and JWT-based session management.

## Important Note

This specification contains **AUTHENTICATION ONLY**.

### What's Included (AUTH ONLY)
- User signup (email/password)
- User signin (email/password)
- OAuth (Google, GitHub)
- JWT token generation and validation
- Session persistence
- Signout functionality
- User model (id, email, name, password hash)

### What's NOT Included (See Other Specs)
- Task management → See `001-todo-web-app`
- Dashboard UI → See `001-todo-web-app`
- AI chatbot → See `002-ai-chatbot`

## Clarification on Existing Content

⚠️ **Historical Note**: The original `001-user-auth` specification included some full-stack application setup (monorepo structure, Task model, dashboard) because it was created as "Phase II" which bundled authentication with the web app foundation.

The **web application functionality** has now been properly extracted to `001-todo-web-app`.

When reading `001-user-auth` files, focus on:
- User Story 1: Signup
- User Story 2: Signin
- User Story 3: Signout
- User Story 4: Session Persistence
- OAuth implementation

Ignore references to:
- Task model (moved to 001-todo-web-app)
- Dashboard implementation (moved to 001-todo-web-app)
- Task CRUD endpoints (moved to 001-todo-web-app)

## Files in This Specification

| File | Purpose | Notes |
|------|---------|-------|
| `spec.md` | User stories and requirements | Focus on auth-related stories |
| `data-model.md` | User entity definition | User model only |
| `plan.md` | Implementation architecture | JWT, Better Auth decisions |
| `tasks.md` | Implementation tasks | Focus on auth tasks (T001-T101) |
| `quickstart.md` | Setup guide | Auth setup only |
| `contracts/signup.md` | Signup API spec | ✅ Auth only |
| `contracts/signin.md` | Signin API spec | ✅ Auth only |
| `contracts/signout.md` | Signout API spec | ✅ Auth only |
| `contracts/oauth-*.md` | OAuth flow specs | ✅ Auth only |

## Dependencies

**External**:
- Neon PostgreSQL database
- Better Auth library
- Google/GitHub OAuth providers

**Provides to Other Features**:
- User model (used by 001-todo-web-app, 002-ai-chatbot)
- JWT authentication (verify_jwt middleware)
- User session management

## Status

✅ **IMPLEMENTED** - Authentication system is functional

## Quick Navigation

- [View Full Specification](./spec.md)
- [Implementation Tasks](./tasks.md)
- [Architecture Plan](./plan.md)
- [API Contracts](./contracts/)
- [Quick Start Guide](./quickstart.md)
