import json
import re

import anthropic
from pydantic import BaseModel, Field, ValidationError

from shylock_trial.app.dtos.scene_dialogue_dto import DialogueLineKind, SceneDialogueLine

from infrastructure.config import get_settings
from shylock_trial.app.constants.portia_prompt import (
    SCENE_DIALOGUE_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_scene_dialogue_message,
    build_user_message,
)
from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue, get_scene_template
from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialogueContent,
    SceneDialoguePromptDto,
    SceneDialogueResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.app.utils.dialogue_text import (
    sanitize_character_direct_speech,
    sanitize_dialogue_line,
    sanitize_game_text,
)
from shylock_trial.app.utils.portia_text import extract_portia_text

MODEL_ID = "claude-sonnet-4-6"


class PortiaResponseOutput(BaseModel):
    text: str = Field(
        description=(
            "Player-facing Korean prose. For reactions: Portia's direct speech to Shylock only "
            "(no third-person narration like '그녀는 말하였다'). 1–4 sentences."
        ),
    )


class SceneDialogueLineOutput(BaseModel):
    text: str = Field(
        description=(
            "For kind=speech: character's direct words only, no third-person narration "
            "or 'X가 말하였다' wrappers."
        ),
    )
    kind: DialogueLineKind = DialogueLineKind.NARRATION


class SceneDialogueOutput(BaseModel):
    lines: list[SceneDialogueLineOutput] = Field(
        description="Ordered lines with speech/narration kind.",
    )
    challenge_header: str = ""
    challenge_text: str = ""
    choice_texts: dict[str, str] = Field(default_factory=dict)


def _resolve_line_kind(
    parsed_kind: DialogueLineKind,
    template_kind: DialogueLineKind,
) -> DialogueLineKind:
    return parsed_kind if parsed_kind in DialogueLineKind else template_kind


def _build_scene_lines(
    parsed: SceneDialogueOutput,
    template,
) -> tuple[SceneDialogueLine, ...]:
    canonical_kinds = template.canonical_line_kinds
    lines: list[SceneDialogueLine] = []
    for index, line in enumerate(parsed.lines):
        if not line.text.strip():
            continue
        fallback_kind = (
            canonical_kinds[index]
            if index < len(canonical_kinds)
            else DialogueLineKind.NARRATION
        )
        kind = _resolve_line_kind(line.kind, fallback_kind)
        text = sanitize_dialogue_line(line.text)
        if kind == DialogueLineKind.SPEECH:
            text = sanitize_character_direct_speech(text)
        lines.append(
            SceneDialogueLine(
                text=text,
                kind=kind,
            )
        )
    return tuple(lines)


def _strip_json_fence(raw: str) -> str:
    trimmed = raw.strip()
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", trimmed, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else trimmed


class PortiaResponseClient(PortiaResponsePort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        response = await self._client.messages.create(
            model=MODEL_ID,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_user_message(prompt),
                },
            ],
        )

        raw = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        prose = extract_portia_text(raw)
        if prose and not prose.startswith("{"):
            return PortiaResponseResultDto(
                text=self._finalize_portia_text(prose, prompt.request_type)
            )

        try:
            parsed = PortiaResponseOutput.model_validate_json(prose or raw)
            text = parsed.text.strip()
            if text:
                return PortiaResponseResultDto(
                    text=self._finalize_portia_text(text, prompt.request_type)
                )
        except (ValidationError, json.JSONDecodeError):
            pass

        return PortiaResponseResultDto(
            text=self._finalize_portia_text(extract_portia_text(raw), prompt.request_type)
        )

    def _finalize_portia_text(self, text: str, request_type: str) -> str:
        cleaned = sanitize_game_text(text)
        if request_type == "reaction":
            cleaned = sanitize_character_direct_speech(cleaned)
        return cleaned

    async def generate_scene_dialogue(
        self,
        prompt: SceneDialoguePromptDto,
    ) -> SceneDialogueResultDto:
        response = await self._client.messages.create(
            model=MODEL_ID,
            max_tokens=1536,
            system=SCENE_DIALOGUE_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_scene_dialogue_message(prompt),
                },
            ],
        )

        raw = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        payload = _strip_json_fence(raw)

        try:
            parsed = SceneDialogueOutput.model_validate_json(payload)
            template = get_scene_template(prompt.scene_index)
            content = SceneDialogueContent(
                lines=_build_scene_lines(parsed, template),
                challenge_header=parsed.challenge_header or template.challenge_header,
                challenge_text=(
                    sanitize_game_text(parsed.challenge_text)
                    if parsed.challenge_text
                    else None
                ),
                choice_texts={
                    cid: sanitize_game_text(
                        parsed.choice_texts.get(cid, template.canonical_choice_texts[cid])
                    )
                    for cid in template.choice_ids
                }
                if template.choice_ids
                else {},
            )
            if content.lines:
                return SceneDialogueResultDto(content=content)
        except (ValidationError, json.JSONDecodeError, KeyError):
            pass

        return SceneDialogueResultDto(
            content=fallback_scene_dialogue(prompt.scene_index),
            fallback_used=True,
        )
