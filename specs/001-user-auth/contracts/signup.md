# API Contract: User Signup

**Endpoint**: `POST /api/auth/signup`
**Purpose**: Create new user account with email and password
**Authentication**: None required (public endpoint)
**Version**: 1.0.0

## Request

### HTTP Method
```
POST
```

### URL
```
/api/auth/signup
```

### Headers
```
Content-Type: application/json
```

### Request Body Schema
```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

### Field Specifications

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | 1-100 characters, no whitespace-only | User's display name |
| `email` | string | Yes | Valid RFC 5322 email format, unique | User's email address |
| `password` | string | Yes | Minimum 8 characters | User's password (will be hashed) |

### Request Example
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

### Validation Rules

1. **Name Validation**:
   - Trim whitespace before validation
   - Reject if empty after trimming
   - Maximum 100 characters
   - No special character restrictions (allow international names)

2. **Email Validation**:
   - Must match RFC 5322 email format
   - Case-insensitive (stored as lowercase)
   - Must be unique across all users
   - Maximum 254 characters (RFC 5321 limit)

3. **Password Validation**:
   - Minimum 8 characters
   - No maximum length (bcrypt handles truncation at 72 chars)
   - No complexity requirements in Phase II (add in Phase III if needed)

---

## Response

### Success Response (201 Created)

**Status Code**: `201 Created`

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

#### 400 Bad Request - Duplicate Email
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Email already registered"
}
```

**Trigger**: User attempts to signup with an email that already exists in the database.

---

#### 400 Bad Request - Invalid Email Format
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Please enter a valid email"
}
```

**Trigger**: Email does not match RFC 5322 format (e.g., "notanemail", "user@", "@example.com").

---

#### 400 Bad Request - Password Too Short
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Password must be at least 8 characters"
}
```

**Trigger**: Password is less than 8 characters.

---

#### 400 Bad Request - Missing Name
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Name is required"
}
```

**Trigger**: Name field is missing, empty, or whitespace-only after trimming.

---

#### 400 Bad Request - Name Too Long
**Status Code**: `400 Bad Request`

**Body**:
```json
{
  "error": "Name must be 100 characters or less"
}
```

**Trigger**: Name exceeds 100 characters.

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

### Password Hashing
- Better Auth automatically hashes password using bcrypt before storing
- Plaintext password NEVER stored in database
- Password hash NEVER returned in API responses

### Email Normalization
- Email converted to lowercase before uniqueness check
- Prevents duplicate accounts with case variations (Alice@example.com vs alice@example.com)

### Token Generation
- JWT token generated immediately upon successful signup
- Token signed with BETTER_AUTH_SECRET (HMAC-SHA256)
- Token expiry set to 7 days from issuance
- Frontend stores token for subsequent authenticated requests

### User ID Generation
- UUID v4 generated for user ID (non-sequential)
- Prevents user enumeration attacks
- Universally unique across all users

---

## Frontend Integration

### Making the Request (TypeScript/Next.js)
```typescript
// lib/api-client.ts
async function signup(name: string, email: string, password: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, email, password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Signup failed')
  }

  return await response.json()
}
```

### Handling Success
```typescript
const { user, token } = await signup('Alice Johnson', 'alice@example.com', 'password123')

// Store token (localStorage for Phase II, httpOnly cookie for Phase III)
localStorage.setItem('auth_token', token)

// Store user info
localStorage.setItem('user', JSON.stringify(user))

// Redirect to dashboard
router.push('/dashboard')
```

### Handling Errors
```typescript
try {
  await signup(name, email, password)
} catch (error) {
  // Display error message to user
  setErrorMessage(error.message)
  // e.g., "Email already registered"
}
```

---

## Backend Implementation Reference

### FastAPI Endpoint (Pseudocode)
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr

router = APIRouter()

class SignupRequest(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True)
    email: EmailStr
    password: constr(min_length=8)

@router.post("/api/auth/signup", status_code=201)
async def signup(data: SignupRequest):
    # 1. Check if email already exists
    existing_user = await db.get_user_by_email(data.email.lower())
    if existing_user:
        raise HTTPException(400, "Email already registered")

    # 2. Create user via Better Auth
    user = await better_auth.create_user(
        name=data.name,
        email=data.email.lower(),
        password=data.password  # Better Auth hashes this
    )

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

**Test Case 1: Successful Signup**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@example.com",
  "password": "password123"
}

Expected: 201 Created with user object and JWT token
```

**Test Case 2: Duplicate Email**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "name": "Another User",
  "email": "test@example.com",  // Same email as Test Case 1
  "password": "password456"
}

Expected: 400 Bad Request with error "Email already registered"
```

**Test Case 3: Invalid Email**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "name": "Test User",
  "email": "notanemail",
  "password": "password123"
}

Expected: 400 Bad Request with error "Please enter a valid email"
```

**Test Case 4: Short Password**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "name": "Test User",
  "email": "test2@example.com",
  "password": "short"
}

Expected: 400 Bad Request with error "Password must be at least 8 characters"
```

**Test Case 5: Missing Name**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "email": "test3@example.com",
  "password": "password123"
}

Expected: 400 Bad Request with error "Name is required"
```

---

## Security Considerations

1. **Password Storage**: Plaintext password NEVER stored; bcrypt hash stored instead
2. **Email Privacy**: Generic error message for duplicate email (don't reveal account existence to attackers)
3. **Rate Limiting**: Consider adding rate limiting in Phase III to prevent signup spam
4. **CAPTCHA**: Consider adding CAPTCHA in Phase III to prevent bot signups
5. **Token Security**: JWT signed with secret, 7-day expiry enforced

---

## Related Endpoints

- [POST /api/auth/signin](./signin.md) - Sign in with existing account
- [POST /api/auth/signout](./signout.md) - Sign out and invalidate token

---

**Contract Version**: 1.0.0
**Last Updated**: 2025-12-17
**Status**: Final
