# Quickstart: Todo Web Application

**Feature**: 001-todo-web-app
**Prerequisites**: Authentication system (001-user-auth) must be running

## Quick Start (5 minutes)

### 1. Ensure Authentication is Running

```bash
# Backend should be running on port 8000
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Frontend should be running on port 3000
cd frontend
npm run dev
```

### 2. Sign In

1. Open http://localhost:3000
2. Click "Sign In"
3. Enter your credentials
4. You'll be redirected to Dashboard

### 3. Test Task Operations

**Create Task**:
1. Click "Add Task" button
2. Enter title: "Buy groceries"
3. (Optional) Add description
4. Click "Create"
5. Task appears in list

**Mark Complete**:
1. Click checkbox next to task
2. Task gets strikethrough styling
3. Status saved to database

**Edit Task**:
1. Click edit icon on task
2. Modify title or description
3. Click "Save"
4. Changes appear immediately

**Delete Task**:
1. Click delete icon
2. Confirm deletion dialog
3. Task removed from list

## API Testing (Postman/cURL)

### List Tasks
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/YOUR_USER_ID/tasks
```

### Create Task
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "2 liters"}' \
  http://localhost:8000/api/YOUR_USER_ID/tasks
```

### Toggle Complete
```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/YOUR_USER_ID/tasks/1/complete
```

### Delete Task
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/YOUR_USER_ID/tasks/1
```

## Database Verification

### Check Tasks Table
```sql
-- Connect to Neon database
SELECT * FROM tasks ORDER BY created_at DESC;
```

### Verify User Isolation
```sql
-- Should only show tasks for specific user
SELECT * FROM tasks WHERE user_id = 'YOUR_USER_ID';
```

## Troubleshooting

### Tasks Not Showing
- **Check**: Is user authenticated? (JWT token in localStorage?)
- **Check**: Backend running on port 8000?
- **Check**: Console errors in browser DevTools?

### 403 Forbidden Error
- **Cause**: user_id in URL doesn't match JWT token
- **Fix**: Ensure you're using your own user_id from token

### 500 Internal Server Error
- **Check**: Database connection working?
- **Check**: Backend logs for error details
- **Check**: Task model has user_id field?

### Tasks Not Persisting
- **Check**: Database migration applied?
- **Check**: Tasks table exists in Neon?
- **Check**: Foreign key constraint on user_id?

## File Structure

```
specs/001-todo-web-app/
├── spec.md              # Feature requirements
├── data-model.md        # Task entity definition
├── plan.md              # Implementation strategy
├── tasks.md             # 60 implementation tasks
├── quickstart.md        # This file
├── contracts/
│   └── task-crud-api.md # API specifications
└── checklists/
    └── requirements.md  # Acceptance checklist
```

## Next Steps

After completing this feature:
1. Verify all tasks marked complete in tasks.md
2. Test user isolation with multiple accounts
3. Proceed to 002-ai-chatbot (AI-powered task management)
