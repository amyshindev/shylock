"""Add pgvector hnsw indexes on play_lines/play_chunks.embedding_e5_1024.

Step 3 of the Cohere -> local-embedding migration (step 1: 029 added the
columns; step 2, apps/shylock_trial/adapter/outbound/seeding/
backfill_local_embeddings.py, filled all 2,623 play_lines + 630 play_chunks
rows — 100% populated before this runs, so there's nothing for pgvector to
skip/backfill into the index later).

Op class is vector_cosine_ops (not the L2 or inner-product one) to match how
this codebase already queries: EvidenceSearchPgRepository uses
`Column.cosine_distance(...)` (the `<=>` operator) on the existing Cohere
`embedding` columns, and the local embeddings were written with
normalize_embeddings=True specifically so the same cosine comparison is valid
here too — see backfill_local_embeddings.py. Whatever local search adapter
replaces/wraps EvidenceSearchPgRepository next should keep using
`.cosine_distance()` on embedding_e5_1024 so it actually hits this index.

hnsw over ivfflat: no training/list-count tuning step needed (ivfflat needs a
representative sample and a chosen list count; hnsw is build-as-you-go), and
the corpus here is tiny (~3.2k rows total) so hnsw's normally-higher build
cost is a non-issue. Default m=16/ef_construction=64 — no reason to tune
those for a corpus this size.

No CONCURRENTLY: both tables are small enough (order of seconds to build)
that holding a lock for the duration of this migration isn't a concern, and
CONCURRENTLY can't run inside Alembic's transactional DDL without extra
autocommit-block plumbing this doesn't need.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "030_local_embed_hnsw"
down_revision: Union[str, None] = "029_local_embed_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMN_NAME = "embedding_e5_1024"
PLAY_LINES_INDEX = "ix_play_lines_embedding_e5_1024_hnsw"
PLAY_CHUNKS_INDEX = "ix_play_chunks_embedding_e5_1024_hnsw"


def upgrade() -> None:
    op.create_index(
        PLAY_LINES_INDEX,
        "play_lines",
        [COLUMN_NAME],
        postgresql_using="hnsw",
        postgresql_ops={COLUMN_NAME: "vector_cosine_ops"},
    )
    op.create_index(
        PLAY_CHUNKS_INDEX,
        "play_chunks",
        [COLUMN_NAME],
        postgresql_using="hnsw",
        postgresql_ops={COLUMN_NAME: "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(PLAY_CHUNKS_INDEX, table_name="play_chunks")
    op.drop_index(PLAY_LINES_INDEX, table_name="play_lines")
