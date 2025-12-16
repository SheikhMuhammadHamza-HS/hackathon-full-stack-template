# Implementation Tasks: Todo CRUD Operations

**Feature**: Todo CRUD Operations
**Branch**: `001-task-crud`
**Created**: 2025-12-16
**Input**: Feature specification from `/specs/001-task-crud/spec.md`

## Implementation Strategy

This implementation follows a spec-driven approach with tasks organized by user story priority. The strategy focuses on delivering an MVP with the first user story (Add Task) first, then incrementally adding functionality for other user stories. Each user story is implemented with its required components (models, services, UI) and can be tested independently.

## Dependencies

- **User Story 1 (Add Task)**: Foundation for all other operations
- **User Story 2 (View Tasks)**: Independent, can be implemented after US1
- **User Story 3 (Update Task)**: Depends on US1 and US2
- **User Story 4 (Delete Task)**: Depends on US1 and US2
- **User Story 5 (Mark Complete)**: Depends on US1 and US2

## Parallel Execution Examples

- **US1 Components**: `validation.py`, `storage.py`, and `tasks.py` functions can be developed in parallel
- **US2 Components**: Menu system and view formatting can be developed in parallel with other US components
- **US3/US4/US5**: Each can be developed in parallel after foundational components exist

---

## Phase 1: Setup

### Goal
Initialize project structure and foundational components required for all user stories.

### Independent Test
Project structure matches implementation plan and basic imports work without errors.

### Tasks

- [X] T001 Create project directory structure per implementation plan in src/, tests/, and root files
- [X] T002 Create pyproject.toml with Python 3.13+ requirement and basic project metadata
- [X] T003 Create README.md with setup and usage instructions from quickstart guide
- [X] T004 Create src/__init__.py to make src a Python package
- [X] T005 [P] Create empty src/main.py file with basic Python shebang and imports
- [X] T006 [P] Install and configure UV package manager for Python dependency management

---

## Phase 2: Foundational Components

### Goal
Create foundational components that all user stories depend on: task model, storage, and validation.

### Independent Test
All foundational components can be imported and basic validation functions work correctly.

### Tasks

- [X] T007 Create src/storage.py with global tasks list and basic storage operations
- [X] T008 Create src/validation.py with all required validation functions per spec
- [X] T009 [P] Define Task data structure and constants in src/tasks.py
- [X] T010 [P] Create basic menu structure in src/main.py
- [X] T011 Test that all foundational components can be imported without errors

---

## Phase 3: User Story 1 - Add New Todo Task (Priority: P1)

### Goal
Implement the ability for users to add new tasks with title and optional description.

### Independent Test
Can add a task with a valid title and description, then verify it appears in the task list with a unique ID and creation timestamp.

### Acceptance Scenarios
1. Given I am using the todo console app, When I enter a valid title and optional description, Then a new task is created with a unique ID and timestamp, and a success message displays the task ID.
2. Given I am using the todo console app, When I enter a title that is empty or too long (>200 chars), Then an error message is displayed and no task is created.

### Tasks

- [X] T012 [US1] Implement add_task function in src/tasks.py with validation
- [X] T013 [US1] Implement input collection for add task in src/main.py
- [X] T014 [US1] Implement success message display for add task in src/main.py
- [X] T015 [US1] Implement error handling for invalid title in src/tasks.py
- [X] T016 [US1] Implement error handling for invalid description in src/tasks.py
- [X] T017 [US1] Test adding task with valid title and description
- [X] T018 [US1] Test error handling with empty title
- [X] T019 [US1] Test error handling with title over 200 characters
- [X] T020 [US1] Test error handling with description over 1000 characters

---

## Phase 4: User Story 2 - View All Todo Tasks (Priority: P1)

### Goal
Implement the ability for users to view all tasks in a readable format.

### Independent Test
Can add tasks and then view them in a readable format with ID, title, status, and creation date sorted by newest first.

### Acceptance Scenarios
1. Given I have added one or more tasks, When I request to view all tasks, Then all tasks are displayed in a readable format with ID, title, status (✓ or ✗), and creation date sorted by newest first.
2. Given I have no tasks in the system, When I request to view all tasks, Then a message "No tasks found. Add your first task!" is displayed.

### Tasks

- [X] T021 [US2] Implement get_all_tasks function in src/tasks.py
- [X] T022 [US2] Implement format_tasks_for_display function in src/tasks.py
- [X] T023 [US2] Implement view tasks menu option in src/main.py
- [X] T024 [US2] Implement display logic for empty task list in src/main.py
- [X] T025 [US2] Implement proper sorting by creation date in src/tasks.py
- [X] T026 [US2] Test viewing tasks after adding multiple tasks
- [X] T027 [US2] Test viewing empty task list
- [X] T028 [US2] Test that tasks are sorted by newest first

---

## Phase 5: User Story 5 - Mark Task as Complete/Incomplete (Priority: P1)

### Goal
Implement the ability for users to toggle the completion status of tasks.

### Independent Test
Can toggle the completion status of a task and verify the status changes when viewing the task list.

### Acceptance Scenarios
1. Given I have an existing task, When I provide a valid task ID to toggle completion status, Then the task's completed status is toggled (True ↔ False) and the new status is displayed.
2. Given I provide an invalid or non-existent task ID, When I attempt to toggle completion status, Then an error message "Task with ID {id} does not exist" is displayed and no status change occurs.

### Tasks

- [X] T029 [US5] Implement toggle_task_completion function in src/tasks.py
- [X] T030 [US5] Implement input collection for task ID in src/main.py
- [X] T031 [US5] Implement success message display for toggle operation in src/main.py
- [X] T032 [US5] Implement error handling for non-existent task ID in src/tasks.py
- [X] T033 [US5] Test toggling completion status of existing task
- [X] T034 [US5] Test error handling with non-existent task ID
- [X] T035 [US5] Test that toggle properly switches between True and False

---

## Phase 6: User Story 3 - Update Existing Todo Task (Priority: P2)

### Goal
Implement the ability for users to update existing tasks' title and/or description.

### Independent Test
Can update an existing task's title or description and verify the changes are reflected when viewing the task.

### Acceptance Scenarios
1. Given I have an existing task, When I provide a valid task ID and new title/description, Then the task is updated with the new information and the updated details are displayed.
2. Given I provide an invalid or non-existent task ID, When I attempt to update a task, Then an error message "Task with ID {id} does not exist" is displayed and no changes are made.

### Tasks

- [X] T036 [US3] Implement update_task function in src/tasks.py
- [X] T037 [US3] Implement input collection for update in src/main.py
- [X] T038 [US3] Implement success message display for update in src/main.py
- [X] T039 [US3] Implement validation for updated title and description in src/tasks.py
- [X] T040 [US3] Implement error handling for non-existent task ID in src/tasks.py
- [X] T041 [US3] Test updating task title only
- [X] T042 [US3] Test updating task description only
- [X] T043 [US3] Test updating both title and description
- [X] T044 [US3] Test error handling with non-existent task ID

---

## Phase 7: User Story 4 - Delete Todo Task (Priority: P2)

### Goal
Implement the ability for users to delete tasks with confirmation.

### Independent Test
Can delete a task and verify it no longer appears in the task list.

### Acceptance Scenarios
1. Given I have an existing task, When I provide a valid task ID and confirm deletion, Then the task is removed from the system and a success message is displayed.
2. Given I provide an invalid or non-existent task ID, When I attempt to delete a task, Then an error message "Task with ID {id} does not exist" is displayed and no task is deleted.

### Tasks

- [X] T045 [US4] Implement delete_task function in src/tasks.py
- [X] T046 [US4] Implement confirmation prompt for deletion in src/main.py
- [X] T047 [US4] Implement success message display for deletion in src/main.py
- [X] T048 [US4] Implement error handling for non-existent task ID in src/tasks.py
- [X] T049 [US4] Implement cancellation handling for deletion in src/main.py
- [X] T050 [US4] Test successful deletion with confirmation
- [X] T051 [US4] Test deletion cancellation
- [X] T052 [US4] Test error handling with non-existent task ID

---

## Phase 8: Polish & Cross-Cutting Concerns

### Goal
Complete the application with proper error handling, menu flow, and edge case handling.

### Independent Test
Application handles all edge cases gracefully without crashing and provides clear navigation for all operations.

### Tasks

- [X] T053 Implement comprehensive error handling for invalid menu selections in src/main.py
- [X] T054 Implement proper exit handling in src/main.py
- [X] T055 Add proper docstrings to all functions following Google style
- [X] T056 Implement handling for non-integer task ID inputs in all operations
- [X] T057 Test all error scenarios from specification: very long title, non-existent tasks, empty list
- [X] T058 Test complete workflow: add, view, update, mark complete, delete tasks
- [X] T059 Perform final code review for PEP 8 compliance and clean code principles
- [X] T060 Update README.md with complete usage examples
- [X] T061 Final integration test of all user stories working together

## MVP Scope

The minimum viable product includes:
- Phase 1: Setup
- Phase 2: Foundational Components
- Phase 3: Add Task functionality (US1)
- Phase 4: View Tasks functionality (US2)
- Phase 5: Mark Complete/Incomplete functionality (US5)

This provides a complete, testable application with the core functionality users need.

---

## Phase 9: Enhanced UI with Rich and Questionary

### Goal
Improve the terminal user interface using rich and questionary libraries for better visual experience and user interaction.

### Independent Test
Application displays enhanced UI with rich formatting, colors, and interactive prompts while maintaining all existing functionality.

### Tasks

- [ ] T062 Install rich and questionary dependencies using UV: `uv add rich questionary`
- [ ] T063 Update pyproject.toml to include rich and questionary dependencies
- [ ] T064 Import rich and questionary in main.py
- [ ] T065 Replace basic print statements with rich console formatting
- [ ] T066 Enhance menu display with rich formatting and colors
- [ ] T067 Use questionary for improved input collection and validation
- [ ] T068 Replace basic input() calls with questionary prompts
- [ ] T069 Enhance task display with rich table formatting
- [ ] T070 Add rich styling to error messages and success messages
- [ ] T071 Test enhanced UI functionality maintains all existing behavior

## Enhancement Scope

The UI enhancement phase includes:
- Installing rich and questionary libraries
- Improving visual presentation with tables, colors, and formatting
- Enhancing user interaction with better prompts and validation
- Maintaining all existing functionality while improving user experience