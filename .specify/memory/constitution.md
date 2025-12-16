<!--
Sync Impact Report:
- Version Change: None → 1.0.0
- New Principles Added: 7 principles for Phase I
- Removed Sections: None (initial version)
- Templates Requiring Updates:
  ✅ plan-template.md (Constitution Check section aligns with Phase I principles)
  ✅ spec-template.md (Requirements sections align with Phase I functional requirements)
  ✅ tasks-template.md (Task structure supports test-first approach)
- Follow-up TODOs: None (all placeholders filled for Phase I context)
-->

# Phase I Todo Console Application Constitution

## Core Principles

### I. Learning Foundation First

Phase I exists to establish fundamental programming patterns before introducing complexity. This phase uses in-memory storage (Python dict/list) and console interface exclusively to focus on core business logic, data structures, and clean code practices. Database integration, web interfaces, and advanced features are explicitly out of scope.

**Rationale**: Building a solid foundation in basic CRUD operations, data validation, and error handling provides the necessary skills for more complex phases. Starting simple prevents overwhelm and ensures mastery of fundamentals.

**Rules**:
- Storage MUST use only Python built-in data structures (dict, list)
- Interface MUST be console-only (stdin/stdout)
- NO external dependencies except Python standard library
- NO database, NO web framework, NO GUI libraries

### II. Spec-Driven Development (NON-NEGOTIABLE)

All code MUST be preceded by written specifications. No implementation may begin without approved spec.md, plan.md, and tasks.md files. This prevents "vibe-coding" (coding without clear requirements) and ensures every line of code has documented purpose and acceptance criteria.

**Rationale**: Spec-driven development catches design flaws early, provides clear success criteria, and creates documentation as a natural byproduct of development. This is essential training for professional software development.

**Rules**:
- Specification (spec.md) MUST exist before plan.md
- Implementation plan (plan.md) MUST exist before tasks.md
- Task list (tasks.md) MUST exist before any code
- Code changes MUST reference specific task IDs
- Claude Code MUST be used for all code generation (no manual coding)

### III. Test-First Development

Tests MUST be written before implementation code. For Phase I, tests are defined as executable scenarios in the console that demonstrate each feature working correctly. Each task MUST include "How to Test" steps that can be executed manually in the console.

**Rationale**: Test-first development forces clear thinking about expected behavior, provides immediate feedback, and prevents regression. Manual console testing is appropriate for Phase I's learning objectives.

**Rules**:
- Each task MUST include specific test steps
- Test steps MUST fail before implementation
- Test steps MUST pass after implementation
- All five CRUD operations MUST be testable via console
- Error cases MUST have defined test scenarios

### IV. Data Model Integrity

Task data structure MUST maintain consistency and type safety. Each task is a dictionary with defined required and optional fields. The in-memory storage MUST preserve referential integrity (e.g., task IDs remain unique, completed status is boolean).

**Rationale**: Even in-memory data requires clear structure. This principle establishes database thinking without database complexity, preparing for Phase II migration.

**Rules**:
- Task structure MUST be documented in spec.md
- Required fields: `id` (int), `title` (str), `completed` (bool)
- Optional fields: `description` (str), `created_at` (str ISO format)
- Task IDs MUST be unique and auto-incremented
- In-memory storage MUST be a global list of task dictionaries
- NO persistence between program runs (explicitly documented behavior)

### V. Input Validation and Error Handling

All user input MUST be validated before processing. Errors MUST be handled gracefully with clear, user-friendly messages. The application MUST NOT crash from invalid input.

**Rationale**: Proper error handling is a fundamental software quality attribute. Learning to validate input and handle errors gracefully in Phase I establishes patterns for all future phases.

**Rules**:
- Validate all user inputs before processing
- Empty task titles MUST be rejected with clear message
- Invalid task IDs MUST be handled gracefully
- Invalid menu choices MUST prompt for correct input
- Error messages MUST be user-friendly (no stack traces shown to users)
- Use try-except blocks for all user input processing

### VI. Clean Code and Python Standards

Code MUST follow Python conventions (PEP 8) and clean code principles. Functions MUST be small, focused, and well-named. Code MUST be readable without excessive comments.

**Rationale**: Clean code is maintainable code. Learning professional code standards in Phase I prevents bad habits and prepares for team collaboration.

**Rules**:
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Functions MUST do one thing and do it well
- Maximum function length: 20 lines (excluding docstrings)
- Descriptive variable names (no single letters except loop counters)
- Docstrings for all functions (Google style)
- No global variables except the task storage list

### VII. Windows via WSL 2 Only

Windows users MUST use Windows Subsystem for Linux (WSL 2) with Ubuntu. Direct Windows execution is not supported for this project.

**Rationale**: WSL 2 provides a consistent Linux environment, eliminating platform-specific issues and aligning with professional development practices where Linux is standard.

**Rules**:
- Windows development MUST occur in WSL 2
- WSL 2 MUST have Python 3.13+ installed
- UV package manager MUST be installed in WSL 2 environment
- File paths MUST use Linux conventions within WSL

## Scope and Constraints

### In Scope (Phase I)
- Five basic CRUD operations: Add, Delete, Update, View, Complete
- Console menu interface for user interaction
- In-memory task storage using Python data structures
- Input validation and error handling
- Manual console testing procedures
- Clean, documented Python code following PEP 8

### Out of Scope (Future Phases)
- Database persistence (Phase II)
- Web interface (Phase III)
- User authentication (Phase III)
- AI chat interface (Phase III)
- Advanced features (filtering, search, tags)
- Automated unit tests (learning manual testing first)
- Multiple users
- Task priorities or categories

### Technology Constraints
- Python 3.13 or higher REQUIRED
- UV package manager for Python dependency management
- Python standard library ONLY (no external packages)
- WSL 2 for Windows users

## Project Structure

Phase I MUST follow this exact directory structure:

```
phase1-console/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # This file
│   └── templates/                   # SpecKit Plus templates
├── specs/
│   └── todo-console/
│       ├── spec.md                  # Feature specification
│       ├── plan.md                  # Implementation plan
│       └── tasks.md                 # Task breakdown
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entry point with menu loop
│   ├── tasks.py                     # Task CRUD operations
│   ├── storage.py                   # In-memory storage management
│   └── validation.py                # Input validation functions
├── history/
│   └── prompts/                     # Prompt History Records
├── README.md                        # Setup and usage instructions
├── CLAUDE.md                        # Claude Code instructions
└── pyproject.toml                   # Python project config (UV)
```

**Structure Rationale**: Separates concerns (main loop, operations, storage, validation) while remaining simple enough for Phase I learning objectives.

## Development Workflow

### Specification Phase
1. User provides feature description
2. Claude Code generates spec.md with user stories and acceptance criteria
3. User reviews and approves specification
4. Specification frozen before planning

### Planning Phase
1. Claude Code generates plan.md with technical approach
2. Plan MUST reference constitution principles
3. Plan MUST define data structures and function signatures
4. User reviews and approves plan
5. Plan frozen before task breakdown

### Task Phase
1. Claude Code generates tasks.md with specific, testable tasks
2. Each task MUST include implementation steps and test steps
3. User reviews and approves task list
4. Tasks executed sequentially with test-first approach

### Implementation Phase
1. For each task:
   - Read task requirements
   - Write test steps (how to verify it works)
   - Implement feature
   - Execute test steps
   - Mark task complete if tests pass
2. Commit after each completed task
3. Create Prompt History Record (PHR) for significant changes

### Validation Phase
1. Execute complete test scenario covering all five operations
2. Verify error handling for all invalid inputs
3. Confirm code follows clean code principles
4. Check documentation completeness

## Success Criteria

Phase I is complete when ALL of the following are true:

### Functional Completeness
- ✅ User can add tasks with title and optional description
- ✅ User can view all tasks with their completion status
- ✅ User can update task title and description
- ✅ User can mark tasks as complete/incomplete (toggle)
- ✅ User can delete tasks
- ✅ Application handles invalid inputs gracefully without crashing

### Code Quality
- ✅ All code follows PEP 8 conventions
- ✅ Functions are small (≤20 lines), focused, with clear names
- ✅ All functions have docstrings
- ✅ No global variables except task storage
- ✅ Error handling uses try-except appropriately

### Documentation
- ✅ spec.md exists with complete user stories and acceptance criteria
- ✅ plan.md exists with data model and architecture decisions
- ✅ tasks.md exists with all tasks marked complete
- ✅ README.md provides setup instructions and usage examples
- ✅ Code includes clear docstrings for all functions

### Testing
- ✅ Manual test scenarios exist for all five operations
- ✅ Error handling scenarios tested and documented
- ✅ All tests pass successfully

### Learning Objectives Met
- ✅ Demonstrates understanding of CRUD operations
- ✅ Shows proper data structure design
- ✅ Implements clean code principles
- ✅ Follows spec-driven development methodology
- ✅ Provides foundation for Phase II database migration

## Governance

### Amendment Process
Constitution changes MUST be documented with:
- Clear rationale for the change
- Version increment following semantic versioning
- Update to dependent templates (spec, plan, tasks)
- Approval before taking effect

### Version Semantics
- MAJOR: Principle removal or fundamental scope change
- MINOR: New principle added or significant expansion
- PATCH: Clarifications, examples, or formatting improvements

### Compliance
- All spec.md files MUST reference relevant constitution principles
- All plan.md files MUST include "Constitution Check" section
- All code reviews MUST verify constitutional compliance
- PHR (Prompt History Records) MUST document any principle violations and justification

### Non-Compliance Handling
If a principle violation is necessary (e.g., external dependency for critical feature):
1. Document in plan.md "Complexity Tracking" section
2. Provide clear justification for why violation is needed
3. Explain why simpler alternatives were insufficient
4. Get explicit user approval
5. Record decision in ADR if architecturally significant

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
