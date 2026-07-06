from dataclasses import dataclass
from uuid import UUID

from shylock_trial.app.constants.ending_type_map import EndingType
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueContent
from shylock_trial.domain.entities.trial_entity import TrialPhase


@dataclass(frozen=True, slots=True)
class StartTrialResultDto:
    trial_id: UUID
    scene_index: int
    dp: int
    hp: int
    portia_hp: int
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
    dp: int
    hp: int
    portia_hp: int
    phase: TrialPhase
    portia_response: str
    ending_type: EndingType | None
    is_ending: bool
    tubal_enhanced_choices: dict[str, str]
    venice_dp_shield: bool


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
    dp: int


@dataclass(frozen=True, slots=True)
class LauncelotSkillResultDto:
    trial_id: UUID
    dp: int
    hp: int
    launcelot_comment: str = (
        "론슬롯이 갑자기 법정으로 뛰어들었다! "
        "모두가 당황하여 잠시 말을 잃었다. "
        "이 틈을 타 숨을 고르자..."
    )


@dataclass(frozen=True, slots=True)
class VeniceParadoxSkillResultDto:
    trial_id: UUID
    dp: int
    hp: int
    venice_paradox_used: bool
    skill_comment: str = (
        "당신들은 나를 고리대금업자라 부르오.\n"
        "허나 묻겠소 — 내가 상인이 되는 것을 당신들의 길드가 허락했소?\n"
        "내가 땅을 사는 것을, 당신들의 법이 허락했소?\n"
        "당신들은 내게 문을 하나만 열어두고, 그 문으로 들어온 나를 손가락질하며 더럽다 하는구려.\n"
        "돈을 빌려주는 것. 그것이 당신들이 내게 허락한 유일한 일이었소.\n"
        "그리고 이제 와서, 내가 그 일을 너무 잘한다고 나를 벌하려 하시오?\n"
        "이것이 베니스의 정의요?\n"
        "당신들이 내게 증오를 가르쳤다면, 나는 그저 훌륭한 학생이었을 뿐이오."
    )
