import pytest

from shylock_trial.app.constants.ending_type_map import EndingType, resolve_ending_type
from shylock_trial.domain.value_objects.dp_score_vo import DpScore


@pytest.mark.parametrize(
    ("dp", "expected"),
    [
        (80, EndingType.FOUGHT_TO_END),
        (100, EndingType.FOUGHT_TO_END),
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
