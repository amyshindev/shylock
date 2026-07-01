from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PortiaPresentAgentResult:
    contradiction_valid: bool
    portia_response: str
    portia_hp_change: int
    reasoning: str = ""
