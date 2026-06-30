from dataclasses import dataclass

from shylock_trial.domain.entities.play_line_entity import PlayLine


@dataclass(frozen=True, slots=True)
class EvidenceSearchInputDto:
    query: str
    evidence_id: str | None = None
    limit: int = 5


@dataclass(frozen=True, slots=True)
class EvidenceSearchResultDto:
    play_lines: tuple[PlayLine, ...]
