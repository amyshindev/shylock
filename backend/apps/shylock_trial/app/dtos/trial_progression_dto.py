from dataclasses import dataclass
from uuid import UUID

from shylock_trial.app.constants.ending_type_map import EndingType
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueContent
from shylock_trial.domain.entities.trial_entity import TrialPhase


@dataclass(frozen=True, slots=True)
class StartTrialResultDto:
    trial_id: UUID
    scene_index: int
    shylock_hp: int
    dp: int
    portia_hp: int
    alien_law_executed: bool
    phase: TrialPhase
    scene_dialogue: SceneDialogueContent


@dataclass(frozen=True, slots=True)
class SubmitChoiceInputDto:
    trial_id: UUID
    choice_id: str


@dataclass(frozen=True, slots=True)
class SubmitChoiceResultDto:
    trial_id: UUID
    scene_index: int
    shylock_hp: int
    dp: int
    portia_hp: int
    alien_law_executed: bool
    phase: TrialPhase
    portia_response: str
    ending_type: EndingType | None
    is_ending: bool


@dataclass(frozen=True, slots=True)
class AdvanceSceneResultDto:
    trial_id: UUID
    scene_index: int
    scene_data: dict
    scene_dialogue: SceneDialogueContent


@dataclass(frozen=True, slots=True)
class GenerateEndingResultDto:
    trial_id: UUID
    ending_type: EndingType
    ending_text: str
    shylock_hp: int
    dp: int
    portia_hp: int
    alien_law_executed: bool
