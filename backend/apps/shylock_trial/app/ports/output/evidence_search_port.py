from abc import ABC, abstractmethod

from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine


class EvidenceSearchPort(ABC):
    @abstractmethod
    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]: ...

    @abstractmethod
    async def list_curated_evidence(self) -> list[Evidence]: ...

    @abstractmethod
    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None: ...
