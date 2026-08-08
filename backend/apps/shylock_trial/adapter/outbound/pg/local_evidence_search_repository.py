"""Local-embedding variant of EvidenceSearchPgRepository — same tables, same
non-embedding methods (inherited unchanged), but the two similarity-search
methods query embedding_e5_1024 (via LocalEmbeddingClient) instead of
embedding (Cohere).

Deliberately has NO internal fallback-on-failure/empty-result here (unlike
the parent's search_similar_play_lines_scored, which falls back to curated
keyword ranking) — exceptions and empty results are left to propagate so
FallbackEvidenceSearchRepository can retry against the still-reliable Cohere
path first. Falling straight to curated ranking from a local-model hiccup
would skip a perfectly good fallback tier. See
dependencies/evidence_search_provider.py for how the three tiers
(local -> Cohere -> curated) actually get assembled.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.client.local_embedding_client import LocalEmbeddingClient
from shylock_trial.adapter.outbound.mappers.evidence_search_mapper import (
    play_chunk_to_entity,
    play_line_to_entity,
)
from shylock_trial.adapter.outbound.orm.play_line_orm import PlayChunkOrm, PlayLineOrm
from shylock_trial.adapter.outbound.pg.evidence_search_repository import EvidenceSearchPgRepository
from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    ScoredPlayChunk,
    ScoredPlayLine,
)


class LocalEvidenceSearchPgRepository(EvidenceSearchPgRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self._local_embedder = LocalEmbeddingClient()

    async def search_similar_play_lines_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[ScoredPlayLine]:
        query_vector = await self._local_embedder.embed_query(input_dto.query)
        distance_expr = PlayLineOrm.embedding_e5_1024.cosine_distance(query_vector)
        result = await self._session.execute(
            select(PlayLineOrm, distance_expr.label("distance"))
            .where(PlayLineOrm.embedding_e5_1024.is_not(None))
            .order_by(distance_expr)
            .limit(input_dto.limit)
        )
        return [
            ScoredPlayLine(play_line=play_line_to_entity(row), cosine_distance=float(distance))
            for row, distance in result.all()
        ]

    async def search_similar_chunks(self, query: str, limit: int = 5) -> list[ScoredPlayChunk]:
        # Searches the paraphrase embedding, not the archaic original — same
        # reasoning as the Cohere path, see evidence_search_repository.py.
        query_vector = await self._local_embedder.embed_query(query)
        distance_expr = PlayChunkOrm.embedding_e5_1024.cosine_distance(query_vector)
        result = await self._session.execute(
            select(PlayChunkOrm, distance_expr.label("distance"))
            .where(PlayChunkOrm.embedding_e5_1024.is_not(None))
            .order_by(distance_expr)
            .limit(limit)
        )
        return [
            ScoredPlayChunk(chunk=play_chunk_to_entity(row), cosine_distance=float(distance))
            for row, distance in result.all()
        ]
