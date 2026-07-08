from abc import ABC, abstractmethod

from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    EvidenceSearchResultDto,
    EvidenceSearchScoredResultDto,
)
from shylock_trial.domain.entities.evidence_entity import Evidence


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
