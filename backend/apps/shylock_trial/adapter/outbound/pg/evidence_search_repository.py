from pgvector.sqlalchemy import Vector
from sqlalchemy import select, cast
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.client.evidence_embedding_client import EvidenceEmbeddingClient
from shylock_trial.adapter.outbound.mappers.evidence_search_mapper import (
    evidence_to_entity,
    play_line_to_entity,
)
from shylock_trial.adapter.outbound.orm.play_line_orm import EvidenceOrm, PlayLineOrm
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine


class EvidenceSearchPgRepository(EvidenceSearchPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._embedder = EvidenceEmbeddingClient()

    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]:
        query_vector = await self._embedder.embed_query(input_dto.query)
        result = await self._session.execute(
            select(PlayLineOrm)
            .order_by(PlayLineOrm.embedding.cosine_distance(query_vector))
            .limit(input_dto.limit)
        )
        return [play_line_to_entity(row) for row in result.scalars().all()]

    async def list_curated_evidence(self) -> list[Evidence]:
        result = await self._session.execute(select(EvidenceOrm))
        return [evidence_to_entity(row) for row in result.scalars().all()]

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        orm = await self._session.get(EvidenceOrm, evidence_id)
        return evidence_to_entity(orm) if orm else None