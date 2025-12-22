# Tasks: Todo Web Application

**Input**: Design documents from `/specs/001-todo-web-app/`
**Prerequisites**: Authentication system (001-user-auth) must be complete

**Organization**: Tasks grouped by functionality (database, backend API, frontend UI)

## Format: `- [ ] [ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1: Database Schema

**Purpose**: Create Task model and database table

**Depends On**: 001-user-auth (User model must exist)

- [x] T001 Add Task model to backend/app/models.py with user_id foreign key
- [x] T002 Generate Alembic migration: `alembic revision --autogenerate -m "add tasks table"`
- [x] T003 Apply migration and verify tasks table created in Neon database
- [x] T004 Verify foreign key constraint between tasks.user_id and users.id
- [x] T005 Verify indexes created on user_id and (user_id, completed)

---

## Phase 2: Backend Task CRUD API

**Purpose**: Implement REST API endpoints for task management

**Depends On**: Phase 1 (Task model must exist)

### List Tasks Endpoint

- [x] T006 Create backend/app/routers/tasks.py with GET /{user_id}/tasks endpoint
- [x] T007 Implement list tasks logic: query tasks filtered by user_id from JWT
- [x] T008 Add JWT authentication to list tasks endpoint via verify_jwt dependency
- [x] T009 Verify user_id in URL matches JWT user_id (403 if mismatch)
- [x] T010 Return tasks ordered by created_at DESC

### Create Task Endpoint

- [x] T011 Add POST /{user_id}/tasks endpoint to backend/app/routers/tasks.py
- [x] T012 Create TaskCreate schema in backend/app/schemas.py (title, description)
- [x] T013 Implement create task logic: validate input, set user_id from JWT, save to database
- [x] T014 Add title validation: required, 1-200 characters, trimmed
- [x] T015 Add description validation: optional, max 1000 characters

### Update Task Endpoint

- [x] T016 Add PUT /{user_id}/tasks/{task_id} endpoint to tasks router
- [x] T017 Create TaskUpdate schema in backend/app/schemas.py
- [x] T018 Implement update task logic: verify ownership (user_id), update fields, return updated task
- [x] T019 Return 404 if task not found or doesn't belong to user

### Toggle Complete Endpoint

- [x] T020 Add PATCH /{user_id}/tasks/{task_id}/complete endpoint
- [x] T021 Implement toggle logic: flip completed boolean, update updated_at timestamp
- [x] T022 Return updated task with new completion status

### Delete Task Endpoint

- [x] T023 Add DELETE /{user_id}/tasks/{task_id} endpoint
- [x] T024 Implement delete logic: verify ownership, delete from database
- [x] T025 Return success message: "Task deleted successfully"

### Router Integration

- [x] T026 Include tasks router in backend/app/main.py: app.include_router(tasks_router, prefix="/api")
- [x] T027 Verify all task endpoints accessible via /api/{user_id}/tasks/*

---

## Phase 3: Frontend Dashboard & Task UI

**Purpose**: Create web interface for task management

**Depends On**: Phase 2 (Backend API must be ready)

### Dashboard Page

- [x] T028 Create frontend/app/dashboard/page.tsx as protected route
- [x] T029 Add authentication check: redirect to /auth/signin if no JWT token
- [x] T030 Implement task list fetching: GET /api/{user_id}/tasks on page load
- [x] T031 Display tasks in list format with title, description, completion status
- [x] T032 Show "No tasks yet" message when task list is empty
- [x] T033 Add loading state while fetching tasks

### Task Creation UI

- [x] T034 [P] Add "Add Task" button to dashboard
- [x] T035 Create task creation modal/form with title and description inputs
- [x] T036 Implement form validation: required title, max lengths
- [x] T037 Implement form submission: POST /api/{user_id}/tasks
- [x] T038 Add new task to UI optimistically (before API response)
- [x] T039 Show success/error messages for task creation

### Task Completion UI

- [x] T040 [P] Add checkbox to each task for completion toggle
- [x] T041 Implement toggle handler: PATCH /api/{user_id}/tasks/{id}/complete
- [x] T042 Update UI immediately on toggle (optimistic update)
- [x] T043 Add visual styling for completed tasks (strikethrough, dimmed)

### Task Edit UI

- [x] T044 [P] Add edit button to each task
- [x] T045 Create edit modal/form with pre-filled title and description
- [x] T046 Implement edit submission: PUT /api/{user_id}/tasks/{id}
- [x] T047 Update task in UI after successful edit

### Task Delete UI

- [x] T048 [P] Add delete button to each task
- [x] T049 Add confirmation dialog: "Are you sure you want to delete this task?"
- [x] T050 Implement delete handler: DELETE /api/{user_id}/tasks/{id}
- [x] T051 Remove task from UI after successful deletion

### UI Components

- [x] T052 [P] Create TaskCard component for displaying individual tasks
- [x] T053 [P] Create TaskForm component (reusable for create/edit)
- [x] T054 [P] Add responsive styling: mobile (375px) to desktop (1024px+)

---

## Phase 4: Integration & Testing

**Purpose**: End-to-end testing and user isolation verification

- [x] T055 Test complete flow: signup → dashboard → create task → view task
- [x] T056 Test task CRUD: create, read, update, delete via UI
- [x] T057 Test user isolation: create 2 users, verify User A cannot see User B's tasks
- [x] T058 Test URL manipulation: verify accessing /api/{other_user_id}/tasks returns 403
- [x] T059 Test mobile responsiveness: verify all UI works on 375px width
- [x] T060 Verify database constraints: foreign key, cascading delete when user deleted

---

## Dependencies & Execution Order

### Prerequisites
- **001-user-auth MUST be complete** before starting this feature
  - User model exists
  - JWT authentication working
  - Signup/signin functional

### Phase Order
1. **Phase 1 (Database)**: BLOCKS everything - must complete first
2. **Phase 2 (Backend API)**: BLOCKS Phase 3 - frontend needs API
3. **Phase 3 (Frontend UI)**: Can implement after Phase 2 complete
4. **Phase 4 (Testing)**: Final validation after all phases

### Parallel Work Opportunities
- Within Phase 2: Different endpoints can be built in parallel (T006-T010 can run with T011-T015)
- Within Phase 3: UI components can be built in parallel (T052-T054)

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Database | 5 | Task model and migrations |
| Phase 2: Backend API | 22 | CRUD endpoints implementation |
| Phase 3: Frontend UI | 27 | Dashboard and task management UI |
| Phase 4: Testing | 6 | Integration and isolation tests |
| **Total** | **60** | |

---

## Success Criteria

- [ ] All 60 tasks completed and tested
- [ ] Users can perform full CRUD on tasks via web UI
- [ ] User isolation verified (no cross-user data access)
- [ ] Mobile responsive on 375px minimum
- [ ] All API endpoints return proper error codes
