# API Contract: User Sign In

**Endpoint**: `POST /api/auth/signin`
**Purpose**: Authenticate existing user and return JWT token
**Authentication**: None required (public endpoint)
**Version**: 1.0.0

## Request

### HTTP Method
```
POST
```

### URL
```
/api/auth/signin
```

### Headers
```
Content-Type: application/json
```

### Request Body Schema
```json
{
  "email": "string",
  "password": "string"
}
```

### Field Specifications

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string | Yes | Valid email format | User's registered email address |
| `password` | string | Yes | Any length | User's password |

### Request Example
```json
{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

### Validation Rules

1. **Email Validation**:
   - Must be present (non-empty)
   - Case-insensitive matching (converted to lowercase)
   - Format validation recommended but not required (backend handles invalid formats)

2. **Password Validation**:
   - Must be present (non-empty)
   - No length validation (backend verifies against stored hash)

---

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Headers**:
```
Content-Type: application/json
```

**Body Schema**:
```json
{
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  },
  "token": "string"
}
```

**Field Specifications**:

| Field | Type | Description |
|-------|------|-------------|
| `user.id` | string | UUID v4 identifier for the user |
| `user.email` | string | User's email address (lowercase) |
| `user.name` | string | User's display name |
| `token` | string | JWT authentication token (7-day expiry) |

**Success Example**:
```json
{
  "user": {
    "id": "a3bb189e-8bf9-3888-9912-ace4e6543002",
    "email": "alice@example.com",
    "name": "Alice Johnson"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTNiYjE4OWUtOGJmOS0zODg4LTk5MTItYWNlNGU2NTQzMDAyIiwiZW1haWwiOiJhbGljZUBleGFtcGxlLmNvbSIsIm5hbWUiOiJBbGljZSBKb2huc29uIiwiaWF0IjoxNzAzMTExMTExLCJleHAiOjE3MDM3MTU5MTF9.signature"
}
```

**JWT Token Payload** (decoded):
```json
{
  "user_id": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "iat": 1703111111,
  "exp": 1703715911
}
```

---

### Error Responses

#### 400 Bad Request - Invalid Credentials
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Invalid email or password"
}
```

**Trigger**: Email does not exist in database OR password does not match stored hash.

**Security Note**: Generic message intentionally does not reveal whether email exists (prevents user enumeration attacks).

---

#### 400 Bad Request - Missing Email
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Email is required"
}
```

**Trigger**: Email field is missing or empty.

---

#### 400 Bad Request - Missing Password
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Password is required"
}
```

**Trigger**: Password field is missing or empty.

---

#### 500 Internal Server Error - Database Failure
**Status Code**: `500 Internal Server Error`

**Body**:
```json
{
  "error": "Service temporarily unavailable, please try again"
}
```

**Trigger**: Database connection failure, Neon unavailable, or internal server error.

**Note**: Actual error details logged server-side, generic message returned to client for security.

---

## Behavior Specifications

### Password Verification
- Backend retrieves user by email (lowercase)
- Better Auth compares submitted password against stored bcrypt hash
- Timing-safe comparison prevents timing attacks
- Invalid credentials return generic error (no distinction between wrong email vs wrong password)

### Token Generation
- JWT token generated only after successful authentication
- Token signed with BETTER_AUTH_SECRET (HMAC-SHA256)
- Token expiry set to 7 days from issuance
- Frontend stores token for subsequent authenticated requests

### Failed Login Attempts
- Phase II: No lockout mechanism (add in Phase III if needed)
- Phase II: No rate limiting (add in Phase III to prevent brute force)
- Phase II: No audit logging (add in Phase III for security monitoring)

---

## Frontend Integration

### Making the Request (TypeScript/Next.js)
```typescript
// lib/api-client.ts
async function signin(email: string, password: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Sign in failed')
  }

  return await response.json()
}
```

### Handling Success
```typescript
const { user, token } = await signin('alice@example.com', 'password123')

// Store token (localStorage for Phase II, httpOnly cookie for Phase III)
localStorage.setItem('auth_token', token)

// Store user info
localStorage.setItem('user', JSON.stringify(user))

// Redirect to dashboard or originally requested page
const returnUrl = sessionStorage.getItem('returnUrl') || '/dashboard'
router.push(returnUrl)
```

### Handling Errors
```typescript
try {
  await signin(email, password)
} catch (error) {
  // Display error message to user
  setErrorMessage(error.message)
  // e.g., "Invalid email or password"
}
```

### Session Persistence
```typescript
// On app load, check if token exists and is valid
useEffect(() => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    // User is already signed in
    setIsAuthenticated(true)
  }
}, [])
```

---

## Backend Implementation Reference

### FastAPI Endpoint (Pseudocode)
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/signin")
async def signin(data: SigninRequest):
    # 1. Get user by email (case-insensitive)
    user = await db.get_user_by_email(data.email.lower())
    if not user:
        raise HTTPException(400, "Invalid email or password")

    # 2. Verify password via Better Auth
    is_valid = await better_auth.verify_password(data.password, user.password_hash)
    if not is_valid:
        raise HTTPException(400, "Invalid email or password")

    # 3. Generate JWT token
    token = create_jwt(user_id=user.id, email=user.email, name=user.name)

    # 4. Return user and token
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": token
    }
```

---

## Testing

### Manual Testing (Postman/Thunder Client)

**Test Case 1: Successful Sign In**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}

Expected: 200 OK with user object and JWT token
```

**Test Case 2: Wrong Password**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "wrongpassword"
}

Expected: 400 Bad Request with error "Invalid email or password"
```

**Test Case 3: Non-Existent Email**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "email": "nonexistent@example.com",
  "password": "password123"
}

Expected: 400 Bad Request with error "Invalid email or password"
```

**Test Case 4: Missing Email**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "password": "password123"
}

Expected: 400 Bad Request with error "Email is required"
```

**Test Case 5: Missing Password**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "email": "test@example.com"
}

Expected: 400 Bad Request with error "Password is required"
```

**Test Case 6: Case-Insensitive Email**
```
POST http://localhost:8000/api/auth/signin
Content-Type: application/json

{
  "email": "TEST@EXAMPLE.COM",  // Uppercase
  "password": "password123"
}

Expected: 200 OK (same as Test Case 1) - case-insensitive matching
```

---

## Security Considerations

1. **Generic Error Messages**: Always return "Invalid email or password" (never reveal if email exists)
2. **Timing-Safe Comparison**: Backend uses constant-time password comparison to prevent timing attacks
3. **No Account Enumeration**: Attackers cannot determine valid email addresses via error messages
4. **Password Security**: Plaintext password never logged or stored; only hash comparison performed
5. **Token Expiry**: 7-day expiry enforces periodic re-authentication
6. **Rate Limiting (Phase III)**: Add rate limiting to prevent brute-force password attacks
7. **Account Lockout (Phase III)**: Add temporary lockout after N failed attempts

---

## Edge Cases

### Scenario: User Signed In on Multiple Devices
- **Behavior**: Each device receives its own JWT token
- **Impact**: Tokens are independent; signing out on one device does not affect others (Phase II)
- **Future Enhancement**: Track active sessions and enable "sign out all devices" (Phase III)

### Scenario: Token Expired While User Active
- **Behavior**: Next API request returns 401 "Token expired, please log in again"
- **Frontend Action**: Redirect to signin page, preserve return URL
- **User Experience**: Re-authenticate and continue where they left off

### Scenario: User Changes Password (Phase III Feature)
- **Behavior**: Old tokens remain valid until expiry (JWT is stateless)
- **Future Enhancement**: Token blacklist or token versioning to invalidate old tokens (Phase III)

---

## Related Endpoints

- [POST /api/auth/signup](./signup.md) - Create new user account
- [POST /api/auth/signout](./signout.md) - Sign out and invalidate token

---

**Contract Version**: 1.0.0
**Last Updated**: 2025-12-17
**Status**: Final
