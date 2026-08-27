from dataclasses import dataclass
from typing import Literal
from uuid import UUID

DukeVerdictResult = Literal["win", "lose"]


@dataclass(frozen=True, slots=True)
class DukeVerdictPromptDto:
    """Only built for "bold" choices (ChoiceEffect.dp_delta > 0) — see
    trial_progression_interactor.submit_choice. Concede/silent choices
    (dp_delta <= 0) are a foregone conclusion and never reach the judge."""

    trial_id: UUID
    scene_index: int
    choice_id: str
    choice_brief: str
    stimulus: str
    dp: int
    portia_hp: int
    round_number: int


@dataclass(frozen=True, slots=True)
class DukeVerdictResultDto:
    result: DukeVerdictResult
    line: str
    fallback_used: bool = False
