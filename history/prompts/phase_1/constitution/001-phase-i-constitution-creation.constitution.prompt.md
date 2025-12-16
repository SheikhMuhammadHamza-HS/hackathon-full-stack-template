---
id: 001
title: Phase I Constitution Creation
stage: constitution
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5
feature: phase-1-console-app
branch: main
user: system
command: /sp.constitution
labels: ["constitution", "phase-1", "setup", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (documentation artifact)
---

## Prompt

# Constitution File Generation Prompt - Phase I

You are tasked with creating a Constitution file for Phase I of the Todo application hackathon project.

## Context
This is Phase I: Todo In-Memory Python Console App with Basic Level functionality only.

## Requirements from Document

### Technology Stack
- Python 3.13+
- UV (package manager)
- In-memory storage (Python dict/list - NO database)
- Claude Code + Spec-Kit Plus for development

### Features to Support (Basic Level Only)
1. Add Task - Create new todo items
2. Delete Task - Remove tasks from list
3. Update Task - Modify existing task details
4. View Task List - Display all tasks
5. Mark as Complete - Toggle task completion status

### Development Constraints
- Spec-Driven Development MANDATORY
- No manual coding allowed - must use Claude Code
- Clean code principles
- Proper Python project structure
- Console interface only (no web, no GUI)

### Project Structure Required
```
phase1-console/
├── constitution.md          # This file
├── specs/                   # All specification files
├── src/                     # Python source code
├── README.md               # Setup instructions
└── CLAUDE.md               # Claude Code instructions
```

### Key Principles to Include
- Why we use in-memory storage (simplicity, learning foundation)
- Why console interface (focus on core logic first)
- Why spec-driven approach (prevent vibe-coding, ensure quality)
- Python coding standards to follow
- Error handling approach
- Data structure design (how to store tasks in memory)
- Input validation rules

### Windows Users Consideration
- Must use WSL 2 (Windows Subsystem for Linux)
- Constitution should acknowledge this requirement

## Your Task

Generate a Constitution file that defines:
1. **Project Purpose** - Why Phase I exists (learning foundation)
2. **Core Principles** - Non-negotiable rules for this phase
3. **Technical Standards** - Python conventions, structure patterns
4. **Architecture Constraints** - In-memory only, console only, no external dependencies except standard library
5. **Data Model Rules** - How tasks should be structured in memory
6. **User Interaction Patterns** - Console input/output standards
7. **Error Handling Strategy** - How to handle invalid inputs gracefully
8. **Testing Approach** - How to verify functionality
9. **Success Criteria** - What makes Phase I complete

## Output Format

Create a markdown Constitution file with clear sections, concise rules, and justifications for each principle. Make it actionable for AI agents implementing Phase I.

The Constitution should guide agents to build a simple, clean, well-structured console todo app that serves as the foundation for future phases.

## Response snapshot

Created comprehensive Phase I Constitution (v1.0.0) with 7 core principles:

1. **Learning Foundation First** - In-memory storage and console interface to focus on fundamentals
2. **Spec-Driven Development** - Mandatory spec → plan → tasks workflow, no vibe-coding
3. **Test-First Development** - Manual console testing with explicit test steps per task
4. **Data Model Integrity** - Structured task dictionaries with type safety and referential integrity
5. **Input Validation and Error Handling** - Graceful error handling, user-friendly messages
6. **Clean Code and Python Standards** - PEP 8, small functions (≤20 lines), docstrings required
7. **Windows via WSL 2 Only** - Consistent Linux environment for development

Additional sections cover:
- Scope and Constraints (in/out of scope for Phase I)
- Project Structure (src/, specs/, history/ organization)
- Development Workflow (specification → planning → task → implementation → validation)
- Success Criteria (functional, code quality, documentation, testing, learning objectives)
- Governance (amendment process, versioning, compliance, non-compliance handling)

Constitution includes Sync Impact Report documenting template alignment verification.

## Outcome

- ✅ Impact: Established foundational governance for Phase I console application development
- 🧪 Tests: N/A (governance document, not code)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0)
- 🔁 Next prompts: Ready for /sp.specify to create feature specification following constitutional principles
- 🧠 Reflection: Constitution successfully bridges learning objectives with professional development practices. Clear rules prevent scope creep while maintaining focus on CRUD fundamentals.

## Evaluation notes (flywheel)

- Failure modes observed: None - initial constitution creation
- Graders run and results (PASS/FAIL): Manual review pending - all placeholders filled, principles actionable
- Prompt variant (if applicable): N/A (initial version)
- Next experiment (smallest change to try): Validate constitution effectiveness during first feature specification cycle
