"""Widen play_lines.embedding to 1536 dims (Cohere embed-v4.0)."""

from typing import Sequence, Union

from alembic import op

revision: str = "004_embedding_1536"
down_revision: Union[str, None] = "003_hp_dp_gauges"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE play_lines "
        "ALTER COLUMN embedding TYPE vector(1536) "
        "USING embedding::vector(1536)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE play_lines "
        "ALTER COLUMN embedding TYPE vector(1024) "
        "USING embedding::vector(1024)"
    )
