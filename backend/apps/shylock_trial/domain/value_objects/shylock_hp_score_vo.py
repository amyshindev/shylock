from dataclasses import dataclass

from shylock_trial.app.constants.game_balance import SHYLOCK_HP_MAX


@dataclass(frozen=True, slots=True)
class ShylockHpScore:
    value: int

    MIN = 0
    MAX = SHYLOCK_HP_MAX

    def __post_init__(self) -> None:
        clamped = max(self.MIN, min(self.MAX, self.value))
        object.__setattr__(self, "value", clamped)

    def apply_delta(self, delta: int) -> "ShylockHpScore":
        return ShylockHpScore(self.value + delta)
