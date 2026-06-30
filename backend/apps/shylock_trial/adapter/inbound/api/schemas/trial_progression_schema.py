from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from shylock_trial.domain.entities.trial_entity import TrialPhase


class StartTrialResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 0,
                    "dignity": 50,
                    "confidence": 50,
                    "phase": "in_progress",
                    "narration_text": "The court of Venice assembles...",
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    dignity: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    phase: TrialPhase
    narration_text: str


class TrialResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 1,
                    "dignity": 55,
                    "confidence": 48,
                    "phase": "in_progress",
                    "choice_history": ["appeal_mercy"],
                    "narration_text": None,
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    dignity: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    phase: TrialPhase
    choice_history: list[str]
    narration_text: str | None = None


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
                    "dignity": 60,
                    "confidence": 52,
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
    dignity: int
    confidence: int
    phase: TrialPhase
    portia_response: str
    ending_type: str | None = None
    is_ending: bool


class AdvanceSceneResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "scene_index": 2,
                    "scene_data": {"scene_index": 2},
                }
            ]
        }
    )

    trial_id: UUID
    scene_index: int
    scene_data: dict


class EndingResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "ending_type": "victory",
                    "ending_text": "Justice tempered with mercy prevails.",
                    "dignity": 72,
                    "confidence": 65,
                }
            ]
        }
    )

    trial_id: UUID
    ending_type: str
    ending_text: str
    dignity: int
    confidence: int
