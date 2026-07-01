from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TubalAgentResult:
    success: bool
    ftln: int | None = None
    passage: str | None = None
    speaker: str | None = None
    act_scene: str | None = None
    tubal_comment: str | None = None
