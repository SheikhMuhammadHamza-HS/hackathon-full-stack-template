# API Contract: Task CRUD Operations

**Feature**: 001-todo-web-app
**Endpoints**: Task management REST API

## Authentication

All endpoints require JWT authentication via Authorization header:
```
Authorization: Bearer <jwt_token>
```

Token must contain `user_id` claim matching the `{user_id}` in URL path.

---

## GET /api/{user_id}/tasks

List all tasks for authenticated user.

### Request

**Path Parameters**:
- `user_id` (string, required): User ID from JWT

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**: None

### Response

**Success (200 OK)**:
```json
[
  {
    "id": 1,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-22T10:30:00Z",
    "updated_at": "2025-12-22T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Call dentist",
    "description": null,
    "completed": true,
    "created_at": "2025-12-21T15:20:00Z",
    "updated_at": "2025-12-22T09:15:00Z"
  }
]
```

**Error (401 Unauthorized)**:
```json
{
  "detail": "Invalid or malformed token"
}
```

**Error (403 Forbidden)**:
```json
{
  "detail": "Access denied to this resource"
}
```

---

## POST /api/{user_id}/tasks

Create a new task.

### Request

**Path Parameters**:
- `user_id` (string, required): User ID from JWT

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Body Schema**:
- `title` (string, required): 1-200 characters
- `description` (string, optional): max 1000 characters

### Response

**Success (201 Created)**:
```json
{
  "id": 3,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-22T11:00:00Z",
  "updated_at": "2025-12-22T11:00:00Z"
}
```

**Error (400 Bad Request)**:
```json
{
  "detail": "Title is required"
}
```

**Error (401/403)**: Same as GET

---

## PUT /api/{user_id}/tasks/{task_id}

Update an existing task.

### Request

**Path Parameters**:
- `user_id` (string, required): User ID from JWT
- `task_id` (integer, required): Task ID to update

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description"
}
```

### Response

**Success (200 OK)**:
```json
{
  "id": 3,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": false,
  "created_at": "2025-12-22T11:00:00Z",
  "updated_at": "2025-12-22T11:30:00Z"
}
```

**Error (404 Not Found)**:
```json
{
  "detail": "Task not found"
}
```

---

## PATCH /api/{user_id}/tasks/{task_id}/complete

Toggle task completion status.

### Request

**Path Parameters**:
- `user_id` (string, required): User ID from JWT
- `task_id` (integer, required): Task ID to toggle

**Headers**:
```
Authorization: Bearer <jwt_token>
```

### Response

**Success (200 OK)**:
```json
{
  "id": 3,
  "completed": true,
  "updated_at": "2025-12-22T11:45:00Z"
}
```

**Error (404 Not Found)**:
```json
{
  "detail": "Task not found"
}
```

---

## DELETE /api/{user_id}/tasks/{task_id}

Delete a task permanently.

### Request

**Path Parameters**:
- `user_id` (string, required): User ID from JWT
- `task_id` (integer, required): Task ID to delete

**Headers**:
```
Authorization: Bearer <jwt_token>
```

### Response

**Success (200 OK)**:
```json
{
  "message": "Task deleted successfully"
}
```

**Error (404 Not Found)**:
```json
{
  "detail": "Task not found"
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this structure:
```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (task created) |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User trying to access another user's data |
| 404 | Not Found | Task doesn't exist |
| 500 | Internal Server Error | Database errors, unexpected failures |

### Security Notes

- Never reveal which field is wrong in validation errors (security)
- Always validate user_id from JWT matches URL path
- Sanitize error messages (no stack traces to client)
