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
    alien_law_executed: bool
    phase: TrialPhase
    portia_response: str
    ending_type: EndingType | None
    is_ending: bool
    tubal_enhanced_choices: dict[str, str]


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
    alien_law_executed: bool


@dataclass(frozen=True, slots=True)
class LauncelotSkillResultDto:
    trial_id: UUID
    dp: int
    shylock_hp: int
    launcelot_comment: str = (
        "론슬롯이 갑자기 법정으로 뛰어들었다! "
        "모두가 당황하여 잠시 말을 잃었다."
    )


@dataclass(frozen=True, slots=True)
class VeniceContradictionSkillResultDto:
    trial_id: UUID
    dp: int
    shylock_hp: int
    skill_comment: str = (
        "당신들은 나를 고리대금업자라 부르오.\n"
        "하지만 당신들이 내게 허락한 것이 그것뿐이었소.\n"
        "이것이 베니스의 정의요?"
    )
