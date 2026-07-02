"""Add tubal_used_scenes and presented_evidence JSON columns to trials."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_trial_tubal_evidence"
down_revision: Union[str, None] = "004_embedding_1536"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trials",
        sa.Column("tubal_used_scenes_json", sa.Text(), nullable=True),
    )
    op.add_column(
        "trials",
        sa.Column("presented_evidence_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trials", "presented_evidence_json")
    op.drop_column("trials", "tubal_used_scenes_json")
