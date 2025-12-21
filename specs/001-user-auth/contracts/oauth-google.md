# API Contract: Google OAuth Authentication

## Overview
Google OAuth 2.0 endpoints for social authentication. Allows users to sign in/sign up using their Google account.

## Endpoints

### 1. Initiate Google OAuth Login

**Endpoint**: `GET /api/auth/google/login`

**Description**: Redirects user to Google consent screen to authorize the application.

**Request Headers**: None required

**Query Parameters**: None

**Response**:
- **Type**: HTTP 302 Redirect
- **Location**: Google OAuth authorization URL with generated state parameter

**Success Response**:
```
HTTP/1.1 302 Found
Location: https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&state=...&scope=openid+email+profile&prompt=select_account
```

**Error Responses**:

- **503 Service Unavailable** - OAuth not configured
```json
{
  "detail": "Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
}
```

**Security**:
- State parameter generated using `secrets.token_urlsafe(32)` for CSRF protection
- State token stored server-side with 5-minute expiry

---

### 2. Google OAuth Callback

**Endpoint**: `GET /api/auth/google/callback`

**Description**: Handles OAuth callback from Google, exchanges authorization code for access token, creates/updates user account, and returns JWT.

**Request Headers**: None required

**Query Parameters**:
- `code` (string, required): Authorization code from Google
- `state` (string, required): CSRF protection token

**Response Type**: HTTP 302 Redirect to frontend with token

**Success Response**:
```
HTTP/1.1 302 Found
Location: http://localhost:3000/auth/callback?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&provider=google
```

**Token Payload** (JWT in URL):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1735689600
}
```

**User Data Retrieved from Google**:
- `email`: User's primary email
- `name`: User's full name
- `picture`: Profile picture URL
- `sub`: Google's unique user ID

**Database Behavior**:
- **New User**: Creates user with `oauth_provider='google'`, `oauth_id`, `profile_picture`, `password_hash=null`
- **Existing User (password-based)**: Updates with `oauth_provider='google'`, `oauth_id`, `profile_picture`
- **Existing User (OAuth)**: Logs in without modification

**Error Responses**:

- **400 Bad Request** - Invalid state parameter (CSRF attack detected)
```json
{
  "detail": "Invalid state parameter. Possible CSRF attack."
}
```

- **400 Bad Request** - Invalid authorization code
```json
{
  "detail": "Invalid authorization code"
}
```

- **400 Bad Request** - Failed to fetch user info
```json
{
  "detail": "Failed to fetch user info from Google"
}
```

- **400 Bad Request** - Missing email or user ID
```json
{
  "detail": "Email or user ID not provided by Google"
}
```

- **500 Internal Server Error** - Server error during OAuth process
```json
{
  "detail": "An error occurred during Google authentication"
}
```

---

## OAuth Flow Diagram

```
1. User clicks "Sign in with Google" button
   ↓
2. Frontend redirects to: GET /api/auth/google/login
   ↓
3. Backend generates state token and redirects to Google
   ↓
4. User authorizes on Google consent screen
   ↓
5. Google redirects back to: GET /api/auth/google/callback?code=...&state=...
   ↓
6. Backend validates state, exchanges code for token
   ↓
7. Backend fetches user info from Google API
   ↓
8. Backend creates/updates user in database
   ↓
9. Backend generates JWT token
   ↓
10. Backend redirects to frontend: /auth/callback?token=...&provider=google
    ↓
11. Frontend stores token and redirects to dashboard
```

---

## Security Considerations

### CSRF Protection
- State parameter generated using cryptographically secure random token
- State stored server-side and validated on callback
- State token consumed after use (single-use)

### Token Security
- JWT tokens signed with `BETTER_AUTH_SECRET`
- 7-day expiry (configurable)
- User ID, email, and name included in payload

### Account Linking
- Email-based account matching (case-insensitive)
- OAuth info added to existing password-based accounts
- No duplicate accounts created for same email

### Data Privacy
- Only essential scopes requested: `openid email profile`
- Profile pictures stored as URLs (not downloaded)
- OAuth tokens not persisted (only used during authentication)

---

## Frontend Integration

### Initiate OAuth Flow
```javascript
// Redirect to Google OAuth
window.location.href = 'http://localhost:8000/api/auth/google/login';
```

### Handle OAuth Callback
```javascript
// In /auth/callback page
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const provider = params.get('provider');

if (token && provider === 'google') {
  localStorage.setItem('authToken', token);
  // Fetch user profile or redirect to dashboard
  window.location.href = '/dashboard';
}
```

---

## Testing

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Visit: `http://localhost:8000/api/auth/google/login`
3. Authorize on Google
4. Verify redirect to callback with token
5. Check database for new user record

### Test Cases
- ✅ New user signup via Google
- ✅ Existing user (password) login via Google (account linking)
- ✅ Existing user (Google) repeat login
- ✅ Invalid state parameter rejection
- ✅ Invalid authorization code handling
- ✅ Email retrieval from Google

---

## Environment Variables Required

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
BETTER_AUTH_SECRET=your-jwt-secret-key
```

---

## Rate Limiting Recommendations

- `/api/auth/google/login`: 10 requests per minute per IP
- `/api/auth/google/callback`: 20 requests per minute per IP (to handle retries)

---

## Monitoring & Logging

### Success Metrics
- Track successful OAuth logins
- Monitor new user registrations via Google
- Track account linking events

### Error Metrics
- Track CSRF validation failures (potential attacks)
- Monitor invalid authorization code errors (user abandonment)
- Alert on repeated failures for same user

### Log Examples
```
INFO: Google OAuth login initiated for state=abc123...
INFO: User user@example.com authenticated via Google (new account)
WARN: Invalid state parameter in Google callback (potential CSRF)
ERROR: Failed to exchange Google authorization code: InvalidGrantError
```
