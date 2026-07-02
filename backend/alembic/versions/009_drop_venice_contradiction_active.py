"""Drop venice_contradiction_active column from trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_drop_venice_contrad"
down_revision: Union[str, None] = "008_drop_portia_hp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _trials_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns("trials")}


def upgrade() -> None:
    if "venice_contradiction_active" in _trials_columns():
        op.drop_column("trials", "venice_contradiction_active")


def downgrade() -> None:
    if "venice_contradiction_active" not in _trials_columns():
        op.add_column(
            "trials",
            sa.Column(
                "venice_contradiction_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.alter_column("trials", "venice_contradiction_active", server_default=None)
