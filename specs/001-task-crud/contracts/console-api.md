# Console Interface Contract: Todo Application

## Overview
This contract defines the console interface for the todo application, specifying the user interactions, input/output formats, and error handling patterns.

## Menu Interface

### Main Menu Options
```
Todo Application
===============
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Exit
Choose an option (1-6):
```

## Operation Contracts

### 1. Add Task
**Input Flow:**
```
Enter task title (1-200 characters): [user input]
Enter task description (optional, max 1000 characters, press Enter to skip): [user input or Enter]
```

**Success Output:**
```
Task added successfully! ID: {task_id}
```

**Error Outputs:**
- Title empty: `Error: Title cannot be empty`
- Title too long: `Error: Title must be 200 characters or less`
- Description too long: `Error: Description must be 1000 characters or less`

### 2. View All Tasks
**Input Flow:**
```
# No input required
```

**Success Output:**
```
All Tasks:
Total: {count}
ID  | Title                 | Status | Created
----|-----------------------|--------|------------------
1   | Sample task title     | ✓      | 2025-12-16 10:30:00
2   | Another task          | ✗      | 2025-12-16 10:29:45

# If no tasks:
No tasks found. Add your first task!
```

### 3. Update Task
**Input Flow:**
```
Enter task ID to update: [user input]
Enter new title (leave empty to keep current): [user input or Enter]
Enter new description (leave empty to keep current): [user input or Enter]
```

**Success Output:**
```
Task {task_id} updated successfully:
Title: {new_title}
Description: {new_description}
```

**Error Outputs:**
- Task not found: `Error: Task with ID {id} does not exist`
- Invalid ID: `Error: Please enter a valid task ID`

### 4. Delete Task
**Input Flow:**
```
Enter task ID to delete: [user input]
Are you sure you want to delete task {id}? (Y/N): [user input]
```

**Success Output:**
```
Task {task_id} deleted successfully!
```

**Error Outputs:**
- Task not found: `Error: Task with ID {id} does not exist`
- Invalid confirmation: `Deletion cancelled.`

### 5. Mark Task Complete/Incomplete
**Input Flow:**
```
Enter task ID to toggle completion: [user input]
```

**Success Output:**
```
Task {task_id} marked as {completed/incomplete}!
```

**Error Outputs:**
- Task not found: `Error: Task with ID {id} does not exist`

### 6. Exit
**Input Flow:**
```
# No input required
```

**Success Output:**
```
Thank you for using the Todo Application. Goodbye!
```

## Error Handling Contract

### Input Validation
All user inputs must be validated according to these rules:
- Task titles: 1-200 characters, non-empty
- Task descriptions: 0-1000 characters
- Task IDs: positive integers that exist in the system
- Menu selections: integers 1-6
- Confirmation: 'Y', 'y', 'N', or 'n'

### Error Message Format
```
Error: [descriptive message]
[Additional guidance if needed]
```

## Data Format Contract

### Task Object
```json
{
  "id": integer,
  "title": string,
  "description": string,
  "completed": boolean,
  "created_at": "YYYY-MM-DD HH:MM:SS"  // Display format
}
```

### Storage Format (Internal)
```python
tasks = [
    {
        "id": int,
        "title": str,
        "description": str,
        "completed": bool,
        "created_at": datetime  // ISO format internally
    },
    ...
]
```

## Session Behavior
- All data stored in-memory only
- Data lost when application exits
- No persistence between sessions
- All operations atomic within session