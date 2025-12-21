# API Contract: GitHub OAuth Authentication

## Overview
GitHub OAuth 2.0 endpoints for social authentication. Allows users to sign in/sign up using their GitHub account.

## Endpoints

### 1. Initiate GitHub OAuth Login

**Endpoint**: `GET /api/auth/github/login`

**Description**: Redirects user to GitHub authorization page to authorize the application.

**Request Headers**: None required

**Query Parameters**: None

**Response**:
- **Type**: HTTP 302 Redirect
- **Location**: GitHub OAuth authorization URL with generated state parameter

**Success Response**:
```
HTTP/1.1 302 Found
Location: https://github.com/login/oauth/authorize?client_id=...&redirect_uri=...&state=...&scope=user:email
```

**Error Responses**:

- **503 Service Unavailable** - OAuth not configured
```json
{
  "detail": "GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET."
}
```

**Security**:
- State parameter generated using `secrets.token_urlsafe(32)` for CSRF protection
- State token stored server-side with 5-minute expiry

---

### 2. GitHub OAuth Callback

**Endpoint**: `GET /api/auth/github/callback`

**Description**: Handles OAuth callback from GitHub, exchanges authorization code for access token, creates/updates user account, and returns JWT.

**Request Headers**: None required

**Query Parameters**:
- `code` (string, required): Authorization code from GitHub
- `state` (string, required): CSRF protection token

**Response Type**: HTTP 302 Redirect to frontend with token

**Success Response**:
```
HTTP/1.1 302 Found
Location: http://localhost:3000/auth/callback?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&provider=github
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

**User Data Retrieved from GitHub**:
- `id`: GitHub's unique numeric user ID
- `login`: GitHub username
- `name`: User's display name (fallback to `login` if not set)
- `avatar_url`: Profile picture URL
- `email`: Primary verified email (from `/user/emails` endpoint)

**Email Resolution Strategy**:
1. Look for primary + verified email
2. Fallback to any verified email
3. Return error if no verified email found

**Database Behavior**:
- **New User**: Creates user with `oauth_provider='github'`, `oauth_id`, `profile_picture`, `password_hash=null`
- **Existing User (password-based)**: Updates with `oauth_provider='github'`, `oauth_id`, `profile_picture`
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

- **400 Bad Request** - No access token received
```json
{
  "detail": "No access token received from GitHub"
}
```

- **400 Bad Request** - Missing email or user ID
```json
{
  "detail": "Email or user ID not provided by GitHub"
}
```

- **500 Internal Server Error** - Server error during OAuth process
```json
{
  "detail": "An error occurred during GitHub authentication"
}
```

---

## OAuth Flow Diagram

```
1. User clicks "Sign in with GitHub" button
   ↓
2. Frontend redirects to: GET /api/auth/github/login
   ↓
3. Backend generates state token and redirects to GitHub
   ↓
4. User authorizes on GitHub authorization page
   ↓
5. GitHub redirects back to: GET /api/auth/github/callback?code=...&state=...
   ↓
6. Backend validates state, exchanges code for access token
   ↓
7. Backend fetches user profile from GitHub API (/user)
   ↓
8. Backend fetches user emails from GitHub API (/user/emails)
   ↓
9. Backend selects primary verified email
   ↓
10. Backend creates/updates user in database
    ↓
11. Backend generates JWT token
    ↓
12. Backend redirects to frontend: /auth/callback?token=...&provider=github
    ↓
13. Frontend stores token and redirects to dashboard
```

---

## GitHub API Calls

### 1. Get User Profile
```
GET https://api.github.com/user
Authorization: Bearer {access_token}
Accept: application/vnd.github.v3+json
```

**Response**:
```json
{
  "id": 12345678,
  "login": "johndoe",
  "name": "John Doe",
  "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
  "email": null  // Often null if email is private
}
```

### 2. Get User Emails
```
GET https://api.github.com/user/emails
Authorization: Bearer {access_token}
Accept: application/vnd.github.v3+json
```

**Response**:
```json
[
  {
    "email": "john@example.com",
    "primary": true,
    "verified": true,
    "visibility": "private"
  },
  {
    "email": "john.doe@users.noreply.github.com",
    "primary": false,
    "verified": true,
    "visibility": null
  }
]
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
- Only essential scope requested: `user:email`
- Profile pictures stored as URLs (not downloaded)
- OAuth access tokens used only during authentication (not persisted)
- Respects user's email privacy settings

### Email Privacy Handling
- Requests `/user/emails` endpoint to get verified emails
- Selects primary verified email when available
- Falls back to any verified email if primary is not verified
- Rejects users with no verified emails (security measure)

---

## Frontend Integration

### Initiate OAuth Flow
```javascript
// Redirect to GitHub OAuth
window.location.href = 'http://localhost:8000/api/auth/github/login';
```

### Handle OAuth Callback
```javascript
// In /auth/callback page
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const provider = params.get('provider');

if (token && provider === 'github') {
  localStorage.setItem('authToken', token);
  // Fetch user profile or redirect to dashboard
  window.location.href = '/dashboard';
}
```

---

## Testing

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Visit: `http://localhost:8000/api/auth/github/login`
3. Authorize on GitHub
4. Verify redirect to callback with token
5. Check database for new user record

### Test Cases
- ✅ New user signup via GitHub
- ✅ Existing user (password) login via GitHub (account linking)
- ✅ Existing user (GitHub) repeat login
- ✅ Invalid state parameter rejection
- ✅ Invalid authorization code handling
- ✅ Email retrieval from private GitHub accounts
- ✅ Primary verified email selection
- ✅ Fallback to non-primary verified email
- ✅ Rejection of users without verified emails

### Test with Private Email
1. Go to GitHub Settings → Emails
2. Enable "Keep my email addresses private"
3. Try OAuth flow
4. Verify backend fetches email from `/user/emails` endpoint

---

## Environment Variables Required

```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
BETTER_AUTH_SECRET=your-jwt-secret-key
```

---

## Rate Limiting Recommendations

- `/api/auth/github/login`: 10 requests per minute per IP
- `/api/auth/github/callback`: 20 requests per minute per IP (to handle retries)

**Note**: GitHub API has its own rate limits (5,000 requests/hour for authenticated requests). OAuth flows count toward this limit but are unlikely to exceed it.

---

## Monitoring & Logging

### Success Metrics
- Track successful OAuth logins
- Monitor new user registrations via GitHub
- Track account linking events
- Monitor email privacy handling (private vs public emails)

### Error Metrics
- Track CSRF validation failures (potential attacks)
- Monitor invalid authorization code errors (user abandonment)
- Alert on repeated failures for same user
- Track users rejected due to no verified email

### Log Examples
```
INFO: GitHub OAuth login initiated for state=xyz789...
INFO: User johndoe@example.com authenticated via GitHub (new account)
INFO: GitHub email retrieved from /user/emails (private email)
WARN: Invalid state parameter in GitHub callback (potential CSRF)
ERROR: Failed to exchange GitHub authorization code: InvalidGrantError
ERROR: GitHub user has no verified email addresses
```

---

## GitHub-Specific Considerations

### No Name Provided
- Some users don't set a display name on GitHub
- Backend falls back to `login` (username) as name

### Email Privacy
- Many users enable "Keep my email addresses private"
- Backend automatically fetches emails from `/user/emails`
- Only verified emails are considered for security

### Organization Membership
- Future enhancement: Could request `read:org` scope to check organization membership
- Useful for B2B applications with team-based access

### Two-Factor Authentication (2FA)
- GitHub handles 2FA during authorization
- No additional handling needed in backend
- Users with 2FA enabled will be prompted during OAuth flow

---

## Comparison: GitHub vs Google OAuth

| Feature | GitHub | Google |
|---------|--------|--------|
| Email in profile | Often null (private) | Always provided |
| Additional API call | `/user/emails` required | Not needed |
| Profile picture | `avatar_url` | `picture` |
| User ID field | `id` (numeric) | `sub` (string) |
| Name fallback | `login` (username) | Always provided |
| 2FA handling | Automatic | Automatic |
| Scope | `user:email` | `openid email profile` |
