"""Scene index constants and linear narrative progression."""

CROWD_JEERS_SCENE_INDEX = 3
JESSICA_DUET_SCENE_INDEX = 7
ALIEN_LAW_SCENE_INDEX = 8
JESSICA_INTERVENTION_SCENE_INDEX = 9
LAST_SCENE_INDEX = JESSICA_INTERVENTION_SCENE_INDEX

# Legacy name kept for callers that mean "last catalogued scene index".
FINAL_SCENE_INDEX = LAST_SCENE_INDEX


def resolve_next_scene_index(scene_index: int, dp: int) -> int | None:
    """Return the next scene index, or None when the narrative should end."""
    del dp  # narrative order is fixed; DP no longer gates Jessica scenes
    if scene_index < LAST_SCENE_INDEX:
        return scene_index + 1
    return None


def is_narrative_complete(scene_index: int, dp: int) -> bool:
    del dp
    return scene_index == LAST_SCENE_INDEX
