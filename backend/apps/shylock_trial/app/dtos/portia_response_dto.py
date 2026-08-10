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
    tubal_used_scenes: tuple[str, ...] = ()
    presented_evidence: tuple[str, ...] = ()
    folger_context: str | None = None
    # Who request_type=reaction should be voiced as — "PORTIA" (default) for
    # every scene except the explicit opt-in set in
    # scene_progression.REACTOR_OVERRIDE_SCENES. See portia_prompt.py's
    # _reaction_instruction for how this branches the prompt, and
    # trial_progression_interactor._build_portia_prompt for where it's resolved.
    reactor_speaker: str = "PORTIA"
    reactor_speaker_label: str = "포샤"


@dataclass(frozen=True, slots=True)
class PortiaResponseResultDto:
    text: str
    fallback_used: bool = False
    # Echoes PortiaResponsePromptDto.reactor_speaker/_label so callers (the
    # trial_progression response) know who actually spoke without re-deriving
    # it from scene data themselves.
    speaker: str = "PORTIA"
    speaker_label: str = "포샤"
