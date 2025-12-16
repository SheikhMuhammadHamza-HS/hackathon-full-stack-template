# Quickstart Guide: Todo Console Application

## Prerequisites
- Python 3.13 or higher
- Windows users: WSL 2 with Ubuntu (as required by constitution)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Verify Python version**
   ```bash
   python --version
   # Should show Python 3.13 or higher
   ```

3. **Navigate to project directory**
   ```bash
   cd phase1-console  # or your project root directory
   ```

## Running the Application

1. **Execute the main application**
   ```bash
   python src/main.py
   ```

2. **Follow the on-screen menu prompts**
   - Use number options to select operations
   - Follow specific prompts for each operation

## Basic Operations

### Adding a Task
1. Select "Add Task" from main menu
2. Enter task title (1-200 characters)
3. Optionally enter task description (max 1000 characters)
4. Task will be created with unique ID and timestamp

### Viewing Tasks
1. Select "View All Tasks" from main menu
2. All tasks will be displayed with:
   - Task ID
   - Title
   - Status (✓ for completed, ✗ for incomplete)
   - Creation date

### Updating a Task
1. Select "Update Task" from main menu
2. Enter the task ID to update
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)

### Deleting a Task
1. Select "Delete Task" from main menu
2. Enter the task ID to delete
3. Confirm deletion with 'Y' or cancel with 'N'

### Marking Complete/Incomplete
1. Select "Mark Task Complete/Incomplete" from main menu
2. Enter the task ID to toggle
3. Status will be toggled (completed ↔ incomplete)

## Error Handling

The application handles these common error scenarios:
- Invalid task IDs (not found)
- Empty or too-long titles
- Invalid menu selections
- Invalid confirmation responses

Error messages will guide you on how to correct the input.

## Development

### File Structure
- `src/main.py` - Main application loop and menu system
- `src/tasks.py` - Task CRUD operations
- `src/storage.py` - In-memory storage management
- `src/validation.py` - Input validation functions

### Adding New Features
1. Update specification (spec.md) first
2. Update this plan (plan.md) if needed
3. Create new tasks in tasks.md
4. Implement following the existing code patterns