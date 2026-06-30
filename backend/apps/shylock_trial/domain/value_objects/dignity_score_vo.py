from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DignityScore:
    value: int

    MIN = 0
    MAX = 100

    def __post_init__(self) -> None:
        clamped = max(self.MIN, min(self.MAX, self.value))
        object.__setattr__(self, "value", clamped)

    def apply_delta(self, delta: int) -> "DignityScore":
        return DignityScore(self.value + delta)
