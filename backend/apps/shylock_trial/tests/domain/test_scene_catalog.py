import pytest

from shylock_trial.app.constants.scene_catalog import (
    SCENE_TEMPLATES,
    fallback_scene_dialogue,
    get_scene_template,
    is_fixed_script_scene,
)
from shylock_trial.app.constants.scene_progression import JESSICA_DUET_SCENE_INDEX


@pytest.mark.parametrize("scene_index", range(len(SCENE_TEMPLATES)))
def test_scene_template_line_kind_counts_match(scene_index: int) -> None:
    template = get_scene_template(scene_index)
    assert len(template.canonical_lines) == len(template.canonical_line_kinds), (
        f"{template.scene_id}: lines={len(template.canonical_lines)}, "
        f"kinds={len(template.canonical_line_kinds)}"
    )
    if template.canonical_line_speakers:
        assert len(template.canonical_line_speakers) == len(template.canonical_lines), (
            f"{template.scene_id}: lines={len(template.canonical_lines)}, "
            f"speakers={len(template.canonical_line_speakers)}"
        )


def test_jessica_duet_fallback_dialogue_builds() -> None:
    content = fallback_scene_dialogue(JESSICA_DUET_SCENE_INDEX)
    assert len(content.lines) == 16


def test_jessica_duet_is_fixed_script_scene() -> None:
    assert is_fixed_script_scene(JESSICA_DUET_SCENE_INDEX)
