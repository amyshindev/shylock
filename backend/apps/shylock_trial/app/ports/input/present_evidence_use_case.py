from abc import ABC, abstractmethod

from shylock_trial.app.dtos.present_evidence_dto import (
    PresentEvidenceInputDto,
    PresentEvidenceResultDto,
)


class PresentEvidenceUseCase(ABC):
    @abstractmethod
    async def present_evidence(
        self,
        input_dto: PresentEvidenceInputDto,
    ) -> PresentEvidenceResultDto: ...
