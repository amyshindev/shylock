"""Drop alien_law_executed column from trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "012_drop_alien_law_executed"
down_revision: Union[str, None] = "011_venice_dp_shield"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("trials", "alien_law_executed")


def downgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("alien_law_executed", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("trials", "alien_law_executed", server_default=None)
