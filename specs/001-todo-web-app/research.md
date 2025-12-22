# Research & Technical Decisions: Todo Web Application

**Feature**: 001-todo-web-app
**Created**: 2025-12-22

## Key Technical Decisions

### 1. Database ORM: SQLModel

**Decision**: Use SQLModel for Task model and database operations

**Rationale**:
- Type-safe: Pydantic models + SQLAlchemy together
- Async support: Works with asyncpg and FastAPI
- Already used for User model (consistency)
- Automatic validation and serialization

**Alternatives Considered**:
- Raw SQLAlchemy: More boilerplate, less type safety
- Django ORM: Not compatible with FastAPI async
- Prisma: Requires Node.js, not Python-native

**Trade-offs**:
- Pros: Type safety, async, FastAPI integration, consistent with auth
- Cons: Smaller ecosystem than pure SQLAlchemy

---

### 2. API Design: RESTful with user_id in Path

**Decision**: Use RESTful endpoints with user_id in URL path

**Pattern**:
```
GET    /api/{user_id}/tasks
POST   /api/{user_id}/tasks
PUT    /api/{user_id}/tasks/{task_id}
PATCH  /api/{user_id}/tasks/{task_id}/complete
DELETE /api/{user_id}/tasks/{task_id}
```

**Rationale**:
- Explicit user context in URL (self-documenting)
- Easy to validate: JWT user_id MUST match URL user_id
- RESTful naming convention
- Consistent with authentication endpoints

**Alternatives Considered**:
- `/api/tasks` (extract user from JWT only): Less explicit, harder to debug
- `/api/users/{user_id}/tasks`: More nested, longer URLs
- GraphQL: Overkill for simple CRUD

**Trade-offs**:
- Pros: Clear, secure, easy to validate
- Cons: Slightly longer URLs

---

### 3. Frontend State Management: React useState

**Decision**: Use React useState for task list state (no global state library)

**Rationale**:
- Simple CRUD operations don't need complex state
- Only one page (dashboard) manages tasks
- Optimistic updates easy with local state
- No need for Redux/Zustand overhead

**Alternatives Considered**:
- Redux Toolkit: Too heavy for simple CRUD
- Zustand: Adds dependency for minimal benefit
- React Query: Good for caching but not needed yet

**Trade-offs**:
- Pros: Simple, no extra dependencies, easy to understand
- Cons: May need refactor if multi-page task access needed

---

### 4. Task Completion: Separate PATCH Endpoint

**Decision**: Use dedicated `PATCH /tasks/{id}/complete` endpoint instead of PUT

**Rationale**:
- Semantic clarity: PATCH for partial update
- Toggle operation is specific action
- Prevents accidental full task updates
- Common UX pattern (checkbox toggle)

**Alternatives Considered**:
- `PUT /tasks/{id}` with completed field: Less explicit
- `POST /tasks/{id}/complete`: Not RESTful (POST should create)
- Boolean query param: `PUT /tasks/{id}?completed=true`: Not clean

**Trade-offs**:
- Pros: Clear intent, semantic correctness
- Cons: One extra endpoint to maintain

---

### 5. User Isolation: Three-Layer Enforcement

**Decision**: Enforce user isolation at three layers

**Layers**:
1. **API Layer**: Verify JWT user_id matches URL user_id (403 if not)
2. **Query Layer**: All database queries filter by user_id
3. **Middleware Layer**: JWT verification on all protected routes

**Rationale**:
- Defense in depth: Multiple security checks
- Prevents URL manipulation attacks
- Clear error messages (403 Forbidden vs 404 Not Found)

**Implementation**:
```python
# Layer 1: API validation
if url_user_id != jwt_user_id:
    raise HTTPException(403, "Access denied")

# Layer 2: Database filter
query = select(Task).where(Task.user_id == jwt_user_id)

# Layer 3: Middleware
@router.get("/", dependencies=[Depends(verify_jwt)])
```

---

### 6. Task Timestamps: Auto-Managed by SQLModel

**Decision**: Use SQLModel's `default_factory=datetime.utcnow` for timestamps

**Rationale**:
- Automatic timestamp management
- Server-side time source (can't be manipulated)
- UTC for consistency across timezones
- updated_at auto-updates on model changes

**Implementation**:
```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Alternatives Considered**:
- Database DEFAULT CURRENT_TIMESTAMP: Works but SQLModel way is cleaner
- Manual timestamp setting: Error-prone, easy to forget

---

### 7. Optimistic UI Updates

**Decision**: Update UI immediately before API response

**Rationale**:
- Instant feedback to user (better UX)
- Feels faster even with network latency
- Rollback on error with toast notification

**Pattern**:
```javascript
// 1. Update UI immediately
setTasks([...tasks, newTask]);

// 2. Call API
const response = await api.post('/tasks', newTask);

// 3. Sync with server response (replace temp ID)
setTasks(tasks.map(t => t.id === tempId ? response : t));
```

**Trade-offs**:
- Pros: Better perceived performance, modern UX
- Cons: Need error handling to rollback on failure

---

### 8. Responsive Design: Mobile-First with Tailwind

**Decision**: Build mobile-first (375px) then scale up with Tailwind breakpoints

**Breakpoints**:
- Mobile: 375px - 640px (base styles)
- Tablet: 640px - 1024px (`sm:`, `md:`)
- Desktop: 1024px+ (`lg:`, `xl:`)

**Rationale**:
- Mobile-first ensures core functionality on all devices
- Tailwind utility classes make responsive easy
- Matches existing app styling

---

## Performance Considerations

### Database Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

**Why**:
- Fast filtering by user (most common query)
- Fast filtering by completion status
- Supports WHERE user_id = X AND completed = Y efficiently

### Query Optimization
- Limit results to recent 100 tasks (prevent slow queries with 1000+ tasks)
- Use `SELECT *` only when all fields needed
- Avoid N+1 queries (fetch tasks in single query)

---

## Security Considerations

### Input Validation
- Title: Required, 1-200 chars, trimmed
- Description: Optional, max 1000 chars
- All inputs sanitized (Pydantic does this automatically)

### SQL Injection Prevention
- SQLModel uses parameterized queries (prevents injection)
- No raw SQL strings with user input
- ORM handles escaping

### Authorization
- JWT verification on all endpoints
- user_id from JWT (not request body - prevents spoofing)
- 403 Forbidden for unauthorized access attempts

---

## Testing Strategy

### Unit Tests (Future)
- Task model validation
- Endpoint input validation
- JWT middleware

### Integration Tests
- Full CRUD flow
- User isolation verification
- Error handling

### Manual Testing
- Multiple users simultaneously
- URL manipulation attempts
- Mobile device testing

---

## Future Enhancements (Out of Scope)

- Task categories/tags
- Task search and filtering
- Due dates and reminders
- Task priority levels
- Pagination for large task lists
- Bulk operations
- Task sharing between users
