import pytest

from shylock_trial.app.constants.ending_type_map import EndingType, resolve_ending_type
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore


@pytest.mark.parametrize(
    ("dp", "expected"),
    [
        (90, EndingType.RESCUED),
        (100, EndingType.RESCUED),
        (89, EndingType.FOUGHT_TO_END),
        (80, EndingType.FOUGHT_TO_END),
        (60, EndingType.DIGNITY_KEPT),
        (79, EndingType.DIGNITY_KEPT),
        (40, EndingType.SURVIVED),
        (59, EndingType.SURVIVED),
        (39, EndingType.SILENT),
        (0, EndingType.SILENT),
    ],
)
def test_resolve_ending_type(dp: int, expected: EndingType) -> None:
    assert resolve_ending_type(dp) == expected


def test_dp_score_clamps() -> None:
    assert DpScore(150).value == 100
    assert DpScore(-10).value == 0

    updated = DpScore(50).apply_delta(30)
    assert updated.value == 80


def test_hp_score_clamps() -> None:
    assert HpScore(150).value == 100
    assert HpScore(-10).value == 0

    updated = HpScore(100).apply_delta(-30)
    assert updated.value == 70
