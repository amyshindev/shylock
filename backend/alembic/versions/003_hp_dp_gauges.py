"""Rename dignity/confidence to dp/shylock_hp; add portia_hp and alien_law_executed."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_hp_dp_gauges"
down_revision: Union[str, None] = "002_scene_dialogues"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("trials", "dignity", new_column_name="dp")
    op.alter_column("trials", "confidence", new_column_name="shylock_hp")
    op.add_column(
        "trials",
        sa.Column("portia_hp", sa.Integer(), nullable=False, server_default="100"),
    )
    op.add_column(
        "trials",
        sa.Column(
            "alien_law_executed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.alter_column("trials", "portia_hp", server_default=None)
    op.alter_column("trials", "alien_law_executed", server_default=None)


def downgrade() -> None:
    op.drop_column("trials", "alien_law_executed")
    op.drop_column("trials", "portia_hp")
    op.alter_column("trials", "shylock_hp", new_column_name="confidence")
    op.alter_column("trials", "dp", new_column_name="dignity")
