from dataclasses import dataclass

from shylock_trial.app.constants.game_balance import PORTIA_HP_MAX


@dataclass(frozen=True, slots=True)
class PortiaHpScore:
    value: int

    MIN = 0
    MAX = PORTIA_HP_MAX

    def __post_init__(self) -> None:
        clamped = max(self.MIN, min(self.MAX, self.value))
        object.__setattr__(self, "value", clamped)

    def apply_delta(self, delta: int) -> "PortiaHpScore":
        return PortiaHpScore(self.value + delta)
