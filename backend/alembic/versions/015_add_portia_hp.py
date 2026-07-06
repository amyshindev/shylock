"""Add portia_hp column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "015_add_portia_hp"
down_revision: Union[str, None] = "014_venice_paradox_used"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("portia_hp", sa.Integer(), nullable=False, server_default="100"),
    )
    op.alter_column("trials", "portia_hp", server_default=None)


def downgrade() -> None:
    op.drop_column("trials", "portia_hp")
