"""Authentication routes for signup, signin, and signout."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
import uuid

from app.database import get_session
from app.models import User
from app.schemas import SignupRequest, SigninRequest, TokenResponse, UserResponse, MessageResponse
from app.auth import generate_jwt
from app.config import ADMIN_EMAILS, ADMIN_CREDENTIALS

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
