"""Add phone_number and emergency contact fields to user model

Revision ID: add_user_phone_fields
Revises: 5cdb56be05da
Create Date: 2025-09-17 14:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_phone_fields'
down_revision: Union[str, Sequence[str], None] = '5cdb56be05da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add only the user fields we need
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('emergency_contact_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'emergency_contact_phone')
    op.drop_column('users', 'emergency_contact_name')
    op.drop_column('users', 'phone_number')