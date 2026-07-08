import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.mappers.evidence_search_mapper import (
    evidence_to_entity,
    play_line_to_entity,
)
from shylock_trial.adapter.outbound.orm.play_line_orm import EvidenceOrm, PlayLineOrm
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto, ScoredPlayLine
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
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