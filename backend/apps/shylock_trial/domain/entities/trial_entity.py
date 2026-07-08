from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialogueContent
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore


class TrialPhase(StrEnum):
    IN_PROGRESS = "in_progress"
    ENDED = "ended"


@dataclass(frozen=True, slots=True)
class Choice:
    choice_id: str
    label: str
    dp_delta: int
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
    dp: DpScore
    hp: HpScore
    portia_hp: PortiaHpScore
    choice_history: list[str]
    phase: TrialPhase
    narration_text: str | None = None
    scene_dialogues: dict[int, SceneDialogueContent] = field(default_factory=dict)
    tubal_used_scenes: tuple[str, ...] = ()
    presented_evidence: tuple[str, ...] = ()
    tubal_enhanced_choices: dict[str, str] = field(default_factory=dict)
    venice_dp_shield: bool = False
    venice_paradox_used: bool = False
    portia_reactions: list[str] = field(default_factory=list)

    def is_ended(self) -> bool:
        return self.phase == TrialPhase.ENDED
