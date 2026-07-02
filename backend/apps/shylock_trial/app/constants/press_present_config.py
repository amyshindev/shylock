"""Press/Present interaction config per scene."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PressPresentTestimony:
    statement_id: str
    text: str
    press_reaction: str


@dataclass(frozen=True, slots=True)
class PressPresentContradiction:
    statement_id: str
    evidence_id: str


@dataclass(frozen=True, slots=True)
class PressPresentSceneConfig:
    scene_id: str
    testimony: tuple[PressPresentTestimony, ...]
    contradiction: PressPresentContradiction


PRESS_PRESENT_BY_SCENE_ID: dict[str, PressPresentSceneConfig] = {}
