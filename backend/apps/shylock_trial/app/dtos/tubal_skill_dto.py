from dataclasses import dataclass
from uuid import UUID

from shylock_trial.app.dtos.tubal_agent_dto import TubalAgentResult


@dataclass(frozen=True, slots=True)
class TubalSkillInputDto:
    trial_id: UUID
    portia_claim: str | None = None
    scene_id: str | None = None


@dataclass(frozen=True, slots=True)
class TubalSkillResultDto:
    trial_id: UUID
    dp: int
    shylock_hp: int
    agent: TubalAgentResult
    tubal_enhanced_choices: dict[str, str]
