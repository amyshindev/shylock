"""One-off batch: backfill play_lines.embedding_e5_1024 / play_chunks.embedding_e5_1024
from the existing Cohere-embedded rows, using a local sentence-transformers model.

Step 2 of the Cohere -> local-embedding migration (step 1:
alembic/versions/029_add_local_embedding_columns.py added the columns, still
all NULL). This script only fills those columns in — it does not touch the
old `embedding` (Cohere) columns, create any index, or change which adapter
the game actually queries. Both of those are later steps.

Embedding convention — matches shylock_trial.evals.compare_embedding_models,
the script that already validated e5 retrieval quality against Cohere on this
corpus, so query-time embeddings (built with the "Instruct: ...\\nQuery: ..."
wrapper) stay comparable to what's indexed here:
    - play_lines.text / play_chunks.paraphrase are embedded PLAIN, no prefix
      (e5-instruct's convention: passages plain, only queries get the
      instruction wrapper).
    - normalize_embeddings=True, so a future local search adapter can do
      dot-product instead of cosine and get the same ranking.

Run from backend/ (needs DATABASE_URL/DIRECT_URL — same migration convention
as alembic; no COHERE_API_KEY needed, this is all local):
    python -m shylock_trial.adapter.outbound.seeding.backfill_local_embeddings
    python -m shylock_trial.adapter.outbound.seeding.backfill_local_embeddings --limit 20   # smoke test
    python -m shylock_trial.adapter.outbound.seeding.backfill_local_embeddings --force      # re-embed rows that already have embedding_e5_1024

Needs: pip install sentence-transformers (downloads ~1.1GB the first run).
"""

from __future__ import annotations

import argparse
import logging
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.asyncio_compat import run_async
from infrastructure.config import get_settings
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.orm.play_line_orm import (
    LOCAL_EMBED_DIMENSION,
    PlayChunkOrm,
    PlayLineOrm,
)

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 32


async def _fetch_rows(
    session: AsyncSession,
    orm_cls: type[PlayLineOrm] | type[PlayChunkOrm],
    force: bool,
    limit: int | None,
) -> list[PlayLineOrm] | list[PlayChunkOrm]:
    stmt = select(orm_cls)
    if not force:
        stmt = stmt.where(orm_cls.embedding_e5_1024.is_(None))
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _backfill_one_table(
    model,
    rows: list[PlayLineOrm] | list[PlayChunkOrm],
    text_of,
    label: str,
    batch_size: int,
) -> None:
    if not rows:
        logger.info("%s: nothing to backfill (all rows already have embedding_e5_1024).", label)
        return

    texts = [text_of(row) for row in rows]
    t0 = time.perf_counter()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=True,
    )
    elapsed = time.perf_counter() - t0
    logger.info("%s: encoded %d rows in %.1fs (%.1fms/row).", label, len(rows), elapsed, elapsed / len(rows) * 1000)

    for row, vector in zip(rows, vectors, strict=True):
        row.embedding_e5_1024 = vector.tolist()

    assert len(rows[0].embedding_e5_1024) == LOCAL_EMBED_DIMENSION, (
        f"encoded vector dim {len(rows[0].embedding_e5_1024)} != column dim {LOCAL_EMBED_DIMENSION} "
        f"— model changed? update LOCAL_EMBED_DIMENSION and the migration together."
    )


async def main(force: bool, limit: int | None, batch_size: int) -> None:
    logging.basicConfig(level=logging.INFO)

    # Imported lazily so `--help` doesn't pay the sentence-transformers import cost.
    from sentence_transformers import SentenceTransformer

    model_name = get_settings().local_embedding_model
    logger.info("Loading %s locally (first run downloads ~1.1GB)...", model_name)
    model = SentenceTransformer(model_name)

    session_factory = get_session_factory()
    async with session_factory() as session:
        lines = await _fetch_rows(session, PlayLineOrm, force, limit)
        _backfill_one_table(model, lines, lambda r: r.text, "play_lines", batch_size)

        chunks = await _fetch_rows(session, PlayChunkOrm, force, limit)
        _backfill_one_table(model, chunks, lambda r: r.paraphrase, "play_chunks", batch_size)

        await session.commit()

    logger.info("Backfilled %d play_lines + %d play_chunks rows.", len(lines), len(chunks))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-embed rows that already have embedding_e5_1024 set (default: only fill NULLs, safe to re-run)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap rows per table (smoke test before running the full ~3,253-row backfill)",
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="local encode() batch size")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_async(main(force=args.force, limit=args.limit, batch_size=args.batch_size))
