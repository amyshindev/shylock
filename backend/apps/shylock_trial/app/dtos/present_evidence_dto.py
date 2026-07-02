from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PresentEvidenceInputDto:
    trial_id: UUID
    scene_id: str
    evidence_id: str
    evidence_text: str


@dataclass(frozen=True, slots=True)
class PresentEvidenceResultDto:
    trial_id: UUID
    shylock_hp: int
    dp: int
    contradiction_valid: bool
    portia_response: str
