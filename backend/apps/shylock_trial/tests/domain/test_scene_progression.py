import pytest

from shylock_trial.app.constants.scene_progression import (
    ALIEN_LAW_SCENE_INDEX,
    JESSICA_DUET_SCENE_INDEX,
    JESSICA_INTERVENTION_SCENE_INDEX,
    is_narrative_complete,
    resolve_next_scene_index,
)


@pytest.mark.parametrize(
    ("scene_index", "expected"),
    [
        (0, 1),
        (6, JESSICA_DUET_SCENE_INDEX),
        (JESSICA_DUET_SCENE_INDEX, ALIEN_LAW_SCENE_INDEX),
        (ALIEN_LAW_SCENE_INDEX, JESSICA_INTERVENTION_SCENE_INDEX),
        (JESSICA_INTERVENTION_SCENE_INDEX, None),
    ],
)
def test_resolve_next_scene_index(scene_index: int, expected: int | None) -> None:
    assert resolve_next_scene_index(scene_index, dp=50) == expected


@pytest.mark.parametrize(
    ("scene_index", "expected"),
    [
        (ALIEN_LAW_SCENE_INDEX, False),
        (JESSICA_DUET_SCENE_INDEX, False),
        (JESSICA_INTERVENTION_SCENE_INDEX, True),
    ],
)
def test_is_narrative_complete(scene_index: int, expected: bool) -> None:
    assert is_narrative_complete(scene_index, dp=50) == expected
