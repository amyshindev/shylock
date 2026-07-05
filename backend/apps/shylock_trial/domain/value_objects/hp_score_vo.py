from dataclasses import dataclass

from shylock_trial.app.constants.game_balance import HP_MAX


@dataclass(frozen=True, slots=True)
class HpScore:
    value: int

    MIN = 0
    MAX = HP_MAX

    def __post_init__(self) -> None:
        clamped = max(self.MIN, min(self.MAX, self.value))
        object.__setattr__(self, "value", clamped)

    def apply_delta(self, delta: int) -> "HpScore":
        return HpScore(self.value + delta)
