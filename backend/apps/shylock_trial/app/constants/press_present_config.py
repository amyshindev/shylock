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


CROWD_JEERS_PRESS_PRESENT = PressPresentSceneConfig(
    scene_id="crowd_jeers",
    testimony=(
        PressPresentTestimony(
            statement_id="t1",
            text="저 유대인을 보라! 자비도 모르는 자가!",
            press_reaction="그렇소! 법만 따를 뿐이오!",
        ),
        PressPresentTestimony(
            statement_id="t2",
            text="이 자는 인간이 아니라 짐승이오.",
            press_reaction="짐승이라니... 계속하시오.",
        ),
    ),
    contradiction=PressPresentContradiction(
        statement_id="t2",
        evidence_id="hath_not",
    ),
)

PRESS_PRESENT_BY_SCENE_ID: dict[str, PressPresentSceneConfig] = {
    CROWD_JEERS_PRESS_PRESENT.scene_id: CROWD_JEERS_PRESS_PRESENT,
}

PRESENT_EVIDENCE_PORTIA_HP_SUCCESS = -15
PRESENT_EVIDENCE_PORTIA_HP_FAIL = 5
