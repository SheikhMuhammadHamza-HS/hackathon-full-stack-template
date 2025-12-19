# Signup UI Documentation

## Overview

Production-ready signup page for multi-user authentication system built with Next.js 16+ (App Router), React 19, TypeScript, and Tailwind CSS.

## Features

### Form Validation
- **Client-side validation**:
  - Name: Required, minimum 2 characters
  - Email: Required, valid email format
  - Password: Required, minimum 8 characters, must contain uppercase, lowercase, and number
- **Server-side error handling**:
  - Duplicate email detection
  - General API error messages
- **Real-time error clearing**: Errors clear when user starts typing

### User Experience
- **Loading states**: Button disabled with spinner during API request
- **Responsive design**: Mobile-first (375px+), scales to desktop
- **Touch targets**: Minimum 44x44px for mobile accessibility
- **Auto-lowercase email**: Ensures consistency in email storage
- **Auto-trim inputs**: Prevents whitespace issues

### Accessibility
- **ARIA attributes**: Proper `role`, `aria-invalid`, `aria-describedby`
- **Keyboard navigation**: Full keyboard support, visible focus states
- **Screen reader support**: Error announcements with `aria-live="polite"`
- **Semantic HTML**: Proper form elements and labels
- **Required field indicators**: Visual (*) and screen reader labels

### Security
- **Token storage**: JWT stored in localStorage on success
- **No hardcoded credentials**: All configuration via environment variables
- **Password masking**: Type="password" for input field
- **HTTPS-ready**: Works with secure connections

## File Structure

```
frontend/
├── app/
│   └── auth/
│       └── signup/
│           ├── page.tsx          # Main signup page component
│           └── README.md         # This file
├── components/
│   ├── AuthForm.tsx              # Reusable auth form container + InputField + SubmitButton
│   ├── ErrorMessage.tsx          # Error display component
│   ├── LoadingSpinner.tsx        # Loading spinner component
│   └── index.ts                  # Component exports
└── lib/
    ├── api-client.ts             # API client with auth handling
    └── types/
        └── auth.ts               # TypeScript type definitions
```

## Components

### 1. AuthForm (`components/AuthForm.tsx`)
Reusable authentication form container with consistent styling.

**Props**:
```typescript
interface AuthFormProps {
  title: string;              // Form title
  description?: string;       // Optional description
  children: ReactNode;        // Form content
  footer?: ReactNode;         // Optional footer (links, etc.)
  backLink?: { href: string; label: string }; // Optional back navigation
  onSubmit: FormEventHandler<HTMLFormElement>; // Form submission handler
}
```

**Features**:
- Centered layout with max-width container
- Card-style design with shadow and border
- Dark mode support
- Responsive padding and spacing

### 2. InputField (`components/AuthForm.tsx`)
Reusable form input with label, validation, and accessibility.

**Props**:
```typescript
interface InputFieldProps {
  label: string;              // Field label
  error?: string | null;      // Validation error message
  helperText?: string;        // Optional helper text
  // ...all standard input attributes
}
```

**Features**:
- Auto-generated IDs for accessibility
- Error state styling (red border)
- Required field indicator (*)
- Helper text below input
- Disabled state support

### 3. SubmitButton (`components/AuthForm.tsx`)
Primary button for form submissions with loading state.

**Props**:
```typescript
interface SubmitButtonProps {
  isLoading?: boolean;        // Loading state
  loadingText?: string;       // Text during loading
  children: ReactNode;        // Button text
  disabled?: boolean;         // Disabled state
}
```

**Features**:
- Full-width responsive button
- Loading spinner animation
- Disabled state during submission
- Minimum 44px height for touch targets
- Focus ring for keyboard navigation

### 4. ErrorMessage (`components/ErrorMessage.tsx`)
Standalone error message component (currently unused in signup, available for future use).

### 5. LoadingSpinner (`components/LoadingSpinner.tsx`)
Reusable loading spinner with size variants (used internally by SubmitButton).

## API Integration

### Endpoint
```
POST ${NEXT_PUBLIC_API_URL}/api/auth/signup
```

### Request Body
```typescript
{
  name: string,      // User's full name (trimmed)
  email: string,     // Email address (trimmed, lowercase)
  password: string   // Password (minimum 8 chars)
}
```

### Response (Success - 200/201)
```typescript
{
  user: {
    id: string,
    email: string,
    name: string,
    created_at: string,
    updated_at: string
  },
  token: string      // JWT authentication token
}
```

### Error Handling
- **400**: Validation errors (duplicate email, invalid format)
- **500**: Server errors
- Errors parsed from `error.message` in API client

## Usage

### Accessing the Page
```
http://localhost:3000/auth/signup
```

### Environment Variables
Required in `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Navigation Flow
1. User fills form → submits
2. Validation runs (client-side)
3. API request sent
4. On success:
   - Token stored in localStorage as `auth_token`
   - Redirect to `/dashboard`
5. On error:
   - Error message displayed
   - Form remains filled
   - User can retry

## Styling Guidelines

### Tailwind Classes Organization
Classes organized in this order:
1. Layout (flex, grid, block)
2. Spacing (margin, padding)
3. Typography (text-size, font-weight)
4. Colors (text-color, bg-color, border-color)
5. States (hover, focus, disabled)

### Responsive Breakpoints
- Mobile: 375px - 767px (base, no prefix)
- Tablet: 768px+ (md:)
- Desktop: 1024px+ (lg:)

### Color Scheme
- Primary action: Blue (`blue-600`)
- Error states: Red (`red-600`)
- Text: Gray scale (`gray-900` to `gray-400`)
- Dark mode: Automatic via `dark:` prefix

## Testing Checklist

### Manual Testing
- [ ] Name field validation (empty, too short)
- [ ] Email field validation (empty, invalid format)
- [ ] Password field validation (empty, too short, missing requirements)
- [ ] Duplicate email error handling
- [ ] Loading state (button disabled, spinner visible)
- [ ] Successful signup (token stored, redirect works)
- [ ] Mobile responsiveness (375px width)
- [ ] Dark mode appearance
- [ ] Keyboard navigation (tab through all fields)
- [ ] Screen reader announcements (test with screen reader)

### Error Scenarios
- [ ] Network failure
- [ ] API timeout
- [ ] Invalid credentials
- [ ] Server error (500)
- [ ] Duplicate email

## Future Enhancements

### Potential Improvements
1. **Password strength indicator**: Visual feedback on password quality
2. **Email verification**: Send verification email after signup
3. **Social login**: OAuth integration (Google, GitHub)
4. **Terms acceptance**: Checkbox for terms and privacy policy
5. **CAPTCHA**: Bot protection
6. **Username availability check**: Real-time email validation
7. **Multi-step form**: Split into multiple screens
8. **Progressive profiling**: Collect additional info after signup

### Accessibility Improvements
1. **Focus trap**: Keep focus within form modal
2. **Announce loading**: Screen reader feedback during API call
3. **Error summary**: List all errors at top of form
4. **High contrast mode**: Additional styling for high contrast

## Code Quality

### Standards Met
- ✅ TypeScript strict mode
- ✅ Comprehensive JSDoc comments
- ✅ Consistent naming conventions
- ✅ No hardcoded strings (i18n-ready)
- ✅ Proper error boundaries
- ✅ Semantic HTML elements
- ✅ WCAG AA color contrast
- ✅ Mobile-first responsive design

### Performance
- Client Component only where needed (form interactions)
- Minimal re-renders (controlled inputs)
- No unnecessary API calls
- Efficient error state management

## Related Documentation
- [API Client Documentation](../../lib/api-client.ts)
- [Auth Types](../../lib/types/auth.ts)
- [Component Library](../../components/README.md)
