"""Drop portia_hp column from trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_drop_portia_hp"
down_revision: Union[str, None] = "007_tubal_enhanced_choices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("trials", "portia_hp")


def downgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("portia_hp", sa.Integer(), nullable=False, server_default="100"),
    )
    op.alter_column("trials", "portia_hp", server_default=None)
