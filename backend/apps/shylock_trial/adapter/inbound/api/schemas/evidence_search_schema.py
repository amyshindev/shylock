from pydantic import BaseModel, ConfigDict, Field


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "evidence_id": "mercy",
                    "quote": "The quality of mercy is not strained",
                    "act_scene": "4.1",
                    "icon": "scale",
                    "description": "Portia's plea for mercy",
                    "source_ftln_start": 1820,
                    "source_ftln_end": 1845,
                }
            ]
        }
    )

    evidence_id: str
    quote: str
    act_scene: str
    icon: str
    description: str
    source_ftln_start: int
    source_ftln_end: int


class PlayLineResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ftln": 1820,
                    "speaker": "PORTIA",
                    "text": "The quality of mercy is not strained;",
                    "act_scene": "4.1",
                }
            ]
        }
    )

    ftln: int
    speaker: str
    text: str
    act_scene: str


class RelatedPlayLinesResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "evidence_id": "mercy",
                    "play_lines": [
                        {
                            "ftln": 1820,
                            "speaker": "PORTIA",
                            "text": "The quality of mercy is not strained;",
                            "act_scene": "4.1",
                        }
                    ],
                }
            ]
        }
    )

    evidence_id: str
    play_lines: list[PlayLineResponse] = Field(default_factory=list)
