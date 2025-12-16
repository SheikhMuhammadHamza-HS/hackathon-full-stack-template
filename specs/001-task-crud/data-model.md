# Data Model: Todo Console Application

## Task Entity

### Fields
- **id** (int, required): Unique identifier for the task, auto-incremented starting from 1
- **title** (str, required): Task title with 1-200 character limit
- **description** (str, optional): Task description with max 1000 characters
- **completed** (bool, required): Completion status, defaults to False
- **created_at** (str, required): Creation timestamp in ISO format (YYYY-MM-DDTHH:MM:SS.ssssss)

### Validation Rules
- `id`: Must be unique positive integer
- `title`: Required, 1-200 characters, cannot be empty or whitespace only
- `description`: Optional, max 1000 characters if provided
- `completed`: Must be boolean value
- `created_at`: Must be valid ISO format timestamp

### State Transitions
- `completed` field can transition from False ↔ True through toggle operation
- Task can transition from active (in storage) to deleted (removed from storage)

## In-Memory Storage Structure

### Global Task Storage
```python
tasks = [
    {
        "id": int,
        "title": str,
        "description": str,
        "completed": bool,
        "created_at": str  # ISO format timestamp
    },
    ...
]
```

### Storage Requirements
- Maintain insertion order for creation date sorting
- Provide efficient lookup by ID (O(1) preferred, O(n) acceptable for Phase I)
- Support all CRUD operations (Create, Read, Update, Delete)
- Maintain uniqueness of task IDs

## Task Operations Data Flow

### Add Task
1. Validate title length (1-200 chars)
2. Validate description length (≤1000 chars if provided)
3. Generate unique ID (max existing ID + 1)
4. Set completion status to False
5. Set creation timestamp to current time
6. Append to tasks list

### View Tasks
1. Return all tasks sorted by created_at (newest first)
2. Format for console display with ID, title, status indicator, and date

### Update Task
1. Validate task ID exists
2. Validate new title if provided (1-200 chars)
3. Validate new description if provided (≤1000 chars)
4. Update only provided fields
5. Preserve other fields unchanged

### Delete Task
1. Validate task ID exists
2. Remove task from storage list
3. Return confirmation

### Toggle Completion
1. Validate task ID exists
2. Toggle completed field value (True ↔ False)
3. Return updated status