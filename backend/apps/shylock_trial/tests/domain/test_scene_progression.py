import pytest

from shylock_trial.app.constants.scene_progression import (
    ALIEN_LAW_SCENE_INDEX,
    JESSICA_DUET_SCENE_INDEX,
    JESSICA_INTERVENTION_SCENE_INDEX,
    is_narrative_complete,
    resolve_next_scene_index,
)


@pytest.mark.parametrize(
    ("scene_index", "portia_hp", "expected"),
    [
        (0, 100, 1),
        (4, 50, JESSICA_DUET_SCENE_INDEX),
        (JESSICA_DUET_SCENE_INDEX, 50, JESSICA_DUET_SCENE_INDEX + 1),
        (7, 50, ALIEN_LAW_SCENE_INDEX),
        (ALIEN_LAW_SCENE_INDEX, 0, JESSICA_INTERVENTION_SCENE_INDEX),
        (ALIEN_LAW_SCENE_INDEX, 1, None),
        (JESSICA_INTERVENTION_SCENE_INDEX, 0, None),
    ],
)
def test_resolve_next_scene_index(
    scene_index: int,
    portia_hp: int,
    expected: int | None,
) -> None:
    assert resolve_next_scene_index(scene_index, portia_hp=portia_hp) == expected


@pytest.mark.parametrize(
    ("scene_index", "portia_hp", "expected"),
    [
        (ALIEN_LAW_SCENE_INDEX, 50, True),
        (ALIEN_LAW_SCENE_INDEX, 1, True),
        (ALIEN_LAW_SCENE_INDEX, 0, False),
        (JESSICA_DUET_SCENE_INDEX, 50, False),
        (JESSICA_INTERVENTION_SCENE_INDEX, 0, True),
    ],
)
def test_is_narrative_complete(
    scene_index: int,
    portia_hp: int,
    expected: bool,
) -> None:
    assert is_narrative_complete(scene_index, portia_hp=portia_hp) == expected
