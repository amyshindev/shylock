"""Add play_chunks: consecutive-same-speaker groupings of play_lines, each
carrying a modern-English paraphrase whose embedding (not the archaic
original) is what search_folger actually searches against.

Table only — no data. Population needs live Haiku (paraphrase) and Cohere
(embed) calls, which migrations shouldn't make; see
adapter/outbound/seeding/seed_play_chunks.py, run as a one-off script.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "028_add_play_chunks"
down_revision: Union[str, None] = "027_add_topic_graph"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBED_DIMENSION = 1536


def upgrade() -> None:
    op.create_table(
        "play_chunks",
        sa.Column("chunk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ftln_start", sa.Integer(), nullable=False),
        sa.Column("ftln_end", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=128), nullable=False),
        sa.Column("act_scene", sa.String(length=32), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("paraphrase", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBED_DIMENSION), nullable=True),
        sa.PrimaryKeyConstraint("chunk_id"),
    )


def downgrade() -> None:
    op.drop_table("play_chunks")
