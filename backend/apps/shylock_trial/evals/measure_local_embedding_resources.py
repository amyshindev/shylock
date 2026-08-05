"""Ad-hoc script: measure the practical cost of serving embeddings locally
(sentence-transformers) vs. calling Cohere's API, on whatever host you run
it on. compare_embedding_models.py only measures retrieval *quality* (and
was run on a dev laptop) — this measures the two things that comparison
can't tell you and that matter for a production decision: memory footprint
and per-query latency. Run this ON the actual target host (e.g. the EC2
instance), not your laptop; laptop numbers don't transfer.

Reports, in order:
  1. Process RSS at each stage of loading the local model (import ->
     construct -> after a batch embed) — is there room for this next to
     FastAPI/Postgres/Redis on that box?
  2. Local single-query embedding latency (warm, N repeats) — mean/median/
     p95/min/max, plus the cold first call separately (lazy init).
  3. Cohere single-query embedding latency (real API calls, same N) for a
     side-by-side comparison against #2. Skippable with --skip-cohere.
  4. Local batch embedding throughput (texts/sec) on a real sample of
     paraphrases pulled from the DB, extrapolated to how long a full
     play_lines + play_chunks re-embed would take on this host — the
     one-time migration cost mentioned in
     _docs/compare-embedding-models-result.md section 4.1.

Run from backend/ (needs DATABASE_URL always; COHERE_API_KEY unless
--skip-cohere; the model downloads ~1.1GB the first time you run this on a
given host):
    python -m shylock_trial.evals.measure_local_embedding_resources [--repeats 20] [--skip-cohere]
"""

from __future__ import annotations

import argparse
import logging
import platform
import resource
import statistics
import time

from sqlalchemy import func, select

from infrastructure.asyncio_compat import run_async
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayChunkOrm, PlayLineOrm
from shylock_trial.evals.evidence_search_eval_set import EVAL_CASES

logger = logging.getLogger(__name__)

LOCAL_MODEL_NAME = "intfloat/multilingual-e5-large-instruct"
LOCAL_TASK_DESCRIPTION = (
    "Given a modern-English paraphrase of a courtroom argument, retrieve the "
    "Early Modern English play passage from The Merchant of Venice that it echoes."
)
SAMPLE_QUERY = EVAL_CASES[0].query


def _rss_mb() -> float:
    """Peak RSS so far, in MB. ru_maxrss is KB on Linux, bytes on macOS/BSD —
    it only ever grows within a process, so calling this at checkpoints shows
    how much each stage added, not just a final total."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 1024 if platform.system() == "Linux" else peak / (1024 * 1024)


def _report_latency(label: str, samples_s: list[float]) -> None:
    ms = [s * 1000 for s in samples_s]
    print(
        f"{label:<28} mean={statistics.mean(ms):7.1f}ms  "
        f"median={statistics.median(ms):7.1f}ms  "
        f"p95={sorted(ms)[int(len(ms) * 0.95)] if len(ms) > 1 else ms[0]:7.1f}ms  "
        f"min={min(ms):7.1f}ms  max={max(ms):7.1f}ms  (n={len(ms)})"
    )


async def _corpus_counts() -> tuple[int, int]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        lines = (await session.execute(select(func.count()).select_from(PlayLineOrm))).scalar_one()
        chunks = (await session.execute(select(func.count()).select_from(PlayChunkOrm))).scalar_one()
        return lines, chunks


async def _sample_paraphrases(n: int) -> list[str]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(PlayChunkOrm.paraphrase).limit(n))
        return [row[0] for row in result.all()]


def run(repeats: int, batch_size: int, corpus_sample: int, skip_cohere: bool) -> None:
    print(f"Host: {platform.platform()} / {platform.processor() or platform.machine()}")
    print(f"RSS at start:                {_rss_mb():8.1f} MB\n")

    # --- 1. memory footprint of loading the local model ---
    print("=" * 78)
    print("1. Local model memory footprint")
    print("=" * 78)

    t0 = time.perf_counter()
    from sentence_transformers import SentenceTransformer  # noqa: PLC0415 (measuring import cost)

    t_import = time.perf_counter() - t0
    print(f"import sentence_transformers: {t_import:6.2f}s   RSS now: {_rss_mb():8.1f} MB")

    t0 = time.perf_counter()
    model = SentenceTransformer(LOCAL_MODEL_NAME)
    t_load = time.perf_counter() - t0
    print(f"load {LOCAL_MODEL_NAME}: {t_load:6.2f}s   RSS now: {_rss_mb():8.1f} MB")
    print("  (first run on this host also includes ~1.1GB download — rerun to see steady-state load time)")

    # --- 2. local single-query latency (warm) ---
    print(f"\n{'=' * 78}")
    print("2. Local single-query embedding latency")
    print("=" * 78)

    instruct_query = f"Instruct: {LOCAL_TASK_DESCRIPTION}\nQuery: {SAMPLE_QUERY}"

    t0 = time.perf_counter()
    model.encode([instruct_query], normalize_embeddings=True)
    cold_s = time.perf_counter() - t0
    print(f"first call (cold, lazy init): {cold_s * 1000:7.1f}ms")

    local_samples: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        model.encode([instruct_query], normalize_embeddings=True)
        local_samples.append(time.perf_counter() - t0)
    _report_latency(f"local (warm, n={repeats})", local_samples)
    print(f"RSS now: {_rss_mb():8.1f} MB")

    # --- 3. Cohere single-query latency, for comparison ---
    if not skip_cohere:
        print(f"\n{'=' * 78}")
        print("3. Cohere embed-v4.0 single-query latency (real API calls)")
        print("=" * 78)

        from shylock_trial.adapter.outbound.client.evidence_embedding_client import (  # noqa: PLC0415
            EvidenceEmbeddingClient,
        )

        async def _cohere_samples() -> list[float]:
            client = EvidenceEmbeddingClient()
            samples: list[float] = []
            for _ in range(repeats):
                t0 = time.perf_counter()
                await client.embed_query(SAMPLE_QUERY)
                samples.append(time.perf_counter() - t0)
            return samples

        cohere_samples = run_async(_cohere_samples())
        _report_latency(f"Cohere API (n={repeats})", cohere_samples)
    else:
        print(f"\n{'=' * 78}\n3. Cohere latency skipped (--skip-cohere)\n{'=' * 78}")

    # --- 4. local batch throughput + full-corpus re-embed estimate ---
    print(f"\n{'=' * 78}")
    print("4. Local batch embedding throughput + full-corpus estimate")
    print("=" * 78)

    paraphrases = run_async(_sample_paraphrases(corpus_sample))
    if not paraphrases:
        print("  (no play_chunks rows found — skipping)")
    else:
        t0 = time.perf_counter()
        model.encode(paraphrases, normalize_embeddings=True, batch_size=batch_size)
        elapsed = time.perf_counter() - t0
        rate = len(paraphrases) / elapsed
        print(
            f"embedded {len(paraphrases)} paraphrases in {elapsed:.2f}s "
            f"({rate:.1f} texts/sec, batch_size={batch_size})"
        )

        n_lines, n_chunks = run_async(_corpus_counts())
        total = n_lines + n_chunks
        est_s = total / rate
        print(f"play_lines={n_lines} + play_chunks={n_chunks} = {total} rows")
        print(f"estimated one-time full re-embed on this host: {est_s:.0f}s ({est_s / 60:.1f} min)")

    print(f"\nRSS peak overall: {_rss_mb():8.1f} MB")


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=20, help="latency samples per method")
    parser.add_argument("--batch-size", type=int, default=32, help="local encode() batch size")
    parser.add_argument(
        "--corpus-sample", type=int, default=100, help="how many real paraphrases to time batch throughput on"
    )
    parser.add_argument(
        "--skip-cohere", action="store_true", help="skip Cohere API calls (no COHERE_API_KEY / avoid cost)"
    )
    args = parser.parse_args()
    run(args.repeats, args.batch_size, args.corpus_sample, args.skip_cohere)


if __name__ == "__main__":
    main()
