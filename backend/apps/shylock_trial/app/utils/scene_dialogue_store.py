import json
from typing import Any

from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)


def _coerce_line_kind(raw: str | None) -> DialogueLineKind:
    if raw == DialogueLineKind.SPEECH.value:
        return DialogueLineKind.SPEECH
    return DialogueLineKind.NARRATION


def _parse_lines(raw_lines: list[Any]) -> tuple[SceneDialogueLine, ...]:
    if not raw_lines:
        return ()

    parsed: list[SceneDialogueLine] = []
    for item in raw_lines:
        if isinstance(item, str):
            parsed.append(SceneDialogueLine(text=item, kind=DialogueLineKind.NARRATION))
            continue
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            parsed.append(
                SceneDialogueLine(
                    text=text,
                    kind=_coerce_line_kind(item.get("kind")),
                )
            )
    return tuple(parsed)


def scene_dialogue_to_dict(content: SceneDialogueContent) -> dict[str, Any]:
    return {
        "lines": [
            {"text": line.text, "kind": line.kind.value}
            for line in content.lines
        ],
        "challenge_header": content.challenge_header,
        "challenge_text": content.challenge_text,
        "choice_texts": dict(content.choice_texts),
    }


def scene_dialogue_from_dict(data: dict[str, Any]) -> SceneDialogueContent:
    return SceneDialogueContent(
        lines=_parse_lines(list(data.get("lines") or [])),
        challenge_header=data.get("challenge_header"),
        challenge_text=data.get("challenge_text"),
        choice_texts=dict(data.get("choice_texts") or {}),
    )


def serialize_scene_dialogues(
    dialogues: dict[int, SceneDialogueContent],
) -> str:
    payload = {str(k): scene_dialogue_to_dict(v) for k, v in dialogues.items()}
    return json.dumps(payload, ensure_ascii=False)


def deserialize_scene_dialogues(raw: str | None) -> dict[int, SceneDialogueContent]:
    if not raw:
        return {}
    data = json.loads(raw)
    return {
        int(key): scene_dialogue_from_dict(value)
        for key, value in data.items()
    }
