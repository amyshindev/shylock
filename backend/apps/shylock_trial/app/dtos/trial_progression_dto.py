from dataclasses import dataclass
from uuid import UUID

from shylock_trial.app.constants.ending_type_map import EndingType
from shylock_trial.domain.entities.trial_entity import TrialPhase


@dataclass(frozen=True, slots=True)
class StartTrialResultDto:
    trial_id: UUID
    scene_index: int
    dignity: int
    confidence: int
    phase: TrialPhase
    narration_text: str


@dataclass(frozen=True, slots=True)
class SubmitChoiceInputDto:
    trial_id: UUID
    choice_id: str


@dataclass(frozen=True, slots=True)
class SubmitChoiceResultDto:
    trial_id: UUID
    scene_index: int
    dignity: int
    confidence: int
    phase: TrialPhase
    portia_response: str
    ending_type: EndingType | None
    is_ending: bool


@dataclass(frozen=True, slots=True)
class AdvanceSceneResultDto:
    trial_id: UUID
    scene_index: int
    scene_data: dict


@dataclass(frozen=True, slots=True)
class GenerateEndingResultDto:
    trial_id: UUID
    ending_type: EndingType
    ending_text: str
    dignity: int
    confidence: int
