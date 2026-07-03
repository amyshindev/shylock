from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PresentEvidenceRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "scene_id": "example_press_present_scene",
                    "evidence_id": "hath_not",
                    "evidence_text": "Hath not a Jew eyes? If you prick us, do we not bleed?",
                }
            ]
        }
    )

    scene_id: str
    evidence_id: str
    evidence_text: str


class PresentEvidenceResponse(BaseModel):
    trial_id: UUID
    dp: int
    contradiction_valid: bool
    portia_response: str
