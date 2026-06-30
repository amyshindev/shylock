from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from shylock_trial.domain.value_objects.confidence_score_vo import ConfidenceScore
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


class TrialPhase(StrEnum):
    IN_PROGRESS = "in_progress"
    ENDED = "ended"


@dataclass(frozen=True, slots=True)
class Choice:
    choice_id: str
    label: str
    dignity_delta: int
    confidence_delta: int
    evidence_id: str | None = None
    is_climax: bool = False


@dataclass(frozen=True, slots=True)
class Scene:
    scene_index: int
    speaker: str
    dialogue: str
    choices: tuple[Choice, ...]


@dataclass(slots=True)
class Trial:
    trial_id: UUID
    scene_index: int
    dignity: DignityScore
    confidence: ConfidenceScore
    choice_history: list[str]
    phase: TrialPhase
    narration_text: str | None = None

    def is_ended(self) -> bool:
        return self.phase == TrialPhase.ENDED
