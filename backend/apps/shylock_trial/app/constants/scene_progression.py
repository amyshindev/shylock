"""Scene index constants and narrative progression."""

BASSANIO_PLEA_SCENE_INDEX = 2
CROWD_JEERS_SCENE_INDEX = 3
JESSICA_DUET_SCENE_INDEX = 5
HATH_NOT_SCENE_INDEX = 6
BLOOD_REVEAL_SCENE_INDEX = 7
ALIEN_LAW_SCENE_INDEX = 8
JESSICA_INTERVENTION_SCENE_INDEX = 9

# Longest possible playthrough ends at Jessica intervention (rescued path).
LAST_SCENE_INDEX = JESSICA_INTERVENTION_SCENE_INDEX

# Legacy name kept for callers that mean "last catalogued scene index".
FINAL_SCENE_INDEX = LAST_SCENE_INDEX

# Scenes where request_type=reaction should be voiced by the scene's own
# speaker (SceneTemplate.speaker) instead of the default Portia — deliberately
# an explicit opt-in allowlist, not "any scene whose speaker isn't PORTIA":
# hath_not_moment's speaker is SHYLOCK and jessica_duet/jessica_intervention's
# is JESSICA, but Portia still reacts (or, for the two scripted-climax scenes,
# there's no reaction step at all) — only bassanio_plea/crowd_jeers actually
# want the swap. See trial_progression_interactor._build_portia_prompt.
REACTOR_OVERRIDE_SCENES: frozenset[int] = frozenset({BASSANIO_PLEA_SCENE_INDEX})


def resolve_next_scene_index(scene_index: int, *, portia_hp: int) -> int | None:
    """Return the next scene index, or None when the narrative should end."""
    if scene_index < ALIEN_LAW_SCENE_INDEX:
        return scene_index + 1
    if scene_index == ALIEN_LAW_SCENE_INDEX:
        return JESSICA_INTERVENTION_SCENE_INDEX if portia_hp <= 0 else None
    return None


def is_narrative_complete(scene_index: int, *, portia_hp: int) -> bool:
    """True when the player has finished the final scene for this run."""
    if scene_index == JESSICA_INTERVENTION_SCENE_INDEX:
        return True
    return scene_index == ALIEN_LAW_SCENE_INDEX and portia_hp > 0
