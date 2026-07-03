import pytest

from shylock_trial.app.constants.scene_progression import (
    JESSICA_DUET_SCENE_INDEX,
    JESSICA_INTERVENTION_SCENE_INDEX,
    is_narrative_complete,
    resolve_next_scene_index,
)


@pytest.mark.parametrize(
    ("scene_index", "dp", "expected"),
    [
        (0, 50, 1),
        (6, 50, 7),
        (7, 89, None),
        (7, 90, JESSICA_DUET_SCENE_INDEX),
        (8, 90, JESSICA_INTERVENTION_SCENE_INDEX),
        (9, 90, None),
    ],
)
def test_resolve_next_scene_index(scene_index: int, dp: int, expected: int | None) -> None:
    assert resolve_next_scene_index(scene_index, dp) == expected


@pytest.mark.parametrize(
    ("scene_index", "dp", "expected"),
    [
        (7, 89, True),
        (7, 90, False),
        (8, 90, False),
        (9, 90, True),
    ],
)
def test_is_narrative_complete(scene_index: int, dp: int, expected: bool) -> None:
    assert is_narrative_complete(scene_index, dp) == expected
