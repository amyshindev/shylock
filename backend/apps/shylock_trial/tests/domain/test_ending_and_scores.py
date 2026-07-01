import pytest

from shylock_trial.app.constants.ending_type_map import EndingType, resolve_ending_type
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore


@pytest.mark.parametrize(
    ("dp", "alien_law_executed", "expected"),
    [
        (70, True, EndingType.DIGNITY),
        (85, True, EndingType.DIGNITY),
        (69, True, EndingType.BAD),
        (40, True, EndingType.BAD),
        (70, False, EndingType.HISTORY_CHANGED),
        (69, False, EndingType.SURVIVAL),
    ],
)
def test_resolve_ending_type(dp: int, alien_law_executed: bool, expected: EndingType) -> None:
    assert resolve_ending_type(dp, alien_law_executed) == expected


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
