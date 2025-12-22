# Implementation Plan: Todo Web Application

**Feature**: 001-todo-web-app
**Created**: 2025-12-22
**Depends On**: 001-user-auth (authentication must be complete)

## Overview

Build a full-stack todo task management web application with CRUD operations, user isolation, and responsive UI.

## Architecture Decisions

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Database** | Neon PostgreSQL | Serverless, auto-scaling, already configured |
| **Backend ORM** | SQLModel | Type-safe, async support, integrates with FastAPI |
| **Backend Framework** | FastAPI | Async, auto-docs, matches existing auth system |
| **Frontend Framework** | Next.js 16 (App Router) | Server components, already in use |
| **Styling** | Tailwind CSS | Utility-first, matches existing UI |
| **State Management** | React useState | Simple enough, no global state needed |

### Database Design

**Task Table Schema**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_tasks_user_id` - Fast filtering by user
- `idx_tasks_user_completed` - Fast filtering by user and status

### API Design

**RESTful Endpoints**:
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion
- `DELETE /api/{user_id}/tasks/{id}` - Delete task

**Security**:
- JWT required on all endpoints
- user_id in URL must match JWT claim
- All queries filter by user_id

### Frontend Architecture

**Pages**:
- `/dashboard` - Main task management interface (protected route)

**Components**:
- `TaskCard` - Individual task display
- `TaskForm` - Create/edit task form
- `TaskList` - List of tasks with filtering

**State Flow**:
```
User Action → API Call → Optimistic UI Update → Server Response → Sync State
```

## Implementation Phases

### Phase 1: Database (Estimated: 30 min)
1. Add Task model to models.py
2. Generate Alembic migration
3. Apply migration to Neon database
4. Verify schema in database

### Phase 2: Backend API (Estimated: 2-3 hours)
1. Create tasks router
2. Implement list tasks endpoint
3. Implement create task endpoint
4. Implement update task endpoint
5. Implement toggle complete endpoint
6. Implement delete task endpoint
7. Add comprehensive error handling
8. Test all endpoints with Postman

### Phase 3: Frontend UI (Estimated: 3-4 hours)
1. Create dashboard page
2. Implement task fetching and display
3. Add task creation UI
4. Add task completion toggle
5. Add task edit functionality
6. Add task delete functionality
7. Add responsive styling
8. Test on mobile and desktop

### Phase 4: Testing & Polish (Estimated: 1-2 hours)
1. End-to-end testing
2. User isolation verification
3. Mobile responsiveness testing
4. Error handling verification
5. Documentation updates

## Key Files

### Backend
- `backend/app/models.py` - Task SQLModel
- `backend/app/routers/tasks.py` - Task CRUD endpoints
- `backend/app/schemas.py` - Request/response models
- `backend/alembic/versions/` - Database migration

### Frontend
- `frontend/app/dashboard/page.tsx` - Main dashboard
- `frontend/components/TaskCard.tsx` - Task display component
- `frontend/components/TaskForm.tsx` - Task create/edit form
- `frontend/lib/api-client.ts` - API calls (already exists)

## Dependencies

### External Dependencies (Already Installed)
- FastAPI, SQLModel, Alembic (backend)
- Next.js, React, Tailwind (frontend)
- Neon PostgreSQL (database)

### Internal Dependencies
- **REQUIRED**: 001-user-auth must be complete
  - User model exists
  - JWT authentication working
  - verify_jwt middleware available
- **BLOCKS**: 002-ai-chatbot (chatbot needs tasks to manage)

## Risk Mitigation

### Risk 1: User Isolation Breach
**Mitigation**:
- Always validate JWT user_id matches URL user_id
- All database queries filter by user_id
- Test with multiple users

### Risk 2: Performance with Many Tasks
**Mitigation**:
- Add database indexes
- Implement pagination if needed (future)
- Limit query results (e.g., most recent 100)

### Risk 3: Race Conditions on Concurrent Updates
**Mitigation**:
- Use database transactions
- Optimistic locking with updated_at timestamp
- Handle 409 Conflict responses

## Testing Strategy

### Unit Tests
- Task model validation
- Endpoint input validation
- JWT verification

### Integration Tests
- Create task → verify in database
- List tasks → verify user isolation
- Update task → verify changes persisted
- Delete task → verify removed from database

### User Isolation Tests
- User A creates task → User B cannot see it
- User A tries to access User B's task → 403 error
- URL manipulation with different user_id → blocked

## Success Metrics

- [ ] All CRUD operations functional via web UI
- [ ] Response times < 500ms for all endpoints
- [ ] Zero cross-user data leakage in testing
- [ ] Mobile responsive on 375px minimum width
- [ ] All error cases handled gracefully
