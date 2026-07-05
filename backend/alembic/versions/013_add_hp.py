"""Add hp column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013_add_hp"
down_revision: Union[str, None] = "012_drop_alien_law_executed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("hp", sa.Integer(), nullable=False, server_default="100"),
    )
    op.alter_column("trials", "hp", server_default=None)


def downgrade() -> None:
    op.drop_column("trials", "hp")
