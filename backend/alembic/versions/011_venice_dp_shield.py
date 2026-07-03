"""Add venice_dp_shield column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011_venice_dp_shield"
down_revision: Union[str, None] = "010_drop_shylock_hp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("venice_dp_shield", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("trials", "venice_dp_shield", server_default=None)


def downgrade() -> None:
    op.drop_column("trials", "venice_dp_shield")
