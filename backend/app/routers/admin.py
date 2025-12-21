"""Admin routes with authentication."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_session
from app.models import User, Task, Conversation, Message
from app.auth import verify_jwt
from app.config import ADMIN_EMAILS
from app.schemas import MessageResponse

router = APIRouter()


async def verify_admin(
    authenticated_user: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """Verify user is admin by checking email against ADMIN_EMAILS list."""
    # Get user from database
    result = await session.execute(
        select(User).where(User.id == authenticated_user)
    )
    user = result.scalar_one_or_none()

    if not user or user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Only authorized administrators can access this endpoint."
        )

    return user.email


@router.get("/users")
async def list_all_users(
    admin_email: str = Depends(verify_admin),
    session: AsyncSession = Depends(get_session)
):
    """List all users (ADMIN ONLY - Requires authentication)"""
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
            "is_admin": user.email in ADMIN_EMAILS
        }
        for user in users
    ]


@router.get("/stats")
async def get_stats(
    admin_email: str = Depends(verify_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get database statistics (ADMIN ONLY - Requires authentication)"""
    user_result = await session.execute(select(User))
    task_result = await session.execute(select(Task))

    users = user_result.scalars().all()
    tasks = task_result.scalars().all()

    return {
        "total_users": len(users),
        "total_tasks": len(tasks),
        "users": [{"name": u.name, "email": u.email, "task_count": len([t for t in tasks if t.user_id == u.id])} for u in users]
    }


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    admin_email: str = Depends(verify_admin),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a user and all their tasks (ADMIN ONLY - Requires authentication).

    This is a destructive operation that:
    1. Deletes all tasks owned by the user
    2. Deletes the user account

    Args:
        user_id: ID of user to delete
        admin_email: Admin email from JWT verification
        session: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException 403: If not admin
        HTTPException 404: If user not found
        HTTPException 400: If trying to delete yourself
    """
    try:
        # Get user to delete
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent admin from deleting themselves
        if user.email == admin_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )

        # Delete user's messages first (due to foreign key constraint)
        await session.execute(
            delete(Message).where(Message.user_id == user_id)
        )

        # Delete user's conversations
        await session.execute(
            delete(Conversation).where(Conversation.user_id == user_id)
        )

        # Delete user's tasks
        await session.execute(
            delete(Task).where(Task.user_id == user_id)
        )

        # Delete user
        await session.delete(user)
        await session.commit()

        return MessageResponse(
            message=f"User {user.email} and all their data deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
