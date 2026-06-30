from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    quote: str
    act_scene: str
    icon: str
    description: str
    source_ftln_range: tuple[int, int]
