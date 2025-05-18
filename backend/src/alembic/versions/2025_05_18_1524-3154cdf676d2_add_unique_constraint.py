"""add unique constraint

Revision ID: 3154cdf676d2
Revises: 85775587bc33
Create Date: 2025-05-18 15:24:20.187811

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3154cdf676d2"
down_revision: Union[str, None] = "85775587bc33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_tg_id_movie_id", "reviews", ["tg_id", "movie_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_tg_id_movie_id", "reviews", type_="unique")
