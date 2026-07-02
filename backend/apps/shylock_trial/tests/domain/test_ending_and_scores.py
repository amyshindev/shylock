import pytest

from shylock_trial.app.constants.ending_type_map import EndingType, resolve_ending_type
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore


@pytest.mark.parametrize(
    ("dp", "shylock_hp", "expected"),
    [
        (70, 40, EndingType.HISTORY_CHANGED),
        (85, 50, EndingType.HISTORY_CHANGED),
        (40, 40, EndingType.SURVIVAL),
        (69, 45, EndingType.SURVIVAL),
        (70, 39, EndingType.DIGNITY),
        (85, 20, EndingType.DIGNITY),
        (40, 20, EndingType.BAD),
        (69, 10, EndingType.BAD),
    ],
)
def test_resolve_ending_type(dp: int, shylock_hp: int, expected: EndingType) -> None:
    assert resolve_ending_type(dp, shylock_hp) == expected


def test_dp_score_clamps() -> None:
    assert DpScore(150).value == 100
    assert DpScore(-10).value == 0

    updated = DpScore(50).apply_delta(30)
    assert updated.value == 80


def test_shylock_hp_score_clamps() -> None:
    assert ShylockHpScore(100).value == 60
    assert ShylockHpScore(-10).value == 0

    updated = ShylockHpScore(50).apply_delta(-10)
    assert updated.value == 40


@pytest.mark.parametrize(
    ("shylock_hp", "expected"),
    [
        (39, True),
        (40, False),
        (60, False),
    ],
)
def test_alien_law_executed_from_shylock_hp(shylock_hp: int, expected: bool) -> None:
    assert (shylock_hp < 40) is expected
