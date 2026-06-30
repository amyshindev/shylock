from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayLine:
    ftln: int
    speaker: str
    text: str
    act_scene: str
