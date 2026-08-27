import json
import re

import anthropic
from pydantic import BaseModel, ValidationError

from infrastructure.config import get_settings
from shylock_trial.app.constants.duke_prompt import SYSTEM_PROMPT, build_user_message
from shylock_trial.app.dtos.duke_verdict_dto import (
    DukeVerdictPromptDto,
    DukeVerdictResult,
    DukeVerdictResultDto,
)
from shylock_trial.app.ports.output.duke_verdict_port import DukeVerdictPort
from shylock_trial.app.utils.dialogue_text import sanitize_character_direct_speech, sanitize_game_text

# DukeVerdictInteractor.FALLBACK_LINE과 동일하게 맞춤 — 어떤 provider
# 체인에서 나온 결과든 플레이어는 같은 최후의 대사를 봐야 한다.
VERDICT_FALLBACK_LINE = "법정은 오늘 그 주장을 인정하오."

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


class _DukeVerdictOutput(BaseModel):
    result: DukeVerdictResult
    line: str


def _strip_json_fence(raw: str) -> str:
    match = _FENCE_RE.match(raw.strip())
    return match.group(1).strip() if match else raw.strip()


class DukeVerdictClient(DukeVerdictPort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())
        self._model = settings.claude_model_id

    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(prompt)}],
        )
        raw = "".join(block.text for block in response.content if block.type == "text").strip()

        try:
            parsed = _DukeVerdictOutput.model_validate_json(_strip_json_fence(raw))
            line = parsed.line.strip()
            if line:
                cleaned = sanitize_character_direct_speech(sanitize_game_text(line))
                return DukeVerdictResultDto(result=parsed.result, line=cleaned)
        except (ValidationError, json.JSONDecodeError):
            pass

        return DukeVerdictResultDto(result="win", line=VERDICT_FALLBACK_LINE, fallback_used=True)
