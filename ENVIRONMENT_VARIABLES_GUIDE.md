# Environment Variables Quick Reference

## Backend (.env file location: `backend/.env`)

### ✅ Required Variables (Already Configured)

```bash
# Database Connection
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# Authentication Secret (JWT signing key)
# Generate with: openssl rand -base64 32
BETTER_AUTH_SECRET=your-secret-key-here

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000

# Optional: Database Logging
DATABASE_ECHO=false
```

---

## 🆕 New OAuth Variables (You Need to Add These)

### Google OAuth

**Where to Get**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

```bash
# Google Client ID (ends with .apps.googleusercontent.com)
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# Google Client Secret
GOOGLE_CLIENT_SECRET=GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

**Setup Steps**:
1. Create project in Google Cloud Console
2. Configure OAuth consent screen
3. Create OAuth 2.0 credentials (Web application)
4. Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
5. Copy Client ID and Client Secret

---

### GitHub OAuth

**Where to Get**: [GitHub Developer Settings](https://github.com/settings/developers)

```bash
# GitHub Client ID (starts with Iv1.)
GITHUB_CLIENT_ID=Iv1.a1b2c3d4e5f6g7h8

# GitHub Client Secret (20-40 characters)
GITHUB_CLIENT_SECRET=1234567890abcdef1234567890abcdef12345678
```

**Setup Steps**:
1. Go to GitHub Settings → Developer Settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/auth/github/callback`
4. Register application
5. Generate client secret (copy immediately!)
6. Copy Client ID and Client Secret

---

### OAuth Redirect URI

```bash
# Base URL for OAuth callbacks (no trailing slash)
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
```

**Note**: This should match your backend URL. In production, use:
```bash
OAUTH_REDIRECT_URI=https://api.yourdomain.com/api/auth
```

---

## 📋 Complete .env File Template

Copy this template to `backend/.env` and fill in your values:

```bash
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.aws.neon.tech/neondb?sslmode=require
DATABASE_ECHO=false

# ============================================================================
# AUTHENTICATION
# ============================================================================
# Generate with: openssl rand -base64 32
BETTER_AUTH_SECRET=your-32-character-random-secret-key-here

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
ALLOWED_ORIGINS=http://localhost:3000

# ============================================================================
# OAUTH CONFIGURATION - GOOGLE
# ============================================================================
# Get credentials from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# ============================================================================
# OAUTH CONFIGURATION - GITHUB
# ============================================================================
# Get credentials from: https://github.com/settings/developers
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# ============================================================================
# OAUTH REDIRECT URI
# ============================================================================
# Must match configured callback URLs in OAuth apps
OAUTH_REDIRECT_URI=http://localhost:8000/api/auth
```

---

## 🔒 Security Best Practices

### DO:
✅ Use `.env` files (never commit to git)
✅ Generate strong random secrets (`openssl rand -base64 32`)
✅ Use different secrets for development and production
✅ Store production secrets in secure secret managers (AWS Secrets Manager, Azure Key Vault, etc.)
✅ Rotate secrets regularly
✅ Use HTTPS in production

### DON'T:
❌ Commit `.env` files to version control
❌ Share secrets in Slack, email, or documentation
❌ Use the same secrets across multiple environments
❌ Use simple or default secrets in production
❌ Store secrets in frontend code

---

## 🚀 Validation Checklist

After adding environment variables, verify your configuration:

### 1. Check .env File Exists
```bash
ls backend/.env  # Should show the file
```

### 2. Verify Variables are Set
```bash
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ DATABASE_URL:', 'SET' if os.getenv('DATABASE_URL') else '❌ MISSING'); print('✅ BETTER_AUTH_SECRET:', 'SET' if os.getenv('BETTER_AUTH_SECRET') else '❌ MISSING'); print('✅ GOOGLE_CLIENT_ID:', 'SET' if os.getenv('GOOGLE_CLIENT_ID') else '❌ MISSING'); print('✅ GITHUB_CLIENT_ID:', 'SET' if os.getenv('GITHUB_CLIENT_ID') else '❌ MISSING')"
```

### 3. Test OAuth Endpoints
```bash
# Start backend server
cd backend
.venv/Scripts/uvicorn.exe app.main:app --reload --port 8001

# In browser, visit:
# http://localhost:8001/api/auth/google/login  (should redirect to Google)
# http://localhost:8001/api/auth/github/login  (should redirect to GitHub)
```

---

## 🌐 Production Environment Variables

When deploying to production (Railway, Render, Vercel, etc.):

### Backend Environment:
```bash
DATABASE_URL=postgresql://...  # Production database
BETTER_AUTH_SECRET=...         # Different secret than dev!
ALLOWED_ORIGINS=https://yourdomain.com
GOOGLE_CLIENT_ID=...           # Production Google OAuth credentials
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...           # Production GitHub OAuth credentials
GITHUB_CLIENT_SECRET=...
OAUTH_REDIRECT_URI=https://api.yourdomain.com/api/auth
```

**Important**: You must create **separate OAuth applications** for production:
- Google: New OAuth 2.0 Client ID with production URLs
- GitHub: New OAuth App with production URLs

---

## 🆘 Troubleshooting

### Backend won't start
**Check**:
- `.env` file exists in `backend/` directory
- `DATABASE_URL` is set and valid
- `BETTER_AUTH_SECRET` is set

### OAuth redirect URI mismatch
**Check**:
- `OAUTH_REDIRECT_URI` in `.env` matches base URL
- Google Cloud Console has: `{OAUTH_REDIRECT_URI}/google/callback`
- GitHub OAuth App has: `{OAUTH_REDIRECT_URI}/github/callback`

### "OAuth not configured" error
**Check**:
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set (for Google)
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set (for GitHub)
- Restart backend server after adding variables

---

## 📚 Additional Resources

- **Detailed OAuth Setup**: `backend/docs/oauth-setup.md`
- **Implementation Summary**: `OAUTH_IMPLEMENTATION_SUMMARY.md`
- **Backend README**: `backend/README.md`
- **Google OAuth Docs**: https://developers.google.com/identity/protocols/oauth2
- **GitHub OAuth Docs**: https://docs.github.com/en/developers/apps/building-oauth-apps

---

**Last Updated**: 2025-12-20
**Status**: Ready for configuration
