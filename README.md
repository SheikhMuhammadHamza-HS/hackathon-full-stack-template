# Hackathon Todo Application

Full-stack multi-user task management system with JWT authentication, built following Spec-Driven Development methodology.

## 🏗️ Monorepo Structure

```
hackathon-full-stack-template/
├── backend/              # FastAPI Python backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   ├── tests/           # Test suite
│   └── README.md        # Backend setup guide
├── frontend/            # Next.js React frontend
│   ├── app/            # Next.js 16 App Router pages
│   ├── components/     # Reusable React components
│   ├── lib/            # Utilities (API client, auth)
│   ├── types/          # TypeScript interfaces
│   └── README.md       # Frontend setup guide
├── specs/              # Feature specifications
│   └── 001-user-auth/  # Authentication feature spec
│       ├── spec.md     # Requirements and user stories
│       ├── plan.md     # Implementation plan
│       ├── tasks.md    # Task breakdown
│       └── contracts/  # API contracts
├── .specify/           # SpecKit Plus templates
└── history/            # Prompt History Records (PHR)
```

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel 0.0.22
- **Migrations**: Alembic 1.13+
- **Auth**: JWT (PyJWT 2.10+)
- **Password**: bcrypt 4.2+
- **Python**: 3.13+

### Frontend
- **Framework**: Next.js 16.0+ (App Router)
- **UI**: React 19
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS v4
- **Font**: Inter (Google Fonts)
- **Node**: 20+

## ⚡ Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- UV package manager (`pip install uv`)
- Neon account (https://neon.tech)

### 1. Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd hackathon-full-stack-template

# Backend setup
cd backend
uv sync
cp .env.example .env
# Edit .env with your Neon DATABASE_URL and BETTER_AUTH_SECRET

# Frontend setup
cd ../frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with matching BETTER_AUTH_SECRET

# Run migrations
cd ../backend
.venv/Scripts/alembic.exe upgrade head
```

### 2. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
.venv/Scripts/uvicorn.exe app.main:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## ✨ Features

### Authentication (Phase II)
- ✅ User signup with email/password
- ✅ User signin with JWT token generation
- ✅ Session persistence (localStorage)
- ✅ Protected routes
- ✅ Secure signout

### Task Management
- ✅ Create tasks (title + description)
- ✅ View all tasks (user-scoped)
- ✅ Edit task details
- ✅ Toggle completion status
- ✅ Delete tasks
- ✅ User data isolation (strict security)

### Admin Features
- ✅ View all users (admin only)
- ✅ Database statistics
- ✅ Delete users (admin only)

### UI/UX
- ✅ Responsive design (mobile-first)
- ✅ Dark mode support
- ✅ Loading states
- ✅ Error handling
- ✅ Accessible (WCAG AA)
- ✅ Keyboard navigation

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- User data isolation (Constitutional Principle VIII)
- Generic error messages (prevent enumeration)
- CORS configured
- Admin role-based access

## 📚 Documentation

- **Quick Start**: `specs/001-user-auth/quickstart.md`
- **Specification**: `specs/001-user-auth/spec.md`
- **Implementation Plan**: `specs/001-user-auth/plan.md`
- **Tasks**: `specs/001-user-auth/tasks.md`
- **Backend Setup**: `backend/README.md`
- **Frontend Setup**: `frontend/README.md`
- **Constitution**: `.specify/memory/constitution.md`

## 🧪 Testing

### Manual Testing Flow
1. **Signup**: Create account at `/auth/signup`
2. **Dashboard**: View tasks (empty state initially)
3. **Add Task**: Create first task
4. **CRUD**: Edit, complete, delete tasks
5. **Signout**: Logout
6. **Signin**: Login again
7. **Verify**: Tasks persisted

### API Testing
Use FastAPI interactive docs:
```
http://localhost:8001/docs
```

### Multi-User Testing
1. Create 2+ accounts
2. Verify data isolation
3. Test cross-user access prevention (403 errors)

## 🛠️ Development Workflow

This project follows **Spec-Driven Development (SDD)**:

1. **Constitution** → Define project principles
2. **Specification** → Define requirements (what to build)
3. **Plan** → Design implementation (how to build)
4. **Tasks** → Break down into actionable items
5. **Implement** → Execute tasks
6. **Test** → Verify against spec
7. **Document** → Create PHR and ADR

### Available Commands
- `/sp.constitution` - Update project principles
- `/sp.specify` - Create feature specification
- `/sp.plan` - Generate implementation plan
- `/sp.tasks` - Generate task breakdown
- `/sp.implement` - Execute implementation
- `/sp.phr` - Create Prompt History Record
- `/sp.adr` - Document architectural decisions

## 📊 Project Status

**Phase**: Phase II (Full-Stack Web Application)
**Feature**: 001-user-auth (Multi-User Authentication)
**Status**: ✅ Implementation Complete (117/117 tasks)

### Completed Phases
- ✅ Phase 1: Setup (T001-T009)
- ✅ Phase 2: Foundational (T010-T020)
- ✅ Phase 3: User Story 1 - Signup (T021-T042)
- ✅ Phase 4: User Story 2 - Signin (T043-T061)
- ✅ Phase 5: User Story 5 - Isolation (T062-T079)
- ✅ Phase 6: User Story 3 - Signout (T080-T090)
- ✅ Phase 7: User Story 4 - Persistence (T091-T101)
- ✅ Phase 8: Dashboard (T102-T106)
- ✅ Phase 9: Polish (T107-T117)

## 🔧 Troubleshooting

### Backend Issues
- **Database connection failed**: Check DATABASE_URL, remove query params
- **Import errors**: Run `uv sync` to reinstall dependencies
- **Migration errors**: Verify alembic/env.py configuration

### Frontend Issues
- **Connection refused**: Verify backend port matches NEXT_PUBLIC_API_URL
- **Auth failed**: Check BETTER_AUTH_SECRET matches backend
- **Env not loading**: Restart dev server after .env.local changes

## 🚀 Deployment

See `specs/001-user-auth/quickstart.md` Section 15 for production deployment:
- **Frontend**: Vercel
- **Backend**: Render
- **Database**: Neon (already cloud-hosted)

## 📝 License

Hackathon Project - Internal Use

## 👥 Contributing

Follow constitutional principles in `.specify/memory/constitution.md`

## 🆘 Support

For detailed setup instructions, see:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Quick Start: `specs/001-user-auth/quickstart.md`
