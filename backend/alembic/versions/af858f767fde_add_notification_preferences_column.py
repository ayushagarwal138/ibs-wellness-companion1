"""add_notification_preferences_column

Revision ID: af858f767fde
Revises: 1f0bc62ee595
Create Date: 2025-10-02 13:22:56.655143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'af858f767fde'
down_revision: Union[str, Sequence[str], None] = '687d42966a35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add notification_preferences column as JSONB
    op.add_column('users', sa.Column('notification_preferences', 
                                     postgresql.JSONB(astext_type=sa.Text()), 
                                     nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove notification_preferences column
    op.drop_column('users', 'notification_preferences')
