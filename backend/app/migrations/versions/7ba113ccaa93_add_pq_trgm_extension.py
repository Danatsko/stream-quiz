"""add_pq_trgm_extension

Revision ID: 7ba113ccaa93
Revises: 072ac3c160e3
Create Date: 2026-05-17 18:37:25.041167

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7ba113ccaa93"
down_revision: Union[str, Sequence[str], None] = "072ac3c160e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
