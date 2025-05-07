"""rename created date name

Revision ID: 8843515a1664
Revises: 49338c07a086
Create Date: 2025-05-07 19:57:14.421761

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8843515a1664"
down_revision: Union[str, None] = "49338c07a086"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=False))
    op.drop_column("users", "create_date")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "create_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("users", "created_at")
