# Todo Web Application Specification

## Overview

This folder contains specifications for the **Todo Web Application** feature - the core task management functionality of the application.

## Important Note

This specification was **extracted from 001-user-auth** to properly separate concerns:

- **001-user-auth**: Authentication ONLY (signup, signin, signout, OAuth, JWT)
- **001-todo-web-app**: Task management ONLY (CRUD operations, dashboard, task UI)
- **002-ai-chatbot**: AI-powered chat interface for task management

## What's Included

### Core Functionality
- Task CRUD operations (Create, Read, Update, Delete)
- Dashboard UI for task management
- Task completion toggling
- User-scoped task filtering
- Responsive UI (mobile to desktop)

### Technical Components

**Backend**:
- Task model (SQLModel)
- Task CRUD API endpoints
- Database migration for tasks table
- User isolation enforcement

**Frontend**:
- Dashboard page (`/dashboard`)
- Task list display
- Task creation/edit forms
- Task delete confirmation
- Responsive styling

## Files in This Specification

| File | Purpose |
|------|---------|
| `spec.md` | User stories and requirements |
| `data-model.md` | Task entity definition and schema |
| `plan.md` | Implementation architecture and decisions |
| `tasks.md` | 60 implementation tasks |
| `quickstart.md` | Setup and testing guide |
| `contracts/task-crud-api.md` | REST API specifications |
| `checklists/requirements.md` | Acceptance criteria checklist |

## Dependencies

**Prerequisites**:
- 001-user-auth MUST be complete (User model, JWT authentication)
- Neon PostgreSQL database configured
- Backend and frontend monorepo structure in place

**Blocks**:
- 002-ai-chatbot depends on this feature (AI manages tasks)

## Status

✅ **IMPLEMENTED** - All tasks complete, feature is functional

## Quick Navigation

- [View Full Specification](./spec.md)
- [Implementation Tasks](./tasks.md)
- [Architecture Plan](./plan.md)
- [API Contracts](./contracts/task-crud-api.md)
- [Quick Start Guide](./quickstart.md)
