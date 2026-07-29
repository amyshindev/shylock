import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.mappers.evidence_search_mapper import (
    evidence_to_entity,
    play_chunk_to_entity,
    play_line_to_entity,
)
from shylock_trial.adapter.outbound.orm.play_line_orm import (
    EvidenceOrm,
    LineTopicOrm,
    PlayChunkOrm,
    PlayLineOrm,
)
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


class EvidenceSearchPgRepository(EvidenceSearchPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._embedder = EvidenceEmbeddingClient()

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
        scored: list[ScoredPlayLine] = []
        try:
            query_vector = await self._embedder.embed_query(input_dto.query)
            distance_expr = PlayLineOrm.embedding.cosine_distance(query_vector)
            result = await self._session.execute(
                select(PlayLineOrm, distance_expr.label("distance"))
                .where(PlayLineOrm.embedding.is_not(None))
                .order_by(distance_expr)
                .limit(input_dto.limit)
            )
            scored = [
                ScoredPlayLine(
                    play_line=play_line_to_entity(row),
                    cosine_distance=float(distance),
                )
                for row, distance in result.all()
            ]
        except Exception:
            logger.exception("Folger vector search failed; falling back to curated evidence")

        if scored:
            return scored

        from shylock_trial.adapter.outbound.memory.evidence_search_repository import (
            rank_curated_play_lines,
        )

        return rank_curated_play_lines(input_dto.query, limit=input_dto.limit)

    async def list_curated_evidence(self) -> list[Evidence]:
        result = await self._session.execute(select(EvidenceOrm))
        return [evidence_to_entity(row) for row in result.scalars().all()]

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        orm = await self._session.get(EvidenceOrm, evidence_id)
        return evidence_to_entity(orm) if orm else None

    async def get_line_context(
        self, ftln_start: int, ftln_end: int, radius: int = 2
    ) -> list[PlayLine]:
        result = await self._session.execute(
            select(PlayLineOrm)
            .where(PlayLineOrm.ftln.between(ftln_start - radius, ftln_end + radius))
            .order_by(PlayLineOrm.ftln)
        )
        return [play_line_to_entity(row) for row in result.scalars().all()]

    async def get_lines_by_topic(self, topic_id: str) -> list[PlayLine]:
        result = await self._session.execute(
            select(PlayLineOrm)
            .join(LineTopicOrm, LineTopicOrm.ftln == PlayLineOrm.ftln)
            .where(LineTopicOrm.topic_id == topic_id)
            .order_by(PlayLineOrm.ftln)
        )
        return [play_line_to_entity(row) for row in result.scalars().all()]

    async def search_similar_chunks(self, query: str, limit: int = 5) -> list[ScoredPlayChunk]:
        # Searches the paraphrase embedding, not the archaic original — see
        # seed_play_chunks.py for why (modern-English query vs. Early Modern
        # English text otherwise rarely embed close enough to match).
        query_vector = await self._embedder.embed_query(query)
        distance_expr = PlayChunkOrm.embedding.cosine_distance(query_vector)
        result = await self._session.execute(
            select(PlayChunkOrm, distance_expr.label("distance"))
            .where(PlayChunkOrm.embedding.is_not(None))
            .order_by(distance_expr)
            .limit(limit)
        )
        return [
            ScoredPlayChunk(chunk=play_chunk_to_entity(row), cosine_distance=float(distance))
            for row, distance in result.all()
        ]

    async def get_chunk(self, ftln_start: int, ftln_end: int) -> PlayChunk | None:
        result = await self._session.execute(
            select(PlayChunkOrm).where(
                PlayChunkOrm.ftln_start == ftln_start,
                PlayChunkOrm.ftln_end == ftln_end,
            )
        )
        orm = result.scalars().first()
        return play_chunk_to_entity(orm) if orm else None