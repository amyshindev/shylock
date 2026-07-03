from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase


class SceneDialogueLineResponse(BaseModel):
    text: str
    kind: Literal["speech", "narration"]
    speaker: str | None = None


class SceneDialogueResponse(BaseModel):
    lines: list[SceneDialogueLineResponse]
    challenge_header: str | None = None
    challenge_text: str | None = None
    choice_texts: dict[str, str] = Field(default_factory=dict)


def scene_dialogue_from_trial(trial: Trial) -> SceneDialogueResponse | None:
    content = trial.scene_dialogues.get(trial.scene_index)
    if content is None:
        return None
    return SceneDialogueResponse(
        lines=[
            SceneDialogueLineResponse(text=line.text, kind=line.kind.value, speaker=line.speaker)
            for line in content.lines
        ],
        challenge_header=content.challenge_header,
        challenge_text=content.challenge_text,
        choice_texts=content.choice_text_map(),
    )


class StartTrialResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 0,
                    "dp": 50,
                    "phase": "in_progress",
                    "scene_dialogue": {
                        "lines": [{"text": "베네치아 법정. 1596년.", "kind": "narration"}],
                        "challenge_header": None,
                        "challenge_text": None,
                        "choice_texts": {},
                    },
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    dp: int = Field(ge=0, le=100)
    phase: TrialPhase
    scene_dialogue: SceneDialogueResponse


class TrialResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 1,
                    "dp": 55,
                    "phase": "in_progress",
                    "choice_history": ["appeal_mercy"],
                    "narration_text": None,
                    "scene_dialogue": {
                        "lines": [
                            {"text": "샤일록, 당신은 안토니오의 살 1파운드를 요구하오.", "kind": "speech"}
                        ],
                        "challenge_header": "▶ 샤일록의 선택",
                        "challenge_text": "자비를 베풀라고?",
                        "choice_texts": {"appeal_contract": "계약은 법적으로 유효합니다"},
                    },
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    dp: int = Field(ge=0, le=100)
    phase: TrialPhase
    choice_history: list[str]
    narration_text: str | None = None
    scene_dialogue: SceneDialogueResponse | None = None
    tubal_enhanced_choices: dict[str, str] = Field(default_factory=dict)
    venice_dp_shield: bool = False


class SubmitChoiceRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"choice_id": "appeal_mercy"}]}
    )

    choice_id: str


class SubmitChoiceResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 1,
                    "dp": 60,
                    "phase": "in_progress",
                    "portia_response": "The quality of mercy is not strained...",
                    "ending_type": None,
                    "is_ending": False,
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    dp: int
    phase: TrialPhase
    portia_response: str
    ending_type: str | None = None
    is_ending: bool
    tubal_enhanced_choices: dict[str, str] = Field(default_factory=dict)
    venice_dp_shield: bool = False


class AdvanceSceneResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 2,
                    "scene_data": {"scene_index": 2},
                    "scene_dialogue": {
                        "lines": [{"text": '"저 유대인을 보라!"', "kind": "speech"}],
                        "challenge_header": "▶ 샤일록의 선택",
                        "challenge_text": "군중의 조롱에 당신은—",
                        "choice_texts": {"show_gaberdine": "외투의 침 자국을 보여준다"},
                    },
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    scene_data: dict
    scene_dialogue: SceneDialogueResponse


class EndingResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-5717-4562-b3fc-2c963f66afa6",
                    "ending_type": "dignity_kept_ending",
                    "ending_text": "Justice tempered with mercy prevails.",
                    "dp": 72,
                }
            ]
        }
    )

    trial_id: UUID
    ending_type: str
    ending_text: str
    dp: int


class LauncelotSkillResponse(BaseModel):
    trial_id: UUID
    dp: int
    launcelot_comment: str


class VeniceContradictionSkillResponse(BaseModel):
    trial_id: UUID
    dp: int
    venice_dp_shield: bool
    skill_comment: str
