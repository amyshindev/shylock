from abc import ABC, abstractmethod

from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    EvidenceSearchResultDto,
    EvidenceSearchScoredResultDto,
)
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine


class EvidenceSearchUseCase(ABC):
    @abstractmethod
    async def search(self, input_dto: EvidenceSearchInputDto) -> EvidenceSearchResultDto: ...

    @abstractmethod
    async def search_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> EvidenceSearchScoredResultDto: ...

    @abstractmethod
    async def list_curated_evidence(self) -> list[Evidence]: ...

    @abstractmethod
    async def get_evidence(self, evidence_id: str) -> Evidence | None: ...

    @abstractmethod
    async def get_line_context(
        self, ftln_start: int, ftln_end: int, radius: int = 2
    ) -> list[PlayLine]: ...
