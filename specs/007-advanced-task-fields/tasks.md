# Tasks: Advanced Task Fields

**Feature**: 007-advanced-task-fields
**Branch**: `007-advanced-task-fields`
**Generated**: 2025-12-25
**Total Tasks**: 15

## Overview

This task list implements advanced task management fields (priority, tags, due dates, recurring tasks) for Phase V. Tasks organized by user story from spec.md.

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 1 |
| Phase 2 | Foundational (Database) | 1 |
| Phase 3 | US1: Priority Management | 3 |
| Phase 4 | US2: Tag Organization | 3 |
| Phase 5 | US3: Due Dates | 3 |
| Phase 6 | US4: Recurring Tasks | 3 |
| Phase 7 | Polish & Validation | 1 |

---

## Phase 1: Setup

**Goal**: Verify database migration completed

- [x] T001 Verify database migration 1fdc137aba7b applied (priority, tags, due_date, is_recurring, recurring_interval columns exist)

---

## Phase 2: Foundational

**Goal**: Update Pydantic schemas for API validation

- [x] T002 Update TaskCreate schema in backend/app/schemas.py to include priority, tags, due_date, is_recurring, recurring_interval fields with validation

---

## Phase 3: User Story 1 - Priority Management (P1)

**Goal**: Enable users to set, filter, and sort tasks by priority

**Independent Test**: Create 3 tasks with different priorities, filter by High, verify only high-priority tasks display

**Acceptance Criteria**:
- ✅ Priority dropdown in task form
- ✅ Priority badge displays in task list
- ✅ Filter by priority works
- ✅ Sort by priority works

### Tasks

- [x] T003 [P] [US1] Add priority query parameter to GET /api/tasks endpoint in backend/app/api/routes/tasks.py
- [x] T004 [P] [US1] Add priority sorting to GET /api/tasks endpoint in backend/app/api/routes/tasks.py
- [x] T005 [US1] Add priority dropdown to task creation form in frontend/components/AddTaskForm.tsx

---

## Phase 4: User Story 2 - Tag Organization (P1)

**Goal**: Enable users to add tags and search/filter by tags

**Independent Test**: Create task with tags work,urgent, search tag=work, verify appears

**Acceptance Criteria**:
- ✅ Tags input in task form
- ✅ Tag chips display in task list
- ✅ Tag search works (case-insensitive)
- ✅ Click tag chip filters tasks

### Tasks

- [x] T006 [P] [US2] Add tags query parameter to GET /api/tasks endpoint for tag filtering in backend/app/api/routes/tasks.py
- [x] T007 [P] [US2] Add tags input field to task creation form in frontend/components/AddTaskForm.tsx
- [x] T008 [US2] Add tag chip display and click-to-filter in task list component in frontend/components/TaskItem.tsx and TaskList.tsx

---

## Phase 5: User Story 3 - Due Dates (P2)

**Goal**: Enable users to set due dates and see overdue indicators

**Independent Test**: Create task with due_date, verify displays in local timezone with overdue indicator if past

**Acceptance Criteria**:
- ✅ Due date/time picker in form
- ✅ Due date displays in local timezone
- ✅ Overdue indicator shows for past dates
- ✅ Sort/filter by due date works

### Tasks

- [x] T009 [P] [US3] Add due_date query parameters (sort, filter) to GET /api/tasks endpoint in backend/app/api/routes/tasks.py
- [x] T010 [P] [US3] Add due date/time picker to task creation form in frontend/components/AddTaskForm.tsx
- [x] T011 [US3] Add due date display with timezone conversion and overdue indicator in frontend/components/TaskItem.tsx

---

## Phase 6: User Story 4 - Recurring Tasks (P2)

**Goal**: Enable users to create recurring tasks (automation requires Dapr - future phase)

**Independent Test**: Create recurring task with interval=daily, verify is_recurring and recurring_interval saved correctly

**Acceptance Criteria**:
- ✅ Recurring checkbox and interval selector in form
- ✅ Recurring tasks display interval badge
- ✅ Validation: interval required if recurring=true

### Tasks

- [x] T012 [P] [US4] Add is_recurring and recurring_interval checkbox and dropdown to task creation form in frontend/components/AddTaskForm.tsx
- [x] T013 [P] [US4] Add recurring badge display in task list component in frontend/components/TaskItem.tsx
- [x] T014 [US4] Add validation logic for recurring_interval (required if is_recurring=true) in frontend/components/AddTaskForm.tsx

---

## Phase 7: Polish & Validation

**Goal**: Verify all features work end-to-end

- [x] T015 Run frontend build to verify no TypeScript errors, test all CRUD operations with new fields

---

## Dependencies

```
T001 (DB verify)
  │
  └─► T002 (Pydantic schemas)
        │
        ├─► T003-T005 (US1: Priority) ─────┐
        ├─► T006-T008 (US2: Tags) ─────────┤
        ├─► T009-T011 (US3: Due Dates) ────┤
        └─► T012-T014 (US4: Recurring) ────┤
                                           │
                                           └─► T015 (Validation)
```

## Parallel Execution Opportunities

### Group 1 (after T002)
- T003, T006, T009, T012 can run in parallel (different query params, independent)

### Group 2 (after T002)
- T004, T007, T010, T013 can run in parallel (different UI components)

### Group 3 (after Group 2)
- T005, T008, T011, T014 can run in parallel (different UI integration points)

## Implementation Strategy

### MVP Scope (P1 Stories Only)
- Phase 1-4: Priority + Tags (T001-T008)
- Delivers: Core organization features

### Second Delivery (P2 Stories)
- Phase 5-6: Due Dates + Recurring (T009-T014)
- Delivers: Scheduling features

### Final Delivery
- Phase 7: Polish (T015)

## Success Criteria Mapping

| Success Criteria | Task(s) |
|-----------------|---------|
| SC-001: Assign priority <10s | T005 |
| SC-002: Add tags <15s | T007 |
| SC-003: Priority filter <1s | T003 (with DB index from migration) |
| SC-004: Tag search <1s | T006 |
| SC-005: Set due date <20s | T010 |
| SC-006: Overdue indicator instant | T011 |
| SC-007: Recurring next instance <60s | Future (Dapr integration) |
| SC-009: 90% use priority first session | T005 (intuitive UI) |
| SC-010: Tag autocomplete <500ms | T007 (future enhancement) |
