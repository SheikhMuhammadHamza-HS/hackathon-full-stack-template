# Feature Specification: Todo CRUD Operations

**Feature Branch**: `001-task-crud`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "create a comprehensive specifications with based om the constitution file # Context
- Phase: I (In-Memory Python Console App)
- Storage: In-memory (Python dict/list)
- Interface: Console/Terminal only
- Features: Basic Level (5 features)


### 1. Feature Overview
Brief description of CRUD operations for todo tasks

### 2. User Stories
Write user stories for each operation:
- As a user, I want to add a task...
- As a user, I want to view all tasks...
- As a user, I want to update a task...
- As a user, I want to delete a task...
- As a user, I want to mark a task complete...

### 3. Acceptance Criteria

#### Add Task
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Auto-generate unique ID
- Auto-set created_at timestamp
- Default completed = False
- Validate inputs before adding
- Display success message with task ID

#### View Tasks
- Show all tasks in readable format
- Display: ID, title, status (✓ or ✗), created date
- Show total count
- Handle empty list gracefully ("No tasks found")
- Sort by creation date (newest first)

#### Update Task
- User provides task ID
- Allow changing title and/or description
- Validate task ID exists
- Validate new inputs
- Update only provided fields
- Display updated task details

#### Delete Task
- User provides task ID
- Validate task ID exists
- Confirm deletion (Y/N)
- Remove from memory
- Display success message

#### Mark as Complete
- User provides task ID
- Validate task ID exists
- Toggle completed status (True ↔ False)
- Display new status

### 4. Input Validation Rules
- Title: non-empty, max 200 chars
- Description: max 1000 chars
- Task ID: must be integer, must exist
- Handle invalid inputs gracefully with error messages

### 5. Error Scenarios
- Task ID not found → "Task with ID {id} does not exist"
- Empty title → "Title cannot be empty"
- Invalid ID format → "Please enter a valid task ID"
- No tasks to display → "No tasks found. Add your first task!"

### 6. Data Structure
Define task object structure in memory:
```python
task = {
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": datetime
}
```

### 7. Console Output Examples
Show expected console output for each operation:
- Add task output
- View tasks output (list format)
- Update confirmation
- Delete confirmation
- Toggle complete confirmation

### 8. Edge Cases
- Adding task with very long title
- Updating non-existent task
- Deleting already deleted task
- Viewing empty list
- Invalid menu choices

## Output Requirements
- Clear, actionable specifications
- No ambiguity - implementation should be straightforward
- Include examples for clarity
- Focus on console interface constraints
- Ensure specifications align with Phase I limitations (in-memory only)

Generate the complete specification file now."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add New Todo Task (Priority: P1)

As a user, I want to add a new task to my todo list so that I can keep track of things I need to do.

**Why this priority**: This is the foundational capability that enables all other operations. Without the ability to add tasks, the todo application has no value.

**Independent Test**: Can be fully tested by adding a task with a title and description, then verifying it appears in the task list with a unique ID and creation timestamp.

**Acceptance Scenarios**:

1. **Given** I am using the todo console app, **When** I enter a valid title and optional description, **Then** a new task is created with a unique ID and timestamp, and a success message displays the task ID.

2. **Given** I am using the todo console app, **When** I enter a title that is empty or too long (>200 chars), **Then** an error message is displayed and no task is created.

---

### User Story 2 - View All Todo Tasks (Priority: P1)

As a user, I want to view all my tasks so that I can see what I need to do and track my progress.

**Why this priority**: This is a core functionality that users need to interact with their tasks. Without viewing capabilities, the application cannot serve its primary purpose.

**Independent Test**: Can be fully tested by adding tasks and then viewing them in a readable format with ID, title, status, and creation date sorted by newest first.

**Acceptance Scenarios**:

1. **Given** I have added one or more tasks, **When** I request to view all tasks, **Then** all tasks are displayed in a readable format with ID, title, status (✓ or ✗), and creation date sorted by newest first.

2. **Given** I have no tasks in the system, **When** I request to view all tasks, **Then** a message "No tasks found. Add your first task!" is displayed.

---

### User Story 3 - Update Existing Todo Task (Priority: P2)

As a user, I want to update a task so that I can modify its title or description as needed.

**Why this priority**: This allows users to maintain accurate information in their todo list, which is essential for ongoing productivity.

**Independent Test**: Can be fully tested by updating an existing task's title or description and verifying the changes are reflected when viewing the task.

**Acceptance Scenarios**:

1. **Given** I have an existing task, **When** I provide a valid task ID and new title/description, **Then** the task is updated with the new information and the updated details are displayed.

2. **Given** I provide an invalid or non-existent task ID, **When** I attempt to update a task, **Then** an error message "Task with ID {id} does not exist" is displayed and no changes are made.

---

### User Story 4 - Delete Todo Task (Priority: P2)

As a user, I want to delete a task so that I can remove items that are no longer needed.

**Why this priority**: This allows users to keep their todo list clean and relevant by removing completed or obsolete tasks.

**Independent Test**: Can be fully tested by deleting a task and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** I have an existing task, **When** I provide a valid task ID and confirm deletion, **Then** the task is removed from the system and a success message is displayed.

2. **Given** I provide an invalid or non-existent task ID, **When** I attempt to delete a task, **Then** an error message "Task with ID {id} does not exist" is displayed and no task is deleted.

---

### User Story 5 - Mark Task as Complete/Incomplete (Priority: P1)

As a user, I want to mark a task as complete or incomplete so that I can track my progress.

**Why this priority**: This is a core functionality that enables users to manage their task status and track completion, which is fundamental to todo applications.

**Independent Test**: Can be fully tested by toggling the completion status of a task and verifying the status changes when viewing the task list.

**Acceptance Scenarios**:

1. **Given** I have an existing task, **When** I provide a valid task ID to toggle completion status, **Then** the task's completed status is toggled (True ↔ False) and the new status is displayed.

2. **Given** I provide an invalid or non-existent task ID, **When** I attempt to toggle completion status, **Then** an error message "Task with ID {id} does not exist" is displayed and no status change occurs.

---

### Edge Cases

- Adding a task with a title longer than 200 characters should result in an error message
- Updating a task that has already been deleted should show an appropriate error message
- Attempting to delete a task that has already been deleted should show an appropriate error message
- Viewing an empty task list should gracefully display "No tasks found. Add your first task!"
- Entering an invalid menu choice should display an error and return to the main menu
- Entering a non-integer value when a task ID is required should result in an appropriate error message
- Adding a task with a very long description (over 1000 characters) should be validated

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to add new tasks with a required title (1-200 characters) and optional description (max 1000 characters)
- **FR-002**: System MUST auto-generate a unique ID for each new task
- **FR-003**: System MUST auto-set a creation timestamp when a new task is added
- **FR-004**: System MUST set the default completion status to False for new tasks
- **FR-005**: System MUST validate input before adding tasks (title length, description length)
- **FR-006**: System MUST display a success message with the task ID after successful task creation
- **FR-007**: System MUST display all tasks in a readable format with ID, title, status (✓ or ✗), and creation date
- **FR-008**: System MUST sort tasks by creation date in descending order (newest first)
- **FR-009**: System MUST show the total count of tasks when displaying the list
- **FR-010**: System MUST handle empty task lists gracefully with a "No tasks found" message
- **FR-011**: System MUST allow users to update existing tasks by providing a valid task ID
- **FR-012**: System MUST validate that the task ID exists before attempting to update
- **FR-013**: System MUST allow updating title and/or description fields independently
- **FR-014**: System MUST display updated task details after successful update
- **FR-015**: System MUST require user confirmation before deleting a task
- **FR-016**: System MUST validate that the task ID exists before attempting to delete
- **FR-017**: System MUST remove the task from memory after successful deletion
- **FR-018**: System MUST display a success message after successful task deletion
- **FR-019**: System MUST allow users to toggle the completion status of tasks by providing a valid task ID
- **FR-020**: System MUST validate that the task ID exists before attempting to toggle completion status
- **FR-021**: System MUST display the new completion status after toggling
- **FR-022**: System MUST handle invalid input gracefully by displaying appropriate error messages
- **FR-023**: System MUST validate that task IDs are integers when required
- **FR-024**: System MUST store all data in-memory only (no persistent storage)
- **FR-025**: System MUST provide a console/terminal interface only (no GUI)

### Key Entities

- **Task**: Represents a single todo item with id, title, description, completion status, and creation timestamp
  - id: Unique integer identifier for the task
  - title: Required string (1-200 characters) representing the task name
  - description: Optional string (max 1000 characters) with additional task details
  - completed: Boolean flag indicating whether the task is completed (True/False)
  - created_at: Timestamp indicating when the task was created

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task in under 30 seconds with appropriate validation and error handling
- **SC-002**: All tasks are displayed in a readable format with clear status indicators (✓ or ✗) and sorted by creation date
- **SC-003**: Users can successfully perform all CRUD operations (Create, Read, Update, Delete) on tasks with appropriate confirmation and error messages
- **SC-004**: All input validation works correctly with appropriate error messages for invalid inputs (title length, description length, invalid task IDs)
- **SC-005**: The system handles all edge cases gracefully without crashing or producing unexpected behavior
- **SC-006**: All data remains in memory during the application session and is accessible through the console interface
- **SC-007**: The console interface provides clear navigation and feedback for all operations