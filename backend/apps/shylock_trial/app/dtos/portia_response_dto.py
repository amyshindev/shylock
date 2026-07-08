from dataclasses import dataclass
from uuid import UUID

from shylock_trial.domain.entities.trial_entity import TrialPhase


@dataclass(frozen=True, slots=True)
class PortiaResponsePromptDto:
    trial_id: UUID
    scene_index: int
    dp: int
    phase: TrialPhase
    choice_history: tuple[str, ...]
    context: str
    request_type: str  # "narration" | "reaction" | "ending"
    portia_hp: int = 100
    choice_id: str | None = None
    previous_portia_reactions: tuple[str, ...] = ()
    previous_portia_stances: tuple[str, ...] = ()
    tubal_used_scenes: tuple[str, ...] = ()
    presented_evidence: tuple[str, ...] = ()
    folger_context: str | None = None


@dataclass(frozen=True, slots=True)
class PortiaResponseResultDto:
    text: str
    fallback_used: bool = False
    stance: str | None = None
