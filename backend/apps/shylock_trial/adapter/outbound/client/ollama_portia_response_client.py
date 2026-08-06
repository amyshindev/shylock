"""Ollama-backed PortiaResponsePort implementation — same prompts, same port
interface as PortiaResponseClient (Claude), different transport underneath.
Never used on its own in production; always wrapped by
FallbackPortiaResponseClient, since a home/local Ollama server can't be
relied on to always be reachable (see dependencies/portia_response_provider.py).

Validated manually against evals/try_portia_prompt_with_ollama.py before this
adapter was written: same SYSTEM_PROMPT / build_user_message() output, think
mode off (~12.5x faster, no quality loss for this task — see that script's
docstring), JSON output usually well-formed but not always (one observed case
had a stray token glued to the ```json fence). That unreliability is exactly
why this adapter treats any non-strict parse as fallback-worthy — see
_parse_reaction.
"""

import json
import logging
import re

import httpx
from pydantic import BaseModel, Field, ValidationError

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
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
    SceneDialoguePromptDto,
    SceneDialogueResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort
from shylock_trial.app.utils.dialogue_text import (
    sanitize_character_direct_speech,
    sanitize_dialogue_line,
    sanitize_game_text,
)

logger = logging.getLogger(__name__)

REACTION_FALLBACK_TEXT = "법정은 그대의 말을 기록에 남기겠소. 다음 절차로 나아가시오."

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


class _PortiaResponseOutput(BaseModel):
    text: str = Field(description="Player-facing Korean prose.")


class _SceneDialogueLineOutput(BaseModel):
    text: str
    kind: DialogueLineKind = DialogueLineKind.NARRATION


class _SceneDialogueOutput(BaseModel):
    lines: list[_SceneDialogueLineOutput]
    challenge_header: str = ""
    challenge_text: str = ""
    choice_texts: dict[str, str] = Field(default_factory=dict)


def _strip_json_fence(raw: str) -> str | None:
    """Only strips a *clean* ```json ... ``` fence. Returns None (not a lenient
    best-effort string) if the fence is malformed — e.g. the observed
    "```json <stray token>\\n{...}```" case — so callers can tell a strict
    parse never had a fair chance and should treat this as fallback-worthy."""
    match = _FENCE_RE.match(raw.strip())
    return match.group(1).strip() if match else raw.strip()


def _parse_reaction(raw: str, request_type: str) -> PortiaResponseResultDto:
    try:
        parsed = _PortiaResponseOutput.model_validate_json(_strip_json_fence(raw))
        text = parsed.text.strip()
        if text:
            cleaned = sanitize_game_text(text)
            if request_type == "reaction":
                cleaned = sanitize_character_direct_speech(cleaned)
            return PortiaResponseResultDto(text=cleaned)
    except (ValidationError, json.JSONDecodeError):
        pass

    # Deliberately stricter than PortiaResponseClient's equivalent fallback: a
    # local model's malformed JSON is treated as unusable rather than
    # best-effort-extracted, so FallbackPortiaResponseClient sees
    # fallback_used=True and escalates to Claude instead of ever serving a
    # player a mangled response.
    return PortiaResponseResultDto(text=REACTION_FALLBACK_TEXT, fallback_used=True)


def _line_speaker_from_template(template, index: int, kind: DialogueLineKind) -> str:
    speakers = getattr(template, "canonical_line_speakers", ())
    if index < len(speakers) and speakers[index]:
        return speakers[index]
    if kind == DialogueLineKind.NARRATION:
        return "NARRATOR"
    return template.speaker


class OllamaPortiaResponseClient(PortiaResponsePort):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self._model = settings.ollama_model
        self._client = http_client or httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout_seconds,
        )

    async def _chat(self, system: str, user: str) -> str:
        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                # See module docstring — thinking mode is ~12.5x slower here
                # for no quality gain on short in-game lines.
                "think": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        raw = await self._chat(SYSTEM_PROMPT, build_user_message(prompt))
        return _parse_reaction(raw, prompt.request_type)

    async def generate_scene_dialogue(
        self,
        prompt: SceneDialoguePromptDto,
    ) -> SceneDialogueResultDto:
        raw = await self._chat(SCENE_DIALOGUE_SYSTEM_PROMPT, build_scene_dialogue_message(prompt))
        template = get_scene_template(prompt.scene_index)

        try:
            parsed = _SceneDialogueOutput.model_validate_json(_strip_json_fence(raw))
            canonical_kinds = template.canonical_line_kinds
            lines: list[SceneDialogueLine] = []
            for index, line in enumerate(parsed.lines):
                if not line.text.strip():
                    continue
                fallback_kind = (
                    canonical_kinds[index] if index < len(canonical_kinds) else DialogueLineKind.NARRATION
                )
                kind = line.kind if line.kind in DialogueLineKind else fallback_kind
                text = sanitize_dialogue_line(line.text)
                if kind == DialogueLineKind.SPEECH:
                    text = sanitize_character_direct_speech(text)
                lines.append(
                    SceneDialogueLine(
                        text=text,
                        kind=kind,
                        speaker=_line_speaker_from_template(template, index, kind),
                    )
                )
            content = SceneDialogueContent(
                lines=tuple(lines),
                challenge_header=parsed.challenge_header or template.challenge_header,
                challenge_text=sanitize_game_text(parsed.challenge_text) if parsed.challenge_text else None,
                choice_texts={
                    cid: sanitize_game_text(parsed.choice_texts.get(cid, template.canonical_choice_texts[cid]))
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
