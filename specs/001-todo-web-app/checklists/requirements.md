# Requirements Checklist: Todo Web Application

**Feature**: 001-todo-web-app

## Functional Requirements

### Task Display
- [x] Dashboard displays all user's tasks
- [x] Tasks show title, description, completion status
- [x] Tasks sorted by creation date (newest first)
- [x] Empty state message when no tasks exist

### Task Creation
- [x] "Add Task" button available on dashboard
- [x] Task creation form with title (required) and description (optional)
- [x] Title validation: 1-200 characters
- [x] Description validation: max 1000 characters
- [x] Task appears in list immediately after creation

### Task Completion
- [x] Checkbox to toggle task completion
- [x] Visual indicator for completed tasks (strikethrough/dimmed)
- [x] Completion status persists to database

### Task Editing
- [x] Edit button on each task
- [x] Edit form pre-filled with current values
- [x] Changes saved to database
- [x] UI updates immediately after edit

### Task Deletion
- [x] Delete button on each task
- [x] Confirmation dialog before deletion
- [x] Task removed from UI and database

## Security Requirements

### Authentication
- [x] All task endpoints require JWT token
- [x] Dashboard redirects to signin if not authenticated
- [x] JWT token validated on every request

### User Isolation
- [x] Users only see their own tasks
- [x] API blocks access to other users' tasks (403 error)
- [x] Database queries filter by user_id
- [x] URL manipulation with different user_id is blocked

## API Requirements

### Endpoints
- [x] GET /api/{user_id}/tasks - List tasks
- [x] POST /api/{user_id}/tasks - Create task
- [x] PUT /api/{user_id}/tasks/{id} - Update task
- [x] PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion
- [x] DELETE /api/{user_id}/tasks/{id} - Delete task

### Error Handling
- [x] 400 for validation errors
- [x] 401 for missing/invalid JWT
- [x] 403 for accessing other user's data
- [x] 404 for non-existent tasks
- [x] 500 for server errors (with user-friendly messages)

## Database Requirements

### Schema
- [x] Tasks table created via Alembic migration
- [x] user_id foreign key to users table
- [x] Indexes on user_id for performance
- [x] Timestamps auto-managed

### Data Integrity
- [x] Foreign key constraint enforced
- [x] Cascade delete when user is deleted
- [x] No orphaned tasks

## UI/UX Requirements

### Responsiveness
- [x] Works on mobile (375px minimum)
- [x] Works on tablet (768px)
- [x] Works on desktop (1024px+)

### User Experience
- [x] Loading states during API calls
- [x] Error messages displayed clearly
- [x] Optimistic UI updates (instant feedback)
- [x] Confirmation dialogs for destructive actions

### Accessibility
- [x] Keyboard navigation works
- [x] Touch targets ≥ 44x44px on mobile
- [x] Clear visual feedback for interactions

## Testing Requirements

### Manual Testing
- [x] Create task via UI - appears in list
- [x] Mark task complete - visual update + persisted
- [x] Edit task - changes saved
- [x] Delete task - removed from list
- [x] Sign out and back in - tasks persist

### User Isolation Testing
- [x] Create 2 users
- [x] User A adds tasks
- [x] User B cannot see User A's tasks
- [x] Attempting to access other user's tasks via URL returns 403

### Integration Testing
- [x] Complete flow: signup → dashboard → create task → CRUD operations
- [x] Session persistence across page reloads
- [x] Mobile testing on 375px width

## Documentation Requirements

- [x] spec.md - Feature requirements
- [x] data-model.md - Task entity definition
- [x] plan.md - Implementation architecture
- [x] tasks.md - Task breakdown
- [x] quickstart.md - Setup and testing guide
- [x] contracts/task-crud-api.md - API specifications

## Success Criteria

- [x] All functional requirements met
- [x] All security requirements enforced
- [x] All API endpoints working
- [x] All UI requirements implemented
- [x] Zero user isolation breaches
- [x] All tests passing
