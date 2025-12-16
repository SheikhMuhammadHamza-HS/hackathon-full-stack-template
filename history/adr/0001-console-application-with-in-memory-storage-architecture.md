# ADR-0001: Console Application with In-Memory Storage Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-16
- **Feature:** 001-task-crud
- **Context:** Phase I of todo application development requires establishing fundamental programming patterns before introducing complexity. The architecture must focus on core business logic, data structures, and clean code practices while avoiding database integration, web interfaces, and advanced features.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Application Type**: Console-based interface with menu-driven user experience
- **Storage**: In-memory using Python built-in data structures (list of dictionaries)
- **Data Persistence**: None between sessions (explicitly temporary storage)
- **User Interface**: Terminal-based with clear prompts and formatted output
- **Architecture Pattern**: Single-process, in-memory data management
- **Session Scope**: All data exists only during runtime and is lost on exit

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Simple implementation allowing focus on core CRUD logic and business rules
- No database setup or configuration complexity
- Fast iteration and testing during development
- Clear separation between data model and persistence concerns
- Aligns with Phase I learning objectives for foundational programming patterns
- No external dependencies or connection management required
- Straightforward debugging and testing procedures

### Negative

- No data persistence between application runs
- Data loss on application exit or crash
- Memory usage scales with task count (no upper limit)
- Single-user only, no concurrency support
- Limited scalability for real-world usage
- Requires re-implementation for Phase II database integration

## Alternatives Considered

**Alternative A: File-based Storage (JSON/CSV)**
- Pros: Basic persistence, simple format, human-readable
- Cons: File I/O complexity, concurrency issues, no ACID properties
- Rejected: Adds unnecessary complexity for Phase I learning objectives

**Alternative B: Database Integration (SQLite)**
- Pros: Persistent storage, query capabilities, structured data
- Cons: Adds database complexity, connection management, migration concerns
- Rejected: Violates Phase I constitution principle of starting simple

**Alternative C: Web Interface with Framework**
- Pros: Modern UI, browser accessibility, interactive experience
- Cons: Adds web framework complexity, HTTP handling, client-server concerns
- Rejected: Violates Phase I constitution requirement for console interface only

## References

- Feature Spec: specs/001-task-crud/spec.md
- Implementation Plan: specs/001-task-crud/plan.md
- Related ADRs: ADR-0002 (Python Standard Library Only), ADR-0003 (Task Data Model)
- Evaluator Evidence: specs/001-task-crud/research.md