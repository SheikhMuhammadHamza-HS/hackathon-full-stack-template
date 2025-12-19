# API Contract: User Sign Out

**Endpoint**: `POST /api/auth/signout`
**Purpose**: Sign out user and clear authentication state
**Authentication**: Optional (token validation not required in Phase II)
**Version**: 1.0.0

## Request

### HTTP Method
```
POST
```

### URL
```
/api/auth/signout
```

### Headers
```
Content-Type: application/json
Authorization: Bearer {token}  (optional in Phase II)
```

### Request Body Schema
```json
{}
```

**Note**: Empty body. Token extracted from Authorization header if present.

### Request Example
```
POST /api/auth/signout HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{}
```

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
  "message": "string"
}
```

**Success Example**:
```json
{
  "message": "Signed out successfully"
}
```

**Behavior**: Confirms signout request received. Frontend is responsible for removing token from storage.

---

### Error Responses

#### 401 Unauthorized (Phase III Feature)
**Status Code**: `401 Unauthorized`

**Body**:
```json
{
  "error": "Authentication required"
}
```

**Trigger**: Token missing or invalid (only enforced in Phase III if token blacklist implemented).

**Phase II Note**: This error is NOT returned in Phase II. Signout is client-side only (token removal from localStorage).

---

## Behavior Specifications

### Phase II Implementation (Client-Side Signout)
- Backend endpoint returns success immediately
- Frontend removes token from localStorage
- Frontend redirects to signin page
- No server-side token invalidation (JWT remains valid until expiry)

**Why Client-Side Only**:
- JWT tokens are stateless (server doesn't track active tokens)
- Token blacklist adds complexity and database overhead
- 7-day expiry provides reasonable security window
- Phase III can add token blacklist if needed

### Phase III Enhancement (Server-Side Token Blacklist)
- Backend maintains blacklist of revoked tokens (Redis or database)
- On signout, add token to blacklist
- JWT middleware checks blacklist before accepting token
- Enables "sign out all devices" feature
- Adds latency to every request (blacklist lookup)

---

## Frontend Integration

### Making the Request (TypeScript/Next.js)
```typescript
// lib/api-client.ts
async function signout() {
  // Phase II: Client-side signout (no backend call needed)
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
  router.push('/auth/signin')

  // Optional: Call backend for consistency (future-proofing)
  try {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    })
  } catch (error) {
    // Ignore errors (token already removed from frontend)
    console.log('Signout API call failed, but local token cleared')
  }
}
```

### Handling Success
```typescript
// User clicks "Sign Out" button
await signout()

// Token removed from localStorage
// User redirected to signin page
// Attempting to access protected routes will redirect back to signin
```

### Browser Back Button Protection
```typescript
// Middleware to protect routes after signout
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token') ||
                 request.headers.get('authorization')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/auth/signin', request.url))
  }

  return NextResponse.next()
}
```

---

## Backend Implementation Reference

### FastAPI Endpoint (Pseudocode - Phase II)
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/auth/signout")
async def signout():
    # Phase II: No server-side action needed
    # Frontend handles token removal

    return {"message": "Signed out successfully"}
```

### FastAPI Endpoint (Pseudocode - Phase III with Token Blacklist)
```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import verify_jwt

router = APIRouter()

@router.post("/api/auth/signout")
async def signout(user_id: str = Depends(verify_jwt), token: str = Depends(get_token)):
    # Phase III: Add token to blacklist
    await redis.setex(
        f"blacklist:{token}",
        60 * 60 * 24 * 7,  # 7 days (token expiry)
        "revoked"
    )

    return {"message": "Signed out successfully"}
```

---

## Testing

### Manual Testing (Postman/Thunder Client)

**Test Case 1: Successful Signout (Phase II)**
```
POST http://localhost:8000/api/auth/signout
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{}

Expected: 200 OK with message "Signed out successfully"
```

**Test Case 2: Signout Without Token (Phase II)**
```
POST http://localhost:8000/api/auth/signout
Content-Type: application/json

{}

Expected: 200 OK (no error in Phase II)
```

**Test Case 3: Verify Token Removed (Frontend)**
```
1. Sign in (get token)
2. Sign out (call signout endpoint)
3. Check localStorage.getItem('auth_token')
   Expected: null (token removed)
4. Attempt to access /dashboard
   Expected: Redirect to /auth/signin
```

**Test Case 4: Token Still Valid After Signout (Phase II)**
```
1. Sign in (get token)
2. Sign out (token removed from localStorage)
3. Manually use old token in API request
   Expected: Request succeeds (token still valid until expiry)
   Note: Phase III will blacklist token, causing 401 error
```

---

## Security Considerations

### Phase II Limitations
1. **Token Remains Valid**: JWT token still accepted by backend until expiry
2. **No Device Logout**: Cannot sign out other devices remotely
3. **Stolen Token Risk**: If attacker steals token before signout, they can use it

### Phase II Security Posture (Acceptable Tradeoffs)
- ✅ Simple implementation (no Redis/database blacklist needed)
- ✅ Fast signout (client-side only, no API latency)
- ✅ No single point of failure (no blacklist database to maintain)
- ❌ Token usable if stolen before signout (7-day window)
- ❌ Cannot revoke token remotely

### Phase III Enhancements
- Token blacklist (Redis recommended for speed)
- "Sign out all devices" feature
- Audit log of signin/signout events
- Suspicious activity detection (multiple signouts, unusual locations)

---

## Edge Cases

### Scenario: User Closes Browser Without Signing Out
- **Behavior**: Token remains in localStorage
- **On Return**: User still signed in (token not expired)
- **Security**: Acceptable on personal device, risky on shared device
- **Mitigation**: Educate users to sign out on shared devices

### Scenario: Token Expires During Active Session
- **Behavior**: Next API request returns 401 "Token expired"
- **Frontend Action**: Redirect to signin, preserve return URL
- **User Experience**: Re-authenticate and continue

### Scenario: Multiple Browser Tabs Open
- **Behavior**: Signout in one tab removes token from localStorage
- **Other Tabs**: Token reference cleared (shared localStorage)
- **Next Request**: All tabs redirect to signin (token missing)

---

## Related Endpoints

- [POST /api/auth/signup](./signup.md) - Create new user account
- [POST /api/auth/signin](./signin.md) - Sign in with existing account

---

## Migration Path to Token Blacklist (Phase III)

### Backend Changes
1. Add Redis for token blacklist storage
2. Update signout endpoint to add token to blacklist
3. Update JWT middleware to check blacklist before accepting token
4. Add TTL on blacklist entries (match token expiry)

### Frontend Changes
- No changes needed (same API contract)
- Benefit: Tokens immediately invalidated server-side

### Redis Blacklist Schema
```
Key: blacklist:{jwt-token-string}
Value: "revoked"
TTL: 604800 seconds (7 days, matches token expiry)
```

### Performance Impact
- Additional Redis lookup on every authenticated request (~1-2ms)
- Acceptable tradeoff for enhanced security

---

**Contract Version**: 1.0.0
**Last Updated**: 2025-12-17
**Status**: Final
**Phase II Implementation**: Client-side signout only
**Phase III Enhancement**: Token blacklist (optional)
