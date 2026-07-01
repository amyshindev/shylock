from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TubalSkillRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "portia_claim": "자비를 베풀라고? 계약은 법이다.",
                    "scene_id": "portia_opens",
                }
            ]
        }
    )

    portia_claim: str | None = None
    scene_id: str | None = None


class TubalSkillResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trial_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "dp": 20,
                    "shylock_hp": 55,
                    "portia_hp": 100,
                    "success": True,
                    "ftln": 1001501,
                    "passage": "The quality of mercy is not strained.",
                    "speaker": "Portia",
                    "act_scene": "1.5",
                    "tubal_comment": "이 구절이 포샤의 주장을 꺾는다.",
                }
            ]
        }
    )

    trial_id: UUID
    dp: int
    shylock_hp: int
    portia_hp: int
    success: bool
    ftln: int | None = None
    passage: str | None = None
    speaker: str | None = None
    act_scene: str | None = None
    tubal_comment: str | None = None
