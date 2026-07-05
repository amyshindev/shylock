"""Add venice_paradox_used column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_venice_paradox_used"
down_revision: Union[str, None] = "013_add_hp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("venice_paradox_used", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("trials", "venice_paradox_used", server_default=None)


def downgrade() -> None:
    op.drop_column("trials", "venice_paradox_used")
