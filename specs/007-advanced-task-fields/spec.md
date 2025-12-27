# Feature Specification: Advanced Task Fields

**Feature Branch**: `007-advanced-task-fields`
**Created**: 2025-12-25
**Status**: Draft
**Phase**: V (Cloud Deployment & Event-Driven Architecture)

## User Scenarios & Testing

### User Story 1 - Prioritize Tasks (Priority: P1)

Users organize tasks by importance using priority levels (High, Medium, Low) to focus on critical work first.

**Why P1**: Core productivity feature - reduces decision fatigue.

**Independent Test**: Create tasks with different priorities, filter by High, verify correct results.

**Acceptance Scenarios**:
1. **Given** creating task, **When** select High priority, **Then** task saved with priority=high, red badge displays
2. **Given** 10 mixed-priority tasks, **When** filter High, **Then** only high-priority tasks show
3. **Given** task list, **When** sort by priority, **Then** High→Medium→Low order
4. **Given** editing task, **When** change Medium→High, **Then** updates and moves to top

---

### User Story 2 - Organize with Tags (Priority: P1)

Users categorize tasks with multiple tags (work, personal, project names) for flexible organization.

**Why P1**: Essential organization - users need multi-dimensional categories.

**Independent Test**: Create task with tags work,urgent, search tag=work, verify appears.

**Acceptance Scenarios**:
1. **Given** creating task, **When** enter tags work,meeting,Q1, **Then** saved as array
2. **Given** tasks with tags, **When** search tag=work, **Then** all work-tagged tasks show
3. **Given** task with tags, **When** click tag chip, **Then** filters to that tag
4. **Given** editing task, **When** add urgent to existing work, **Then** both tags saved

---

### User Story 3 - Set Due Dates (Priority: P2)

Users track deadlines by setting due dates with times.

**Why P2**: Important but less critical than priority/tags.

**Independent Test**: Create task with due_date, verify displays in local timezone.

**Acceptance Scenarios**:
1. **Given** creating task, **When** set due 2025-12-31 18:00, **Then** UTC timestamp saved
2. **Given** tasks with dates, **When** sort by due date, **Then** chronological order
3. **Given** overdue task, **When** view list, **Then** red Overdue indicator shows
4. **Given** filter, **When** select Due this week, **Then** next 7 days tasks show

---

### User Story 4 - Recurring Tasks (Priority: P2)

Users create repeating tasks (daily standup, weekly reports) that auto-regenerate.

**Why P2**: Reduces manual work for repetitive tasks.

**Independent Test**: Create recurring daily task, complete it, verify next instance created.

**Acceptance Scenarios**:
1. **Given** creating task, **When** check Recurring + daily, **Then** is_recurring=true saved
2. **Given** weekly recurring, **When** mark complete, **Then** new instance created 7 days ahead
3. **Given** recurring task, **When** edit interval daily→weekly, **Then** future use weekly

---

### Edge Cases

- Past due dates: Allowed, shows Overdue
- Tags with spaces/unicode: Allowed, trimmed and lowercased
- Recurring deletion: Cancels future scheduled events
- Timezone changes: UTC storage, display converts automatically
- is_recurring without interval: Validation error
- Invalid priority: Validation error
- 100 tags: Autocomplete shows 20 most recent

## Requirements

### Functional Requirements

- **FR-001**: System MUST support priority: low, medium, high
- **FR-002**: System MUST default priority=medium
- **FR-003**: System MUST filter by priority
- **FR-004**: System MUST sort by priority
- **FR-005**: System MUST support 0-10 tags per task
- **FR-006**: System MUST search tags case-insensitive
- **FR-007**: System MUST match ANY tag (OR logic)
- **FR-008**: System MUST allow optional due date/time
- **FR-009**: System MUST store UTC timestamps
- **FR-010**: System MUST display local timezone
- **FR-011**: System MUST show overdue indicator
- **FR-012**: System MUST allow recurring flag
- **FR-013**: System MUST require interval if recurring
- **FR-014**: System MUST support daily/weekly/monthly
- **FR-015**: System MUST auto-create next instance
- **FR-016**: System MUST validate priority enum
- **FR-017**: System MUST validate non-empty tags
- **FR-018**: System MUST validate recurring_interval
- **FR-019**: System MUST enforce user isolation
- **FR-020**: System MUST index priority and due_date

### Key Entities

- **Task (Enhanced)**: User actionable with priority, tags, due_date, recurring fields
- **Priority**: Enum (low/medium/high) for importance
- **Tag**: Flexible category label
- **Recurring Interval**: Schedule pattern (daily/weekly/monthly)

## Success Criteria

- **SC-001**: Assign priority in <10s
- **SC-002**: Add tags in <15s
- **SC-003**: Priority filter <1s for 1000 tasks
- **SC-004**: Tag search <1s for 1000 tasks
- **SC-005**: Set due date in <20s
- **SC-006**: Overdue indicator instant
- **SC-007**: Recurring next instance <60s
- **SC-008**: 10 tags no degradation
- **SC-009**: 90% use priority filtering first session
- **SC-010**: Tag autocomplete <500ms

## Assumptions

- Simple priority levels sufficient
- Comma-separated tag input acceptable
- Simple recurring intervals (not custom)
- UTC storage, local display for dates
- Event-driven handles recurring automation
- JSONB/ARRAY database support
- 10 tag limit reasonable

## Dependencies

- Phase I-IV task CRUD functional
- Kubernetes deployment operational
- Neon PostgreSQL + Alembic
- Dapr Jobs API (future)

## Out of Scope

- Custom recurring intervals
- Tag hierarchies
- Task dependencies
- Priority auto-escalation
- Timezone selection UI
- Notification system

## Constitution Alignment

- Principle IV: Data Model Integrity
- Principle XXII: Event-Driven Architecture
- Principle XXVI: Advanced Task Management
- Principle II: Spec-Driven Development
- Principle VIII: User Isolation
