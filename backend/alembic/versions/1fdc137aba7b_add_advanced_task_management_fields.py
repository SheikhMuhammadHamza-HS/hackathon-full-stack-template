"""add advanced task management fields

Revision ID: 1fdc137aba7b
Revises: 0038046a8779
Create Date: 2025-12-25 15:51:19.717211

Phase V: Add advanced task management fields to support:
- Priority levels (low, medium, high)
- Tags for categorization (JSONB array)
- Due dates for reminders (with timezone)
- Recurring task support (daily, weekly, monthly intervals)

All fields have defaults for backward compatibility with existing tasks.
Performance indexes added for priority and due_date filtering.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1fdc137aba7b'
down_revision: Union[str, Sequence[str], None] = '0038046a8779'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add advanced task management fields."""
    # Add priority column with default 'medium' for existing rows
    op.add_column('tasks', sa.Column('priority', sa.VARCHAR(length=10), nullable=False, server_default='medium'))

    # Add tags column with default empty JSON array for existing rows
    op.add_column('tasks', sa.Column('tags', sa.Text(), nullable=False, server_default='[]'))

    # Add due_date column (nullable, no default needed)
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))

    # Add is_recurring flag with default false for existing rows
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))

    # Add recurring_interval column (nullable, only used when is_recurring=true)
    op.add_column('tasks', sa.Column('recurring_interval', sa.VARCHAR(length=20), nullable=True))

    # Create performance indexes
    # Index on priority for filtering by priority level
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])

    # Partial index on due_date (only non-null values) for reminder queries
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))


def downgrade() -> None:
    """Downgrade schema: Remove advanced task management fields."""
    # Drop indexes first
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')

    # Drop columns in reverse order
    op.drop_column('tasks', 'recurring_interval')
    op.drop_column('tasks', 'is_recurring')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
