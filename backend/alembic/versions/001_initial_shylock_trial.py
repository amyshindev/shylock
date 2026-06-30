"""Initial shylock_trial schema."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "trials",
        sa.Column("trial_id", sa.UUID(), nullable=False),
        sa.Column("scene_index", sa.Integer(), nullable=False),
        sa.Column("dignity", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(length=32), nullable=False),
        sa.Column("narration_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("trial_id"),
    )
    op.create_table(
        "trial_choice_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("trial_id", sa.UUID(), nullable=False),
        sa.Column("choice_id", sa.String(length=64), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trial_id"], ["trials.trial_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "play_lines",
        sa.Column("ftln", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("act_scene", sa.String(length=32), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.PrimaryKeyConstraint("ftln"),
    )
    op.create_table(
        "evidence",
        sa.Column("evidence_id", sa.String(length=64), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("act_scene", sa.String(length=32), nullable=False),
        sa.Column("icon", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_ftln_start", sa.Integer(), nullable=False),
        sa.Column("source_ftln_end", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("evidence_id"),
    )


def downgrade() -> None:
    op.drop_table("evidence")
    op.drop_table("play_lines")
    op.drop_table("trial_choice_history")
    op.drop_table("trials")
