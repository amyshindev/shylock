"""Add tubal_enhanced_choices JSON column to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_tubal_enhanced_choices"
down_revision: Union[str, None] = "006_bassanio_plea_shift"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("tubal_enhanced_choices", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trials", "tubal_enhanced_choices")
