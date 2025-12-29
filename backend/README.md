# Backend - Hackathon Todo API

FastAPI backend for Multi-User Authentication System with JWT-based security and PostgreSQL database.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLModel 0.0.22
- **Migrations**: Alembic 1.13+
- **Authentication**: JWT (PyJWT 2.10+)
- **Password Hashing**: bcrypt 4.2+
- **Python**: 3.13+
- **Package Manager**: UV

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database connection & session management
│   ├── models.py            # SQLModel database models (User, Task)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT middleware (verify_jwt, generate_jwt)
│   ├── config.py            # Application configuration
│   └── routers/
│       ├── auth.py          # Authentication endpoints (signup, signin, signout)
│       ├── tasks.py         # Task CRUD endpoints
│       └── admin.py         # Admin endpoints (user management)
├── alembic/
│   ├── versions/            # Database migration files
│   └── env.py               # Alembic configuration
├── tests/                   # Test suite
├── .env                     # Environment variables (DO NOT COMMIT)
├── .env.example             # Environment template
└── pyproject.toml           # Dependencies and build config
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend

# Install with UV package manager
uv sync
```

### 2. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env and fill in values:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - BETTER_AUTH_SECRET: Generate with: openssl rand -base64 32
# - ALLOWED_ORIGINS: Frontend URL (http://localhost:3000)
```

**Required Variables:**
```env
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-32-char-random-secret
ALLOWED_ORIGINS=http://localhost:3000
DATABASE_ECHO=false
```

**OAuth Variables (Optional - for Google/GitHub authentication):**
```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
```

> **Note**: OAuth is optional. If not configured, users can still signup/signin with email/password. See [OAuth Setup Guide](docs/oauth-setup.md) for detailed instructions on obtaining credentials.

### 3. Run Database Migrations

```bash
# Apply migrations to create tables
.venv/Scripts/alembic.exe upgrade head

# Verify tables created in Neon Console
```

### 4. Start Development Server

```bash
# Start with auto-reload
.venv/Scripts/uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8001

# Server will be available at:
# - API: http://localhost:8001
# - Docs: http://localhost:8001/docs
# - Health: http://localhost:8001/health
```

## API Endpoints

### Authentication (Public)
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in with email/password
- `POST /api/auth/signout` - Sign out (client-side token removal)
- `GET /api/auth/google/login` - Initiate Google OAuth flow
- `GET /api/auth/google/callback` - Handle Google OAuth callback
- `GET /api/auth/github/login` - Initiate GitHub OAuth flow
- `GET /api/auth/github/callback` - Handle GitHub OAuth callback

### Tasks (Protected - Requires JWT)
- `GET /api/{user_id}/tasks` - List all user tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PATCH /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `POST /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

### Admin (Protected - Requires Admin JWT)
- `GET /api/admin/users` - List all users
- `GET /api/admin/stats` - Database statistics
- `DELETE /api/admin/users/{user_id}` - Delete user and their tasks

## Security Features

### User Isolation
Every protected endpoint enforces:
1. JWT token validation
2. URL `user_id` matches JWT `authenticated_user`
3. Database queries filter by `authenticated_user`

### Error Handling
- Generic error messages (prevent user enumeration)
- Server-side logging for debugging
- Appropriate HTTP status codes (401, 403, 404, 500)

## Testing

### Interactive API Documentation
```
http://localhost:8001/docs
```

### Manual Testing with cURL
```bash
# Signup
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'

# Signin
curl -X POST http://localhost:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get tasks (requires JWT token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8001/api/YOUR_USER_ID/tasks
```

## Database Management

### Create New Migration
```bash
.venv/Scripts/alembic.exe revision --autogenerate -m "Description"
```

### Apply Migrations
```bash
.venv/Scripts/alembic.exe upgrade head
```

### Rollback Migration
```bash
.venv/Scripts/alembic.exe downgrade -1
```

### Reset Database
```bash
.venv/Scripts/alembic.exe downgrade base
.venv/Scripts/alembic.exe upgrade head
```

## Admin Configuration

Configure admin access via environment variables in your `.env` file:

```bash
# Comma-separated list of emails with admin privileges
ADMIN_EMAILS=admin@example.com,other-admin@example.com

# Admin credentials (for initial admin user)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=YourSecurePassword123!
```

**Security Notes:**
- Never hardcode admin credentials in source code
- Use strong passwords (8+ chars with uppercase, lowercase, digit)
- Keep `.env` file out of version control (already in `.gitignore`)

Admin users can access `/api/admin/*` endpoints after authentication.

## Troubleshooting

### Common Issues

**1. Import Error: ModuleNotFoundError**
```bash
# Reinstall dependencies
uv sync
```

**2. Database Connection Error**
- Verify DATABASE_URL in .env
- Remove query parameters (?sslmode=require) from URL
- SSL is configured in code via `connect_args={"ssl": True}`

**3. Migration Fails**
```bash
# Check alembic/env.py imports app.models correctly
# Ensure DATABASE_URL is set in .env
```

**4. CORS Error**
```bash
# Verify ALLOWED_ORIGINS in .env matches frontend URL
ALLOWED_ORIGINS=http://localhost:3000
```

## Development Commands

```bash
# Install dependencies
uv sync

# Start server (with reload)
.venv/Scripts/uvicorn.exe app.main:app --reload --port 8001

# Run migrations
.venv/Scripts/alembic.exe upgrade head

# Generate migration
.venv/Scripts/alembic.exe revision --autogenerate -m "message"

# Run tests (when implemented)
.venv/Scripts/pytest.exe
```

## Production Deployment

See `specs/001-user-auth/quickstart.md` for production deployment instructions (Render or Docker).

## Contributing

This project follows Spec-Driven Development (SDD). All changes must:
1. Reference specification requirements
2. Include tests
3. Follow code quality standards in `.specify/memory/constitution.md`

## License

Hackathon Project - Internal Use
