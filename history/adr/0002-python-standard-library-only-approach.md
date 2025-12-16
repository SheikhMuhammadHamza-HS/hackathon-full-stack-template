# ADR-0002: Python Standard Library Only Approach

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-16
- **Feature:** 001-task-crud
- **Context:** Phase I constitution requires using only Python standard library to focus on core programming concepts without external dependencies. This approach ensures learning fundamental patterns before introducing complexity through third-party packages.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Language Version**: Python 3.13+ (as required by constitution)
- **Dependencies**: Python standard library only (no external packages)
- **Validation**: Using built-in Python validation functions (len(), isinstance(), etc.)
- **Date/Time Handling**: Using Python's datetime module from standard library
- **Input/Output**: Using built-in input() and print() functions
- **Data Structures**: Using built-in Python data types (dict, list, str, int, bool)

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- No external dependency management required (no pip install, requirements.txt, etc.)
- Focus on core Python programming concepts without framework distractions
- Consistent behavior across Python installations
- Faster setup and execution without package resolution
- Learning fundamental Python standard library capabilities
- Aligns with Phase I learning foundation principles from constitution
- No version conflicts or dependency hell scenarios
- Deterministic builds and execution

### Negative

- Limited functionality compared to specialized third-party libraries
- More manual implementation required for validation and formatting
- Less sophisticated error handling capabilities
- Missing advanced features like automatic serialization/deserialization
- Potentially more verbose code for complex operations
- May require more custom code to achieve the same functionality
- Could be less performant than optimized third-party alternatives

## Alternatives Considered

**Alternative A: Third-party Validation Library (e.g., pydantic)**
- Pros: Advanced validation, type checking, automatic serialization
- Cons: Adds external dependency, learning curve for library-specific patterns
- Rejected: Violates constitution requirement for standard library only

**Alternative B: Web Framework (e.g., Flask/Django)**
- Pros: Built-in validation, routing, request handling
- Cons: Adds significant complexity, web-specific concerns for console app
- Rejected: Violates constitution requirement for console interface and standard library only

**Alternative C: Database ORM (e.g., SQLAlchemy)**
- Pros: Structured data management, query capabilities, type safety
- Cons: Adds external dependencies, database complexity for in-memory storage
- Rejected: Violates both constitution requirements (standard library only and in-memory storage)

## References

- Feature Spec: specs/001-task-crud/spec.md
- Implementation Plan: specs/001-task-crud/plan.md
- Related ADRs: ADR-0001 (Console Architecture), ADR-0003 (Task Data Model)
- Evaluator Evidence: specs/001-task-crud/research.md