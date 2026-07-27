from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    EvidenceSearchResultDto,
    EvidenceSearchScoredResultDto,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine


class EvidenceSearchInteractor(EvidenceSearchUseCase):
    def __init__(self, port: EvidenceSearchPort) -> None:
        self._port = port

    async def search(self, input_dto: EvidenceSearchInputDto) -> EvidenceSearchResultDto:
        play_lines = await self._port.search_similar_play_lines(input_dto)
        return EvidenceSearchResultDto(play_lines=tuple(play_lines[: input_dto.limit]))

    async def search_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> EvidenceSearchScoredResultDto:
        scored_lines = await self._port.search_similar_play_lines_scored(input_dto)
        return EvidenceSearchScoredResultDto(
            scored_lines=tuple(scored_lines[: input_dto.limit]),
        )

    async def list_curated_evidence(self) -> list[Evidence]:
        return await self._port.list_curated_evidence()

    async def get_evidence(self, evidence_id: str) -> Evidence | None:
        return await self._port.find_evidence_by_id(evidence_id)

    async def get_line_context(
        self, ftln_start: int, ftln_end: int, radius: int = 2
    ) -> list[PlayLine]:
        return await self._port.get_line_context(ftln_start, ftln_end, radius)
