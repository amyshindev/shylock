"""Wraps a primary EvidenceSearchPort (local e5) with a fallback (Cohere).
Domain code depends on EvidenceSearchPort only and never knows this wrapping
exists — see dependencies/evidence_search_provider.py for where it's
assembled. Mirrors FallbackPortiaResponseClient's shape (same escalation
idea, different port).

Only the two embedding-backed methods (search_similar_play_lines_scored,
search_similar_chunks — search_similar_play_lines delegates to the scored
one, same as EvidenceSearchPgRepository itself) actually differ between
local and Cohere, so those are the only ones with try/fallback logic here.
The rest (list_curated_evidence, find_evidence_by_id, get_line_context,
get_lines_by_topic, get_chunk) read the same Postgres tables regardless of
embedding provider, so they go straight to `primary` — trying `fallback` too
would just repeat the identical query against the identical DB.

Falls back to `fallback` when `primary` raises, or returns an empty list —
`fallback` (Cohere) itself still has its own curated-evidence fallback for
search_similar_play_lines_scored, so the full cascade is local -> Cohere ->
curated keyword ranking, never a hard failure.
"""

import logging

from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    ScoredPlayChunk,
    ScoredPlayLine,
)
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_chunk_entity import PlayChunk
from shylock_trial.domain.entities.play_line_entity import PlayLine

logger = logging.getLogger(__name__)


class FallbackEvidenceSearchRepository(EvidenceSearchPort):
    def __init__(self, primary: EvidenceSearchPort, fallback: EvidenceSearchPort) -> None:
        self._primary = primary
        self._fallback = fallback

    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]:
        scored = await self.search_similar_play_lines_scored(input_dto)
        return [item.play_line for item in scored]

    async def search_similar_play_lines_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[ScoredPlayLine]:
        try:
            result = await self._primary.search_similar_play_lines_scored(input_dto)
            if result:
                return result
            logger.warning(
                "Primary evidence search provider returned no results for "
                "search_similar_play_lines_scored (query=%r) — falling back to Cohere",
                input_dto.query,
            )
        except Exception:
            logger.exception(
                "Primary evidence search provider failed on "
                "search_similar_play_lines_scored (query=%r) — falling back to Cohere",
                input_dto.query,
            )
        return await self._fallback.search_similar_play_lines_scored(input_dto)

    async def search_similar_chunks(self, query: str, limit: int = 5) -> list[ScoredPlayChunk]:
        try:
            result = await self._primary.search_similar_chunks(query, limit=limit)
            if result:
                return result
            logger.warning(
                "Primary evidence search provider returned no results for "
                "search_similar_chunks (query=%r) — falling back to Cohere",
                query,
            )
        except Exception:
            logger.exception(
                "Primary evidence search provider failed on search_similar_chunks "
                "(query=%r) — falling back to Cohere",
                query,
            )
        return await self._fallback.search_similar_chunks(query, limit=limit)

    async def list_curated_evidence(self) -> list[Evidence]:
        return await self._primary.list_curated_evidence()

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        return await self._primary.find_evidence_by_id(evidence_id)

    async def get_line_context(
        self, ftln_start: int, ftln_end: int, radius: int = 2
    ) -> list[PlayLine]:
        return await self._primary.get_line_context(ftln_start, ftln_end, radius)

    async def get_lines_by_topic(self, topic_id: str) -> list[PlayLine]:
        return await self._primary.get_lines_by_topic(topic_id)

    async def get_chunk(self, ftln_start: int, ftln_end: int) -> PlayChunk | None:
        return await self._primary.get_chunk(ftln_start, ftln_end)
