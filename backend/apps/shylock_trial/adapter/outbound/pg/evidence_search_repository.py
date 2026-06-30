from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]:
        # TODO: embed query via EvidenceEmbeddingClient and pgvector cosine search
        result = await self._session.execute(select(PlayLineOrm).limit(input_dto.limit))
        return [play_line_to_entity(row) for row in result.scalars().all()]

    async def list_curated_evidence(self) -> list[Evidence]:
        result = await self._session.execute(select(EvidenceOrm))
        return [evidence_to_entity(row) for row in result.scalars().all()]

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        orm = await self._session.get(EvidenceOrm, evidence_id)
        return evidence_to_entity(orm) if orm else None
