from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    EvidenceSearchResultDto,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence


class EvidenceSearchInteractor(EvidenceSearchUseCase):
    def __init__(self, port: EvidenceSearchPort) -> None:
        self._port = port

    async def search(self, input_dto: EvidenceSearchInputDto) -> EvidenceSearchResultDto:
        play_lines = await self._port.search_similar_play_lines(input_dto)
        return EvidenceSearchResultDto(play_lines=tuple(play_lines[: input_dto.limit]))

    async def list_curated_evidence(self) -> list[Evidence]:
        return await self._port.list_curated_evidence()

    async def get_evidence(self, evidence_id: str) -> Evidence | None:
        return await self._port.find_evidence_by_id(evidence_id)
