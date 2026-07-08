"""Add portia_stances_json column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018_add_portia_stances_json"
down_revision: Union[str, None] = "017_seed_curated_evidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("portia_stances_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trials", "portia_stances_json")
