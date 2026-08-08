"""Add 1024-dim local-embedding columns to play_lines/play_chunks, alongside
the existing 1536-dim Cohere embed-v4.0 `embedding` columns.

Step 1 of the Cohere -> local-embedding migration (see
apps/shylock_trial/evals/measure_embedding_latency.py for the latency/quality
comparison that motivated this). Schema only: the new columns start out
entirely NULL (no backfill here — that's the reembedding step) and get no
index yet (no point indexing an empty column; the hnsw index gets created
after reembedding). The old `embedding` columns are left in place untouched
so the game keeps running on Cohere exactly as before, and so there's a
working comparison/rollback path until the local model is validated.

Target model: intfloat/multilingual-e5-large-instruct (sentence-transformers),
1024 dims — vs. Cohere embed-v4.0's 1536. Column name encodes the model
family (e5) and dimension together (`embedding_e5_1024`) rather than reusing
the bare `embedding` name, since `embedding` already implicitly means
"Cohere embed-v4.0, 1536-dim" everywhere else in this codebase (ORM
`EMBED_DIMENSION`, `Settings.cohere_embed_model`, etc.).

Next steps (not this migration): reembed play_lines/play_chunks locally,
create an hnsw index on the new columns, swap the search adapter to read
from them (with Cohere fallback), then — once validated — drop the old
`embedding` columns in a follow-up migration.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "029_local_embed_cols"
down_revision: Union[str, None] = "028_add_play_chunks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOCAL_EMBED_DIMENSION = 1024
COLUMN_NAME = "embedding_e5_1024"


def upgrade() -> None:
    op.add_column(
        "play_lines",
        sa.Column(COLUMN_NAME, Vector(LOCAL_EMBED_DIMENSION), nullable=True),
    )
    op.add_column(
        "play_chunks",
        sa.Column(COLUMN_NAME, Vector(LOCAL_EMBED_DIMENSION), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("play_chunks", COLUMN_NAME)
    op.drop_column("play_lines", COLUMN_NAME)
