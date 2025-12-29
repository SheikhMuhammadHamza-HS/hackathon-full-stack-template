"""add user-specific task number

Revision ID: a2b3c4d5e6f7
Revises: 1fdc137aba7b
Create Date: 2025-12-29 12:00:00.000000

Add task_number column for user-specific task numbering.
Each user's tasks are numbered independently (1, 2, 3...).
This allows chatbot to reference tasks by user-friendly numbers
instead of global database IDs.

Migration Strategy:
1. Add task_number column with default 1
2. Populate existing tasks with sequential numbers per user
3. Add composite index on (user_id, task_number) for lookups
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = '1fdc137aba7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add task_number column with per-user numbering."""
    # Add task_number column with default 1 (will be updated for existing rows)
    op.add_column('tasks', sa.Column('task_number', sa.Integer(), nullable=False, server_default='1'))

    # Update existing tasks with sequential task_number per user
    # Using raw SQL for the window function
    op.execute("""
        WITH numbered_tasks AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at, id) as new_number
            FROM tasks
        )
        UPDATE tasks
        SET task_number = numbered_tasks.new_number
        FROM numbered_tasks
        WHERE tasks.id = numbered_tasks.id
    """)

    # Create composite index for efficient lookups by user_id + task_number
    op.create_index('idx_tasks_user_task_number', 'tasks', ['user_id', 'task_number'])


def downgrade() -> None:
    """Downgrade schema: Remove task_number column."""
    # Drop index first
    op.drop_index('idx_tasks_user_task_number', table_name='tasks')

    # Drop column
    op.drop_column('tasks', 'task_number')
