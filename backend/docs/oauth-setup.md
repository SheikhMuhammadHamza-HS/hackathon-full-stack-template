# OAuth Setup Guide

This guide explains how to configure Google and GitHub OAuth authentication for the Hackathon Todo application.

## Prerequisites

- Google Cloud Platform account
- GitHub account
- Backend application running (default: `http://localhost:8000`)
- Frontend application running (default: `http://localhost:3000`)

---

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: **"Hackathon Todo App"**
4. Click **"Create"**

### Step 2: Configure OAuth Consent Screen

1. Navigate to **APIs & Services** → **OAuth consent screen**
2. Select **"External"** user type → Click **"Create"**
3. Fill in required fields:
   - **App name**: Hackathon Todo App
   - **User support email**: your-email@example.com
   - **Developer contact email**: your-email@example.com
4. Click **"Save and Continue"**
5. Skip **Scopes** section → Click **"Save and Continue"**
6. Add test users if needed → Click **"Save and Continue"**
7. Review and click **"Back to Dashboard"**

### Step 3: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Web application"**
4. Configure:
   - **Name**: Hackathon Todo Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (frontend)
     - `http://localhost:8000` (backend)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/api/auth/google/callback`
5. Click **"Create"**
6. **Copy your credentials**:
   - Client ID (format: `xxxx.apps.googleusercontent.com`)
   - Client Secret

### Step 4: Add Credentials to Backend .env

```bash
# In backend/.env file
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Step 5: Test Google OAuth

1. Start your backend: `cd backend && uvicorn app.main:app --reload`
2. Start your frontend: `cd frontend && npm run dev`
3. Navigate to your signup page
4. Click **"Sign in with Google"** button
5. You should be redirected to Google consent screen
6. After authorization, you'll be redirected back to your application with a token

---

## GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"OAuth Apps"** → **"New OAuth App"**
3. Fill in application details:
   - **Application name**: Hackathon Todo App
   - **Homepage URL**: `http://localhost:3000`
   - **Application description**: (Optional) Full-stack todo application with OAuth
   - **Authorization callback URL**: `http://localhost:8000/api/auth/github/callback`
4. Click **"Register application"**

### Step 2: Generate Client Secret

1. After registration, you'll see your **Client ID**
2. Click **"Generate a new client secret"**
3. **Copy both**:
   - Client ID (format: `Iv1.xxxxxxxxxxxx`)
   - Client Secret (shown only once)

### Step 3: Add Credentials to Backend .env

```bash
# In backend/.env file
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Step 4: Test GitHub OAuth

1. Start your backend: `cd backend && uvicorn app.main:app --reload`
2. Start your frontend: `cd frontend && npm run dev`
3. Navigate to your signup page
4. Click **"Sign in with GitHub"** button
5. You should be redirected to GitHub authorization page
6. After authorization, you'll be redirected back to your application with a token

---

## Environment Variables Reference

Add these to your `backend/.env` file:

```bash
# OAuth Configuration - Google
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth Configuration - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth Redirect URI (must match configured callback URLs)
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
```

---

## Production Deployment Considerations

### Update Authorized Origins and Redirect URIs

When deploying to production, update your OAuth app configurations:

**Google Cloud Console:**
- Add production frontend URL to **Authorized JavaScript origins**
- Add production callback URL to **Authorized redirect URIs**
  - Example: `https://api.yourdomain.com/api/auth/google/callback`

**GitHub OAuth App:**
- Update **Homepage URL** to production frontend
- Update **Authorization callback URL** to production backend
  - Example: `https://api.yourdomain.com/api/auth/github/callback`

**Backend Environment Variables:**
```bash
OAUTH_REDIRECT_URI=https://api.yourdomain.com/api/auth
```

### Security Best Practices

1. **Never commit secrets to version control**
   - Use `.env` files (already in `.gitignore`)
   - Use environment variables in CI/CD pipelines

2. **Use HTTPS in production**
   - OAuth providers require HTTPS for production apps
   - Update all URLs to `https://`

3. **Implement rate limiting**
   - Prevent abuse of OAuth endpoints
   - Use middleware like `slowapi` or API gateway rate limiting

4. **Monitor OAuth usage**
   - Track failed authentication attempts
   - Set up alerts for suspicious activity

5. **Keep dependencies updated**
   - Regularly update `authlib` and `httpx`
   - Monitor security advisories

---

## Troubleshooting

### "OAuth not configured" Error

**Cause**: Missing environment variables

**Solution**:
1. Check `backend/.env` file exists
2. Verify `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` are set
3. Restart backend server after adding environment variables

### "Invalid state parameter" Error

**Cause**: CSRF token validation failed

**Solution**:
1. Clear browser cookies and try again
2. Ensure `SessionMiddleware` is configured in `main.py`
3. Check `BETTER_AUTH_SECRET` is set in `.env`

### "Invalid authorization code" Error

**Cause**: Authorization code already used or expired

**Solution**:
1. Don't refresh the callback page (codes are single-use)
2. Start OAuth flow again from the beginning
3. Check system clock is synchronized (OAuth tokens are time-sensitive)

### "redirect_uri_mismatch" Error

**Cause**: Callback URL doesn't match configured value

**Solution**:
1. **Google**: Check **Authorized redirect URIs** in Google Cloud Console
2. **GitHub**: Check **Authorization callback URL** in GitHub OAuth App settings
3. Ensure URLs match exactly (including `http`/`https`, port, and path)
4. Common mistake: `http://localhost:8000/api/auth/google/callback` vs `http://127.0.0.1:8000/api/auth/google/callback`

### GitHub Email Not Found

**Cause**: User's GitHub email is private

**Solution**:
- The backend automatically requests access to user emails
- Ensure GitHub OAuth app has `user:email` scope (already configured)
- User must have at least one verified email in GitHub settings

### User Already Exists with Different Provider

**Behavior**: If email exists in database (e.g., from password signup), OAuth will link the account

**Note**: Current implementation links OAuth to existing accounts automatically. If you need stricter control, modify the callback handlers in `app/routers/auth.py`

---

## API Endpoints

### Google OAuth Flow

1. **Initiate Login**
   ```
   GET /api/auth/google/login
   ```
   Redirects to Google consent screen

2. **Handle Callback**
   ```
   GET /api/auth/google/callback?code=xxx&state=xxx
   ```
   Exchanges code for token, creates/updates user, returns JWT

### GitHub OAuth Flow

1. **Initiate Login**
   ```
   GET /api/auth/github/login
   ```
   Redirects to GitHub authorization page

2. **Handle Callback**
   ```
   GET /api/auth/github/callback?code=xxx&state=xxx
   ```
   Exchanges code for token, creates/updates user, returns JWT

---

## Testing OAuth Locally

### Using curl

```bash
# 1. Get authorization URL
curl -v http://localhost:8000/api/auth/google/login

# 2. Manually visit the redirect URL in browser

# 3. After callback, you'll be redirected to frontend with token
```

### Using Browser DevTools

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Click "Sign in with Google/GitHub"
4. Observe the OAuth flow:
   - Initial redirect to provider
   - Callback to backend with authorization code
   - Final redirect to frontend with JWT token

---

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [FastAPI OAuth Tutorial](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure OAuth app configurations match your URLs exactly
4. Test with a different browser or incognito mode (to rule out cookie issues)
