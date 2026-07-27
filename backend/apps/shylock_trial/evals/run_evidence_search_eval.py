"""Ad-hoc script: measure EvidenceSearchPort recall against EVAL_CASES.

Only recall@k and MRR@k are reported — we only have one (or a couple of)
known-good ftln range per case, not a full relevance judgment over every
returned line, so a precision@k number would be fabricated. Run this before
and after any retrieval change (e.g. adding graph expansion) to see whether
it actually helps.

Run from backend/ (needs DATABASE_URL + COHERE_API_KEY, same as seed_play_lines.py):
    python -m shylock_trial.evals.run_evidence_search_eval [--limit 5]
"""

from __future__ import annotations

import argparse
import logging

from infrastructure.asyncio_compat import run_async
from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.pg.evidence_search_repository import (
    EvidenceSearchPgRepository,
)
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.evals.evidence_search_eval_set import EVAL_CASES

logger = logging.getLogger(__name__)


def _rank_of_first_hit(
    ftlns: list[int], gold_ranges: tuple[tuple[int, int], ...]
) -> int | None:
    for rank, ftln in enumerate(ftlns, start=1):
        if any(start <= ftln <= end for start, end in gold_ranges):
            return rank
    return None


async def run(limit: int) -> None:
    session_factory = get_session_factory()
    reciprocal_ranks: list[float] = []
    hits = 0

    async with session_factory() as session:
        repo = EvidenceSearchPgRepository(session)
        for case in EVAL_CASES:
            scored = await repo.search_similar_play_lines_scored(
                EvidenceSearchInputDto(query=case.query, limit=limit)
            )
            ftlns = [item.play_line.ftln for item in scored]
            rank = _rank_of_first_hit(ftlns, case.gold_ftln_ranges)
            hit = rank is not None
            hits += hit
            reciprocal_ranks.append(1 / rank if rank else 0.0)

            status = f"HIT @ rank {rank}" if hit else "MISS"
            print(f"[{case.confidence:>8}] {case.scene_id:<20} {status}")
            if not hit:
                speakers = [
                    (item.play_line.ftln, item.play_line.speaker) for item in scored
                ]
                print(f"           gold in {case.gold_ftln_ranges}, got {speakers}")

    n = len(EVAL_CASES)
    print(f"\nrecall@{limit}: {hits}/{n} ({hits / n:.0%})")
    print(f"MRR@{limit}: {sum(reciprocal_ranks) / n:.3f}")


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    run_async(run(args.limit))


if __name__ == "__main__":
    main()
