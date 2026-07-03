"""Scene index constants and DP-gated progression after alien_law_reveal."""

from shylock_trial.app.constants.game_balance import DP_JESSICA_EPILOGUE_THRESHOLD

ALIEN_LAW_SCENE_INDEX = 7
JESSICA_DUET_SCENE_INDEX = 8
JESSICA_INTERVENTION_SCENE_INDEX = 9
LAST_SCENE_INDEX = JESSICA_INTERVENTION_SCENE_INDEX

# Legacy name kept for callers that mean "last catalogued scene index".
FINAL_SCENE_INDEX = LAST_SCENE_INDEX


def resolve_next_scene_index(scene_index: int, dp: int) -> int | None:
    """Return the next scene index, or None when the narrative should end."""
    if scene_index < ALIEN_LAW_SCENE_INDEX:
        return scene_index + 1
    if scene_index == ALIEN_LAW_SCENE_INDEX:
        if dp >= DP_JESSICA_EPILOGUE_THRESHOLD:
            return JESSICA_DUET_SCENE_INDEX
        return None
    if scene_index == JESSICA_DUET_SCENE_INDEX:
        return JESSICA_INTERVENTION_SCENE_INDEX
    return None


def is_narrative_complete(scene_index: int, dp: int) -> bool:
    if scene_index == ALIEN_LAW_SCENE_INDEX and dp < DP_JESSICA_EPILOGUE_THRESHOLD:
        return True
    return scene_index == JESSICA_INTERVENTION_SCENE_INDEX
