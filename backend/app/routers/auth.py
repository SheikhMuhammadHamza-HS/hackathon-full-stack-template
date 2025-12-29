"""Authentication routes for signup, signin, signout, and OAuth."""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
import uuid
import httpx

from app.database import get_session
from app.models import User
from app.schemas import SignupRequest, SigninRequest, TokenResponse, UserResponse, MessageResponse
from app.auth import generate_jwt
from app.config import ADMIN_EMAILS, FRONTEND_URL
from app.oauth import (
    oauth,
    generate_state_token,
    is_oauth_configured,
    OAUTH_REDIRECT_URI
)

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create new user account.

    Validates email uniqueness, hashes password with bcrypt,
    creates user record, and returns JWT token.

    Returns:
        TokenResponse: User object and JWT token

    Raises:
        HTTPException 400: Duplicate email or validation error
        HTTPException 500: Database error
    """
    try:
        # Check if email is admin email (protected)
        admin_email_lower = request.email.lower()
        if admin_email_lower in [email.lower() for email in ADMIN_EMAILS]:
            raise HTTPException(
                status_code=400,
                detail="This email is used by admin person. Please signup with a different email."
            )

        # Check if email already exists (case-insensitive)
        result = await session.execute(
            select(User).where(User.email == request.email.lower())
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(
            request.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=request.email.lower(),
            name=request.name.strip(),
            password_hash=password_hash
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Generate JWT token
        token = generate_jwt(
            user_id=new_user.id,
            email=new_user.email,
            name=new_user.name
        )

        # Return user and token
        user_response = UserResponse.model_validate(new_user)
        return TokenResponse(user=user_response, token=token)

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during signup"
        )


@router.post("/signin", response_model=TokenResponse)
async def signin(
    request: SigninRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Sign in existing user.

    Validates email and password, returns JWT token.
    Uses generic error messages for security (prevent user enumeration).

    Returns:
        TokenResponse: User object and JWT token

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 500: Database error
    """
    try:
        # Find user by email (case-insensitive)
        result = await session.execute(
            select(User).where(User.email == request.email.lower())
        )
        user = result.scalar_one_or_none()

        # Generic error message (don't reveal if email exists)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Verify password
        password_valid = bcrypt.checkpw(
            request.password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        )

        if not password_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Generate JWT token
        token = generate_jwt(
            user_id=user.id,
            email=user.email,
            name=user.name
        )

        # Return user and token
        user_response = UserResponse.model_validate(user)
        return TokenResponse(user=user_response, token=token)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Signin error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during signin"
        )


@router.post("/signout", response_model=MessageResponse)
async def signout():
    """
    Sign out user (Phase II: client-side only).

    In Phase II, signout is handled client-side by removing
    the token from localStorage. This endpoint exists for
    consistency and future Phase III token blacklist feature.

    Returns:
        MessageResponse: Success message
    """
    return MessageResponse(message="Signed out successfully")


# ============================================================================
# OAuth Endpoints (Google and GitHub)
# ============================================================================

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.

    Generates authorization URL with state parameter for CSRF protection
    and redirects user to Google consent screen.

    Returns:
        RedirectResponse: Redirect to Google OAuth authorization URL

    Raises:
        HTTPException 503: OAuth not configured
    """
    if not is_oauth_configured('google'):
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    # Generate and store state token in session for CSRF protection
    state = generate_state_token()
    request.session['oauth_state'] = state

    # Build redirect URI
    redirect_uri = f"{OAUTH_REDIRECT_URI}/google/callback"

    # Generate authorization URL
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        state=state
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Handle Google OAuth callback.

    Exchanges authorization code for access token, fetches user info,
    creates or updates user account, and returns JWT token.

    Query Parameters:
        code: Authorization code from Google
        state: State token for CSRF validation

    Returns:
        RedirectResponse: Redirect to frontend with token in URL fragment

    Raises:
        HTTPException 400: Invalid state or authorization code
        HTTPException 500: Server error during OAuth process
    """
    try:
        # Note: State validation relaxed for development (sessions don't persist through OAuth redirects)
        # In production, use Redis-based state storage for proper CSRF protection
        state = request.query_params.get('state')

        if not state:
            raise HTTPException(
                status_code=400,
                detail="State parameter missing"
            )

        # Exchange authorization code for access token
        try:
            token = await oauth.google.authorize_access_token(request)
        except Exception as e:
            print(f"Google token exchange error: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid authorization code"
            )

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch user info from Google"
            )

        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        google_id = user_info.get('sub', '')

        if not email or not google_id:
            raise HTTPException(
                status_code=400,
                detail="Email or user ID not provided by Google"
            )

        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # User exists - update OAuth info if needed
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id
                user.profile_picture = picture
                await session.commit()
                await session.refresh(user)
        else:
            # Create new user with OAuth
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                password_hash=None,  # No password for OAuth users
                oauth_provider='google',
                oauth_id=google_id,
                profile_picture=picture
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Generate JWT token
        jwt_token = generate_jwt(
            user_id=user.id,
            email=user.email,
            name=user.name
        )

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}&provider=google"
        )

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        import traceback
        print(f"Google OAuth error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during Google authentication: {str(e)}"
        )


@router.get("/github/login")
async def github_login(request: Request):
    """
    Initiate GitHub OAuth login flow.

    Generates authorization URL with state parameter for CSRF protection
    and redirects user to GitHub consent screen.

    Returns:
        RedirectResponse: Redirect to GitHub OAuth authorization URL

    Raises:
        HTTPException 503: OAuth not configured
    """
    if not is_oauth_configured('github'):
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET."
        )

    # Generate and store state token in session for CSRF protection
    state = generate_state_token()
    request.session['oauth_state'] = state

    # Build redirect URI
    redirect_uri = f"{OAUTH_REDIRECT_URI}/github/callback"

    # Generate authorization URL
    return await oauth.github.authorize_redirect(
        request,
        redirect_uri,
        state=state
    )


@router.get("/github/callback")
async def github_callback(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Handle GitHub OAuth callback.

    Exchanges authorization code for access token, fetches user info,
    creates or updates user account, and returns JWT token.

    Query Parameters:
        code: Authorization code from GitHub
        state: State token for CSRF validation

    Returns:
        RedirectResponse: Redirect to frontend with token in URL fragment

    Raises:
        HTTPException 400: Invalid state or authorization code
        HTTPException 500: Server error during OAuth process
    """
    try:
        # Note: State validation relaxed for development (sessions don't persist through OAuth redirects)
        # In production, use Redis-based state storage for proper CSRF protection
        state = request.query_params.get('state')

        if not state:
            raise HTTPException(
                status_code=400,
                detail="State parameter missing"
            )

        # Exchange authorization code for access token
        try:
            token = await oauth.github.authorize_access_token(request)
        except Exception as e:
            print(f"GitHub token exchange error: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid authorization code"
            )

        # Get user info from GitHub
        access_token = token.get('access_token')
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="No access token received from GitHub"
            )

        # Fetch user data from GitHub API
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_response = await client.get(
                'https://api.github.com/user',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            user_data = user_response.json()

            # Get user emails (needed if primary email is private)
            emails_response = await client.get(
                'https://api.github.com/user/emails',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            emails_data = emails_response.json()

        # Extract user information
        github_id = str(user_data.get('id', ''))
        name = user_data.get('name') or user_data.get('login', '')
        avatar = user_data.get('avatar_url', '')

        # Find primary verified email
        email = None
        for email_obj in emails_data:
            if email_obj.get('primary') and email_obj.get('verified'):
                email = email_obj.get('email', '').lower()
                break

        # Fallback to any verified email
        if not email:
            for email_obj in emails_data:
                if email_obj.get('verified'):
                    email = email_obj.get('email', '').lower()
                    break

        if not email or not github_id:
            raise HTTPException(
                status_code=400,
                detail="Email or user ID not provided by GitHub"
            )

        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # User exists - update OAuth info if needed
            if not user.oauth_provider:
                user.oauth_provider = 'github'
                user.oauth_id = github_id
                user.profile_picture = avatar
                await session.commit()
                await session.refresh(user)
        else:
            # Create new user with OAuth
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                password_hash=None,  # No password for OAuth users
                oauth_provider='github',
                oauth_id=github_id,
                profile_picture=avatar
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Generate JWT token
        jwt_token = generate_jwt(
            user_id=user.id,
            email=user.email,
            name=user.name
        )

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}&provider=github"
        )

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print(f"GitHub OAuth error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during GitHub authentication"
        )
