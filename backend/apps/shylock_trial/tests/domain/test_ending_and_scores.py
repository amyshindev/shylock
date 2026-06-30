import pytest

from shylock_trial.app.constants.ending_type_map import EndingType, resolve_ending_type
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


@pytest.mark.parametrize(
    ("dignity", "expected"),
    [
        (70, EndingType.VICTORY),
        (85, EndingType.VICTORY),
        (40, EndingType.STANDARD_DEFEAT),
        (69, EndingType.STANDARD_DEFEAT),
        (39, EndingType.SILENT_DEFEAT),
    ],
)
def test_resolve_ending_type(dignity: int, expected: EndingType) -> None:
    assert resolve_ending_type(dignity) == expected


def test_dignity_score_clamps() -> None:
    assert DignityScore(150).value == 100
    assert DignityScore(-10).value == 0

    updated = DignityScore(50).apply_delta(30)
    assert updated.value == 80
