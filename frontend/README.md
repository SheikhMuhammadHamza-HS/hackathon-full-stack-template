# Frontend - Hackathon Todo App

Next.js 16+ frontend with React 19, TypeScript, and Tailwind CSS for multi-user task management.

## Tech Stack

- **Framework**: Next.js 16.0+ (App Router)
- **UI Library**: React 19
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS v4
- **Font**: Inter (Google Fonts)
- **Authentication**: JWT token-based
- **HTTP Client**: Custom API client with automatic JWT injection
- **Node**: 20+
- **Package Manager**: npm

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy example file
cp .env.local.example .env.local

# Edit .env.local with your values
```

### 3. Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

Create `.env.local` with these values:

```env
# Must match backend secret
BETTER_AUTH_SECRET=your-32-char-secret

# Backend API URL (check backend port!)
NEXT_PUBLIC_API_URL=http://localhost:8001

# Better Auth URL
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth

# Neon database connection
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

**CRITICAL**: `BETTER_AUTH_SECRET` must be identical to backend `.env` file!

## Application Features

### Authentication
- ✅ User signup with validation
- ✅ User signin with JWT generation
- ✅ Session persistence via localStorage
- ✅ Protected routes with auto-redirect
- ✅ Secure signout with token cleanup

### Task Management
- ✅ Create tasks with title and description
- ✅ View all user tasks (sorted by date)
- ✅ Edit task details
- ✅ Toggle completion status
- ✅ Delete tasks with confirmation
- ✅ User data isolation (each user sees only their tasks)

### UI/UX
- ✅ Responsive design (mobile-first 375px+)
- ✅ Dark mode with system preference
- ✅ Loading states for async operations
- ✅ Error messages with retry options
- ✅ Optimistic UI updates
- ✅ Accessible (WCAG AA compliant)
- ✅ Keyboard navigation support

## Project Structure

### Pages (`app/`)
- `page.tsx` - Landing page with smart routing
- `layout.tsx` - Root layout with font and theme provider
- `auth/signup/page.tsx` - User registration form
- `auth/signin/page.tsx` - User login form
- `dashboard/page.tsx` - Protected task management dashboard

### Components (`components/`)
- `AuthForm.tsx` - Reusable form container with inputs
- `TaskList.tsx` - Task list display with sorting
- `TaskItem.tsx` - Individual task with actions
- `AddTaskForm.tsx` - Task creation form
- `LoadingSpinner.tsx` - Loading indicator
- `ErrorMessage.tsx` - Error display
- `ThemeToggle.tsx` - Dark/light mode switch

### Utilities (`lib/`)
- `api-client.ts` - HTTP client with JWT authentication
- `auth.ts` - JWT decode, validation, storage utilities

### Types (`types/`)
- `task.ts` - TypeScript interfaces for Task, User, API responses

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Type check
npx tsc --noEmit
```

## API Integration

All API requests automatically include JWT token via `api-client.ts`:

```typescript
import { api } from '@/lib/api-client';

// GET request
const tasks = await api.get(`/api/${userId}/tasks`);

// POST request
const newTask = await api.post(`/api/${userId}/tasks`, {
  title: 'Task title',
  description: 'Optional description'
});

// PATCH request
await api.patch(`/api/${userId}/tasks/${taskId}`, {
  title: 'Updated title'
});

// DELETE request
await api.delete(`/api/${userId}/tasks/${taskId}`);
```

## Security

- JWT tokens stored in localStorage (client-side)
- Tokens automatically included in Authorization header
- User ID extracted from JWT (not URL parameters)
- Protected routes redirect to signin when unauthenticated
- Token expiration handled with re-authentication

## Responsive Breakpoints

```css
Mobile:  375px - 767px
Tablet:  768px - 1023px
Desktop: 1024px+
```

## Accessibility Features

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation (Tab, Enter, Escape)
- Focus management
- Screen reader announcements
- High contrast text
- Touch targets 44x44px minimum

## Troubleshooting

### "Failed to fetch" / Connection Error
- Verify backend is running on port 8001
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Restart frontend after changing `.env.local`

### "Authentication failed" / Invalid Token
- Check `BETTER_AUTH_SECRET` matches backend
- Clear localStorage and login again
- Verify token hasn't expired (7 day expiry)

### Environment Variables Not Working
- Ensure file is named `.env.local` (not `.env`)
- Restart dev server after changes
- Check variables are prefixed with `NEXT_PUBLIC_` for client-side access

### Tasks Not Loading
- Open browser console (F12) for error details
- Verify JWT token exists in localStorage
- Check Network tab for API response errors
- Ensure backend `/api/{user_id}/tasks` endpoint is working

## Production Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Environment Variables for Production
- Update `NEXT_PUBLIC_API_URL` to production backend URL
- Update `DATABASE_URL` to production Neon database
- Keep `BETTER_AUTH_SECRET` synchronized with backend

## Contributing

This project follows Spec-Driven Development (SDD):
- All features defined in `specs/001-user-auth/spec.md`
- Implementation plan in `specs/001-user-auth/plan.md`
- Tasks tracked in `specs/001-user-auth/tasks.md`

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)

## License

Hackathon Project - Internal Use
