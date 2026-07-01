from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)
from shylock_trial.app.utils.scene_dialogue_store import (
    scene_dialogue_from_dict,
    scene_dialogue_to_dict,
)


def test_scene_dialogue_store_roundtrip() -> None:
    content = SceneDialogueContent(
        lines=(
            SceneDialogueLine(text="포샤가 말한다.", kind=DialogueLineKind.SPEECH),
            SceneDialogueLine(text="법정이 조용해진다.", kind=DialogueLineKind.NARRATION),
        ),
        challenge_text="선택",
        choice_texts={"a": "A"},
    )
    restored = scene_dialogue_from_dict(scene_dialogue_to_dict(content))

    assert restored.lines[0].text == "포샤가 말한다."
    assert restored.lines[0].kind == DialogueLineKind.SPEECH
    assert restored.lines[1].kind == DialogueLineKind.NARRATION


def test_scene_dialogue_store_legacy_string_lines() -> None:
    restored = scene_dialogue_from_dict(
        {"lines": ["legacy line"], "challenge_text": None, "choice_texts": {}}
    )
    assert restored.lines[0].text == "legacy line"
    assert restored.lines[0].kind == DialogueLineKind.NARRATION
