"""Ad-hoc script: compare Cohere embed-v4.0 (production) against a locally
served sentence-transformers model for Folger corpus retrieval. Reports
recall@k and MRR@k for both, same methodology as run_evidence_search_eval.py
(only recall/MRR, not precision — we only have one or two known-good ftln
range per case, not a full relevance judgment over every returned chunk).
Pass --verbose to also print the top-k passages side by side per query.

Both sides search play_chunks, not play_lines: the chunk table stores a
modern-English `paraphrase` alongside the archaic `text`, and embeddings are
computed from the paraphrase (see EvidenceSearchPgRepository.search_similar_chunks
and seed_play_chunks.py) — a modern-English query otherwise rarely embeds
close enough to Early Modern English to match. We embed the same paraphrase
field locally so the two models are compared on equal footing.

Cohere side reuses the production path (EvidenceSearchPgRepository.search_similar_chunks),
which queries the play_chunks.embedding pgvector column already populated by
seed_play_chunks.py. The local model can't share that column — it's a
different dimension — so this script fetches every play_chunks row once,
embeds every paraphrase locally, and does a brute-force cosine top-k in
numpy. The corpus is ~630 chunks, so this is fine as a one-off script; don't
reuse this pattern for anything that runs per-request.

"Hit" = a returned chunk's [ftln_start, ftln_end] overlaps any of the case's
gold ftln ranges (chunks span multiple lines, so exact-match isn't right).

Run from backend/ (needs DATABASE_URL + COHERE_API_KEY, same as
seed_play_chunks.py; the local model downloads ~1.1GB the first time you run
this):
    python -m shylock_trial.evals.compare_embedding_models [--limit 5] [--verbose]
"""

from __future__ import annotations

import argparse
import logging
from typing import Protocol

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from infrastructure.asyncio_compat import run_async
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayChunkOrm
from shylock_trial.adapter.outbound.pg.evidence_search_repository import (
    EvidenceSearchPgRepository,
)
from shylock_trial.evals.evidence_search_eval_set import EVAL_CASES

logger = logging.getLogger(__name__)

LOCAL_MODEL_NAME = "intfloat/multilingual-e5-large-instruct"

# e5-instruct wants queries wrapped in a task instruction; passages are
# embedded plain (no prefix). Same instruction for every query here is good
# enough for a qualitative compare — tune per-query if you want to chase
# precision later.
LOCAL_TASK_DESCRIPTION = (
    "Given a modern-English paraphrase of a courtroom argument, retrieve the "
    "Early Modern English play passage from The Merchant of Venice that it echoes."
)


class _ChunkLike(Protocol):
    ftln_start: int
    ftln_end: int
    act_scene: str
    speaker: str
    text: str
    paraphrase: str


def _instruct(query: str) -> str:
    return f"Instruct: {LOCAL_TASK_DESCRIPTION}\nQuery: {query}"


def _local_top_k(
    model: SentenceTransformer,
    corpus_embeddings: np.ndarray,
    corpus: list[PlayChunkOrm],
    query: str,
    k: int,
) -> list[tuple[PlayChunkOrm, float]]:
    query_vec = model.encode([_instruct(query)], normalize_embeddings=True)[0]
    # corpus_embeddings is already L2-normalized, so dot product == cosine similarity.
    scores = corpus_embeddings @ query_vec
    top_idx = np.argsort(-scores)[:k]
    return [(corpus[i], float(scores[i])) for i in top_idx]


def _rank_of_first_hit(
    chunks: list[_ChunkLike], gold_ranges: tuple[tuple[int, int], ...]
) -> int | None:
    for rank, chunk in enumerate(chunks, start=1):
        overlaps = any(
            chunk.ftln_start <= end and start <= chunk.ftln_end for start, end in gold_ranges
        )
        if overlaps:
            return rank
    return None


def _print_hits(label: str, rows: list[tuple[str, str, str, str, float, str]]) -> None:
    print(f"\n-- {label} --")
    if not rows:
        print("  (no hits)")
        return
    for rank, (act_scene, speaker, text, paraphrase, score, score_label) in enumerate(
        rows, start=1
    ):
        print(f'  {rank}. [{act_scene}] {speaker}: "{text}" ({score_label}={score:.3f})')
        print(f'       paraphrase: "{paraphrase}"')


async def run(limit: int, verbose: bool) -> None:
    session_factory = get_session_factory()

    async with session_factory() as session:
        print("Loading Folger corpus from play_chunks ...")
        result = await session.execute(select(PlayChunkOrm).order_by(PlayChunkOrm.ftln_start))
        corpus = list(result.scalars().all())
        print(f"Corpus: {len(corpus)} chunks")

        print(f"Loading {LOCAL_MODEL_NAME} locally (first run downloads the model) ...")
        model = SentenceTransformer(LOCAL_MODEL_NAME)
        corpus_embeddings = np.asarray(
            model.encode(
                [chunk.paraphrase for chunk in corpus],
                normalize_embeddings=True,
                show_progress_bar=True,
                batch_size=32,
            )
        )

        cohere_repo = EvidenceSearchPgRepository(session)

        cohere_hits = 0
        local_hits = 0
        cohere_rr: list[float] = []
        local_rr: list[float] = []

        for case in EVAL_CASES:
            cohere_scored = await cohere_repo.search_similar_chunks(case.query, limit=limit)
            cohere_chunks = [item.chunk for item in cohere_scored]
            local_scored = _local_top_k(model, corpus_embeddings, corpus, case.query, limit)
            local_chunks = [chunk for chunk, _ in local_scored]

            cohere_rank = _rank_of_first_hit(cohere_chunks, case.gold_ftln_ranges)
            local_rank = _rank_of_first_hit(local_chunks, case.gold_ftln_ranges)

            cohere_hits += cohere_rank is not None
            local_hits += local_rank is not None
            cohere_rr.append(1 / cohere_rank if cohere_rank else 0.0)
            local_rr.append(1 / local_rank if local_rank else 0.0)

            cohere_status = f"HIT @ rank {cohere_rank}" if cohere_rank else "MISS"
            local_status = f"HIT @ rank {local_rank}" if local_rank else "MISS"
            print(
                f"[{case.confidence:>8}] {case.scene_id:<20} "
                f"Cohere: {cohere_status:<12} Local(e5): {local_status}"
            )

            if verbose:
                print("  QUERY:", case.query)
                _print_hits(
                    f"Cohere embed-v4.0 (top {limit})",
                    [
                        (c.act_scene, c.speaker, c.text, c.paraphrase, item.cosine_distance, "cosine_distance")
                        for c, item in zip(cohere_chunks, cohere_scored, strict=True)
                    ],
                )
                _print_hits(
                    f"{LOCAL_MODEL_NAME} (top {limit})",
                    [
                        (c.act_scene, c.speaker, c.text, c.paraphrase, score, "cosine_sim")
                        for c, score in local_scored
                    ],
                )
                print()

        n = len(EVAL_CASES)
        print(f"\n{'=' * 60}")
        print(f"{'model':<28} recall@{limit:<3} MRR@{limit}")
        print(f"{'-' * 60}")
        print(
            f"{'Cohere embed-v4.0':<28} "
            f"{cohere_hits}/{n} ({cohere_hits / n:.0%})   {sum(cohere_rr) / n:.3f}"
        )
        print(
            f"{LOCAL_MODEL_NAME:<28} "
            f"{local_hits}/{n} ({local_hits / n:.0%})   {sum(local_rr) / n:.3f}"
        )


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="also print the top-k passages side by side per query",
    )
    args = parser.parse_args()
    run_async(run(args.limit, args.verbose))


if __name__ == "__main__":
    main()
