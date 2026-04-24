"""rename_ibs_subtype_to_ibs_type

Revision ID: 5cdb56be05da
Revises: 5727f7c9d071
Create Date: 2025-09-17 11:47:46.111224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cdb56be05da'
down_revision: Union[str, Sequence[str], None] = '5727f7c9d071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
