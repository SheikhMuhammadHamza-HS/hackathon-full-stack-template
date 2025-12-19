# Dashboard Page

## Overview

Protected landing page displayed after successful user authentication. Provides user profile information and sign-out functionality.

## Location

`frontend/app/dashboard/page.tsx`

## Features

### Authentication
- JWT token validation on page load
- Automatic redirect to `/auth/signin` if unauthenticated or token expired
- Token expiration checking via utility functions
- Secure sign-out flow with localStorage cleanup

### User Interface
- Welcome message with user's name
- User profile cards displaying:
  - Full name
  - Email address
  - User ID (for debugging/admin purposes)
- Sign out button in header
- Placeholder section for future todo management
- Loading state during authentication check
- Signing out state during logout process

### Design
- Mobile-first responsive layout
- Dark mode support (respects system preference)
- Tailwind CSS styling
- Semantic HTML structure
- WCAG AA accessibility compliance
- Professional, clean design

## Dependencies

### New Files Created
- `frontend/lib/auth.ts` - JWT authentication utilities
- `frontend/app/dashboard/page.tsx` - Dashboard page component

### Existing Dependencies
- `next/navigation` - Next.js App Router navigation
- `@/lib/auth` - JWT utilities (newly created)

## JWT Token Structure

The JWT token stored in localStorage as `auth_token` contains:

```typescript
{
  user_id: string;    // Unique user identifier
  sub: string;        // Subject (user identifier)
  email: string;      // User email address
  name: string;       // User full name
  iat: number;        // Issued at timestamp
  exp: number;        // Expiration timestamp
}
```

## Authentication Flow

1. **Page Load**
   - Extract JWT token from localStorage (`auth_token`)
   - Decode and validate token
   - Check expiration status
   - If invalid/expired/missing: redirect to `/auth/signin`
   - If valid: display dashboard with user info

2. **Sign Out**
   - User clicks "Sign Out" button
   - Remove `auth_token` from localStorage
   - Redirect to `/auth/signin`
   - Optional: Display confirmation message (future enhancement)

## API Integration

### Current Implementation
Client-side only authentication check. No server-side API calls required for dashboard display.

### Future Enhancement
Optional sign-out endpoint call:
```typescript
POST /api/auth/signout
Authorization: Bearer <token>
```

## Route Protection

This is a **protected route**:
- Requires valid JWT token
- Redirects unauthenticated users to `/auth/signin`
- Validates token expiration on mount
- No middleware required (client-side protection)

## Usage

### Accessing the Dashboard
Users are automatically redirected to `/dashboard` after successful sign-in.

Direct navigation:
```
http://localhost:3000/dashboard
```

### Sign Out
Click the "Sign Out" button in the header to log out and return to sign-in page.

## Security Considerations

1. **Client-Side Token Decoding**
   - Token is decoded client-side for UI display only
   - Does NOT verify signature (backend must still validate)
   - Used only for showing user information

2. **Token Storage**
   - JWT stored in localStorage as `auth_token`
   - Automatically cleared on sign-out
   - Expired tokens automatically removed

3. **Route Protection**
   - Client-side redirect to sign-in if no token
   - Protected API endpoints must validate tokens server-side
   - Future: Consider middleware for SSR protection

## Styling

### Tailwind CSS Classes Organization
Classes are organized by category for maintainability:
1. Layout (flex, grid, positioning)
2. Spacing (padding, margin)
3. Typography (font size, weight)
4. Colors (background, text, borders)
5. States (hover, focus, disabled, dark mode)

### Responsive Breakpoints
- Mobile: Default (< 640px)
- Tablet: `sm:` (≥ 640px)
- Desktop: `lg:` (≥ 1024px)

### Dark Mode
Dark mode styles use `dark:` prefix and are based on system preference (automatic).

## Accessibility

- Semantic HTML elements (`header`, `main`, `footer`, `section`)
- ARIA labels for interactive elements
- Focus states with visible indicators
- Color contrast meets WCAG AA standards
- Loading states with status announcements
- Keyboard navigable

## Future Enhancements

### Phase III: Todo Management
- Todo list display
- CRUD operations for todos
- Filter and search functionality
- Todo completion tracking

### Additional Features
- User profile editing
- Password change
- Session management
- Toast notifications for sign-out confirmation
- Server-side rendering with middleware protection
- Refresh token implementation

## Testing Checklist

- [ ] Dashboard loads successfully after sign-in
- [ ] User information displays correctly (name, email)
- [ ] Sign out button removes token and redirects
- [ ] Unauthenticated access redirects to sign-in
- [ ] Expired token triggers redirect
- [ ] Loading state displays during auth check
- [ ] Responsive layout works on mobile/tablet/desktop
- [ ] Dark mode toggles correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces content properly

## Related Files

- `frontend/lib/auth.ts` - Authentication utilities
- `frontend/lib/api-client.ts` - API client with JWT integration
- `frontend/app/auth/signin/page.tsx` - Sign-in page
- `frontend/app/auth/signup/page.tsx` - Sign-up page
- `backend/app/routers/auth.py` - Authentication API endpoints

## Development Commands

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint code
npm run lint
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Default: `http://localhost:8000` if not set.
