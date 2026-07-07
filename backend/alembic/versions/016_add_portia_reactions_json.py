"""Add portia_reactions_json column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "016_add_portia_reactions_json"
down_revision: Union[str, None] = "015_add_portia_hp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("portia_reactions_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trials", "portia_reactions_json")
