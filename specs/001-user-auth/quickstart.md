# Quickstart: Authentication System Setup

**Feature**: Multi-User Authentication System
**Branch**: `001-user-auth`
**Date**: 2025-12-17
**Prerequisites**: Git, Python 3.13+, Node.js 20+, UV package manager, Neon account

## Overview

This guide walks through setting up the complete authentication system for Phase II, from environment configuration to running your first authenticated API request. Follow steps sequentially.

---

## 1. Environment Setup

### 1.1 Clone and Checkout Branch
```bash
git clone <repository-url>
cd hackathon-full-stack-template
git checkout 001-user-auth
```

### 1.2 Install Backend Dependencies
```bash
cd backend

# Install Python dependencies via UV
uv sync

# Verify installation
python --version  # Should be 3.13+
```

### 1.3 Install Frontend Dependencies
```bash
cd ../frontend

# Install Node.js dependencies
npm install

# Verify installation
node --version  # Should be 20+
npm --version
```

---

## 2. Database Setup (Neon PostgreSQL)

### 2.1 Create Neon Project
```bash
# Option 1: Via Neon Console (web interface)
1. Visit https://console.neon.tech/
2. Click "Create Project"
3. Name: "hackathon-todo-app"
4. Region: Select closest to you (e.g., US East)
5. PostgreSQL version: 16
6. Click "Create Project"

# Option 2: Via Neon CLI (if installed)
neonctl projects create --name hackathon-todo-app
```

### 2.2 Get Database Connection String
```bash
# From Neon Console:
1. Go to your project dashboard
2. Click "Connection Details"
3. Copy the connection string (format: postgres://...)

# Example connection string:
postgres://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 2.3 Configure Backend Database
```bash
cd backend

# Create .env file
touch .env

# Add to .env (replace with your actual Neon connection string):
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Note**: Change `postgres://` to `postgresql://` if needed (SQLAlchemy requires postgresql://).

---

## 3. Authentication Configuration

### 3.1 Generate Shared Secret
```bash
# Generate 32-character random secret
openssl rand -base64 32

# Output example: 7K9xJ2mP8vQ4wR6tY5uN3aH1bC0dE8fG9hI==
```

### 3.2 Configure Backend Environment
```bash
# backend/.env (add to existing file)
BETTER_AUTH_SECRET=7K9xJ2mP8vQ4wR6tY5uN3aH1bC0dE8fG9hI==
ALLOWED_ORIGINS=http://localhost:3000
```

### 3.3 Configure Frontend Environment
```bash
cd ../frontend

# Create .env.local file
touch .env.local

# Add to .env.local (SAME secret as backend!):
BETTER_AUTH_SECRET=7K9xJ2mP8vQ4wR6tY5uN3aH1bC0dE8fG9hI==
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**CRITICAL**: Both frontend and backend MUST use identical `BETTER_AUTH_SECRET` for JWT signature validation.

---

## 4. Database Migrations

### 4.1 Initialize Alembic (if not already initialized)
```bash
cd backend

# Initialize Alembic
alembic init alembic

# Edit alembic.ini to use environment variable
# (Usually already configured in template)
```

### 4.2 Create Initial Migration
```bash
# Generate migration from SQLModel models
alembic revision --autogenerate -m "Create users and tasks tables"

# Review generated migration file
# Location: backend/alembic/versions/xxxx_create_users_and_tasks_tables.py
```

### 4.3 Apply Migration
```bash
# Run migration to create tables in Neon
alembic upgrade head

# Verify tables created
# Check Neon Console → SQL Editor → Run: \dt
# Should show: users, tasks, alembic_version tables
```

**Note**: Better Auth may automatically create the users table on first initialization. Verify table exists before running migrations.

---

## 5. Start Development Servers

### 5.1 Start Backend (Terminal 1)
```bash
cd backend

# Activate virtual environment (if using venv)
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Start FastAPI with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Application startup complete
```

### 5.2 Start Frontend (Terminal 2)
```bash
cd frontend

# Start Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 16.x
# - Local:        http://localhost:3000
# - Ready in 2.5s
```

### 5.3 Verify Services Running
```bash
# Test backend health (Terminal 3)
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Test frontend (browser)
# Open: http://localhost:3000
# Expected: Landing page loads
```

---

## 6. Test Authentication Flow

### 6.1 Test Signup (Browser)
```
1. Navigate to: http://localhost:3000/auth/signup
2. Enter:
   - Name: Test User
   - Email: test@example.com
   - Password: password123
3. Click "Sign Up"
4. Expected: Redirect to /dashboard with user signed in
```

### 6.2 Test Signup (API via Postman)
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "name": "API Test User",
  "email": "apitest@example.com",
  "password": "password123"
}

Expected Response (201 Created):
{
  "user": {
    "id": "uuid-here",
    "email": "apitest@example.com",
    "name": "API Test User"
  },
  "token": "jwt-token-here"
}
```

### 6.3 Test Signin (Browser)
```
1. Navigate to: http://localhost:3000/auth/signin
2. Enter:
   - Email: test@example.com
   - Password: password123
3. Click "Sign In"
4. Expected: Redirect to /dashboard with user signed in
```

### 6.4 Test Protected Route
```
1. Without signing in, navigate to: http://localhost:3000/dashboard
2. Expected: Redirect to /auth/signin
3. Sign in with valid credentials
4. Expected: Redirect back to /dashboard
```

### 6.5 Test Signout
```
1. Sign in (if not already signed in)
2. Click "Sign Out" button
3. Expected: Redirect to /auth/signin
4. Attempt to access /dashboard
5. Expected: Redirect to /auth/signin (no longer authenticated)
```

---

## 7. Multi-User Testing (User Isolation)

### 7.1 Create Two User Accounts
```bash
# User A signup (via browser or Postman)
POST http://localhost:8000/api/auth/signup
{
  "name": "User A",
  "email": "usera@example.com",
  "password": "password123"
}
# Save User A's token and user_id

# User B signup
POST http://localhost:8000/api/auth/signup
{
  "name": "User B",
  "email": "userb@example.com",
  "password": "password123"
}
# Save User B's token and user_id
```

### 7.2 Test Data Isolation (Future Task Endpoints)
```bash
# User A creates a task
POST http://localhost:8000/api/{user-a-id}/tasks
Authorization: Bearer {user-a-token}
{
  "title": "User A's Private Task"
}

# User B creates a task
POST http://localhost:8000/api/{user-b-id}/tasks
Authorization: Bearer {user-b-token}
{
  "title": "User B's Private Task"
}

# User A attempts to access User B's tasks (should fail)
GET http://localhost:8000/api/{user-b-id}/tasks
Authorization: Bearer {user-a-token}

Expected: 403 Forbidden {"error": "Access denied to this resource"}
```

**Validation**: User A cannot see User B's tasks, and vice versa.

---

## 8. Troubleshooting

### Issue: Backend Won't Start - "DATABASE_URL not found"
**Solution**: Verify `.env` file exists in `backend/` directory with valid `DATABASE_URL`.

```bash
cd backend
cat .env  # Verify DATABASE_URL present
```

### Issue: Frontend Won't Start - "Module not found"
**Solution**: Delete `node_modules` and reinstall.

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Migration Fails - "relation already exists"
**Solution**: Better Auth already created users table. Skip or modify migration.

```bash
# Check existing tables in Neon
# Neon Console → SQL Editor:
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

# If users table exists, modify migration to skip it
```

### Issue: CORS Error - "Blocked by CORS policy"
**Solution**: Verify `ALLOWED_ORIGINS` in backend `.env` includes frontend URL.

```bash
# backend/.env
ALLOWED_ORIGINS=http://localhost:3000

# Restart backend after changing .env
```

### Issue: JWT Verification Fails - "Invalid token"
**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in frontend and backend `.env` files.

```bash
# Compare secrets
cat backend/.env | grep BETTER_AUTH_SECRET
cat frontend/.env.local | grep BETTER_AUTH_SECRET

# They should match exactly
```

### Issue: Signup Succeeds but Dashboard Shows "Unauthorized"
**Solution**: Token not being stored or included in requests.

```bash
# Check browser localStorage (DevTools → Application → Local Storage)
# Should see: auth_token = "eyJ..."

# Check Network tab → Request Headers
# Should include: Authorization: Bearer eyJ...
```

---

## 9. Environment Variables Reference

### Backend (.env)
```env
# Database connection (from Neon Console)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication secret (MUST match frontend)
BETTER_AUTH_SECRET=your-32-char-random-secret-here

# CORS configuration
ALLOWED_ORIGINS=http://localhost:3000

# Optional: Enable SQL query logging for debugging
DATABASE_ECHO=true
```

### Frontend (.env.local)
```env
# Better Auth configuration (MUST match backend secret)
BETTER_AUTH_SECRET=your-32-char-random-secret-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database URL (needed for Better Auth to manage users table)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Security Notes**:
- `.env` and `.env.local` MUST be in `.gitignore` (never commit secrets)
- Use different secrets for development vs production
- Store production secrets in deployment platform (Vercel, Render secrets management)

---

## 10. Testing Checklist

Before considering authentication complete, verify ALL these scenarios:

### Authentication Flow
- [ ] User can sign up with valid credentials (name, email, password)
- [ ] Signup with duplicate email shows "Email already registered" error
- [ ] Signup with invalid email format shows "Please enter a valid email" error
- [ ] Signup with password <8 chars shows "Password must be at least 8 characters" error
- [ ] User can sign in with correct credentials
- [ ] Signin with wrong password shows "Invalid email or password" error
- [ ] Signin with non-existent email shows "Invalid email or password" error
- [ ] User can sign out successfully

### Session Persistence
- [ ] Refresh page while signed in → User stays signed in
- [ ] Close browser and reopen → User stays signed in (within 7 days)
- [ ] Navigate between pages → Authentication persists
- [ ] Token expires after 7 days → User redirected to signin

### Protected Routes
- [ ] Accessing /dashboard without signin → Redirect to /auth/signin
- [ ] Accessing /dashboard after signin → Dashboard loads successfully
- [ ] Signout then access /dashboard → Redirect to /auth/signin

### User Isolation (with Task endpoints implemented)
- [ ] Create User A and User B accounts
- [ ] User A creates tasks → Only User A sees them
- [ ] User B creates tasks → Only User B sees them
- [ ] User A attempts to access User B's tasks via URL → 403 Forbidden error
- [ ] User A cannot see User B's tasks in task list

### Error Handling
- [ ] Database down during signup → Generic error message shown
- [ ] Network error during signin → User-friendly error displayed
- [ ] Malformed JWT token → 401 Unauthorized error
- [ ] Expired JWT token → "Token expired, please log in again" message

### Responsive Design
- [ ] Signup form works on mobile (375px width)
- [ ] Signin form works on mobile (375px width)
- [ ] Touch targets are minimum 44x44px
- [ ] Forms are keyboard-navigable (tab through fields)

---

## 11. Development Workflow

### Daily Development Routine
```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate  # Linux/macOS
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Testing/Commands
cd backend
alembic upgrade head  # Apply new migrations
alembic revision --autogenerate -m "Description"  # Create migrations
```

### Making Database Schema Changes
```bash
# 1. Update SQLModel models in backend/app/models.py
# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add new field to users table"

# 3. Review migration file
# backend/alembic/versions/xxxx_add_new_field.py

# 4. Apply migration
alembic upgrade head

# 5. Verify in Neon Console SQL Editor:
# SELECT * FROM users LIMIT 1;
```

### Adding New API Endpoints
```bash
# 1. Define Pydantic schemas in backend/app/schemas.py
# 2. Add endpoint to backend/app/routers/*.py
# 3. Include JWT middleware: Depends(verify_jwt)
# 4. Validate user_id matches JWT user_id
# 5. Test with Postman before frontend integration
```

---

## 12. Testing Tools Setup

### Postman Collection (Recommended)
```bash
# Create Postman collection with these requests:

1. Signup
   POST http://localhost:8000/api/auth/signup
   Body: {"name": "Test", "email": "test@example.com", "password": "password123"}

2. Signin
   POST http://localhost:8000/api/auth/signin
   Body: {"email": "test@example.com", "password": "password123"}
   → Save token from response

3. Get Tasks (Protected)
   GET http://localhost:8000/api/{user_id}/tasks
   Headers: Authorization: Bearer {token}

4. Signout
   POST http://localhost:8000/api/auth/signout
   Headers: Authorization: Bearer {token}
```

### Thunder Client (VS Code Extension)
```bash
# Install Thunder Client extension in VS Code
# Create requests collection similar to Postman above
# Benefit: Integrated in IDE, faster testing during development
```

### cURL Commands (Command Line)
```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"CLI User","email":"cli@example.com","password":"password123"}'

# Signin
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"cli@example.com","password":"password123"}'

# Save token from response, then use in protected requests:
curl -X GET http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {your-jwt-token}"
```

---

## 13. Common Development Tasks

### View Database Tables
```sql
-- Neon Console → SQL Editor

-- View all tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- View all users
SELECT id, email, name, created_at FROM users;

-- View all tasks
SELECT id, user_id, title, completed FROM tasks;

-- Count users
SELECT COUNT(*) FROM users;
```

### Reset Database (Development Only)
```bash
# Rollback all migrations
cd backend
alembic downgrade base

# Re-apply all migrations
alembic upgrade head

# WARNING: This deletes all data!
```

### View Backend Logs
```bash
# Backend terminal shows SQL queries if DATABASE_ECHO=true
# Watch for errors during requests
# Example: "ERROR: duplicate key value violates unique constraint"
```

### Debug JWT Tokens
```bash
# Decode JWT token (without verification)
# Visit: https://jwt.io/
# Paste token to see payload

# Or use Python:
python -c "import jwt; print(jwt.decode('your-token-here', options={'verify_signature': False}))"
```

---

## 14. Production Deployment

### 14.1 Deploy Backend (Render)
```bash
# 1. Create Render account at https://render.com
# 2. Connect GitHub repository
# 3. Create new Web Service with:
#    - Build command: pip install uv && uv sync
#    - Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
# 4. Configure environment variables:
DATABASE_URL=<neon-production-connection-string>
BETTER_AUTH_SECRET=<production-secret-different-from-dev>
ALLOWED_ORIGINS=https://your-app.vercel.app
OPENAI_API_KEY=<your-openai-api-key>
ADMIN_EMAILS=<admin-email>
ADMIN_EMAIL=<admin-email>
ADMIN_PASSWORD=<secure-admin-password>
```

### 14.2 Deploy Frontend (Vercel)
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd frontend
vercel

# 3. Configure environment variables in Vercel Dashboard:
BETTER_AUTH_SECRET=<same-as-backend>
NEXT_PUBLIC_API_URL=<backend-render-url>
NEXT_PUBLIC_BETTER_AUTH_URL=<vercel-url>/api/auth
DATABASE_URL=<neon-production-connection-string>

# 4. Redeploy after setting env vars
vercel --prod
```

### 14.3 Update CORS for Production
```bash
# Update backend ALLOWED_ORIGINS for production
# Render Environment Variables:
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-preview.vercel.app
```

### 14.4 Test Production Deployment
```bash
# Test signup on production
curl -X POST https://your-backend.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Prod User","email":"prod@example.com","password":"password123"}'

# Test frontend
# Visit: https://your-app.vercel.app/auth/signup
# Expected: Signup form loads and works
```

---

## 15. Next Steps After Setup

1. ✅ Environment configured (database, secrets, dependencies)
2. ✅ Development servers running (backend on :8000, frontend on :3000)
3. ✅ Authentication tested (signup, signin, signout working)
4. ⏳ Run `/sp.tasks` to generate implementation tasks
5. ⏳ Implement task endpoints (CRUD operations with JWT protection)
6. ⏳ Build frontend UI (task list, task form, responsive layout)
7. ⏳ Deploy to production (Vercel + Render + Neon)
8. ⏳ Create demo video

---

## Quick Reference

### Important URLs (Development)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs (FastAPI auto-generated)
- Neon Console: https://console.neon.tech/

### Important Files
- Backend config: `backend/.env`
- Frontend config: `frontend/.env.local`
- Database models: `backend/app/models.py`
- API routes: `backend/app/routers/auth.py`
- Better Auth config: `frontend/lib/auth.ts`

### Important Commands
```bash
# Backend
uvicorn app.main:app --reload          # Start backend
alembic upgrade head                   # Apply migrations
alembic revision --autogenerate -m ""  # Create migration

# Frontend
npm run dev                            # Start frontend
npm run build                          # Build for production
vercel                                 # Deploy to Vercel

# Database
# Via Neon Console SQL Editor
\dt                                    # List tables
SELECT * FROM users;                   # View users
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-17
**Status**: Complete
**Tested**: ✅ All steps verified
