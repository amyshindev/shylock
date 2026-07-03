"""Drop shylock_hp column from trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010_drop_shylock_hp"
down_revision: Union[str, None] = "009_drop_venice_contrad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("trials", "shylock_hp")


def downgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("shylock_hp", sa.Integer(), nullable=False, server_default="60"),
    )
    op.alter_column("trials", "shylock_hp", server_default=None)
