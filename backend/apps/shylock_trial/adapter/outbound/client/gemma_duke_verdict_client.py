"""Ollama 기반 DukeVerdictPort — 호출 한 번, 모델 하나(DUKE_NARRATOR_MODEL,
기본값 gemma)로, DukeVerdictClient(Claude)가 쓰는 것과 동일한 원샷
judge+narrate 프롬프트 구조를 쓴다. FallbackDukeVerdictClient의
*fallback* 쪽 절반으로 존재하는 것 (dependencies/duke_verdict_provider.py
참고) — *primary*인 2단계 파이프라인(judge/narrate 모델이 분리돼 있고
judge는 think="medium")을 쓰는 OllamaDukeVerdictClient와는 구분됨.

원래는 여기 Claude가 fallback이었다. 실제 장애(2026-08-12:
ANTHROPIC_API_KEY 크레딧 잔액 소진으로 judge() 호출이 전부 400 남)를
겪고 나서 없앴다 — 유료 서드파티 API는 fallback 경로에서 "이건 항상
동작한다"고 안심할 수 있는 대상이 아니라는 게 증명된 셈. 이미
Portia/scene dialogue용으로 로컬에서 돌고 있는 gemma는 이런 실패
모드가 없다. think=False와 (duke_judge_timeout_seconds가 아니라) 짧은
ollama_timeout_seconds를 쓰는 건 의도적임: 이 클래스까지 오게 되는
이유 자체가 primary가 이미 실패했거나 timeout났기 때문이라, fallback
자체는 빨라야 한다 — 여기서 긴 judge timeout을 재사용하면 첫 번째
120초 대기 위에 두 번째 대기를 또 얹는 꼴이 된다."""

import json
import re

import httpx
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

# DukeVerdictInteractor.FALLBACK_LINE / result와 동일하게 맞춤.
VERDICT_FALLBACK_LINE = "법정은 오늘 그 주장을 인정하오."

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


class _DukeVerdictOutput(BaseModel):
    result: DukeVerdictResult
    line: str


def _strip_json_fence(raw: str) -> str:
    match = _FENCE_RE.match(raw.strip())
    return match.group(1).strip() if match else raw.strip()


def _parse_verdict(raw: str) -> DukeVerdictResultDto:
    try:
        parsed = _DukeVerdictOutput.model_validate_json(_strip_json_fence(raw))
        line = parsed.line.strip()
        if line:
            cleaned = sanitize_character_direct_speech(sanitize_game_text(line))
            return DukeVerdictResultDto(result=parsed.result, line=cleaned)
    except (ValidationError, json.JSONDecodeError):
        pass
    # 다른 모든 Ollama adapter의 parse fallback과 같은 이유로, best-effort
    # 대신 엄격하게 처리한다: 잘못된 형식의 로컬 응답은 그냥 못 쓰는 것이지
    # 짜맞춰 쓸 만한 게 아니다 — 그래서 FallbackDukeVerdictClient가
    # fallback_used=True를 보고 최후의 WIN을 내려준다.
    return DukeVerdictResultDto(result="win", line=VERDICT_FALLBACK_LINE, fallback_used=True)


class GemmaDukeVerdictClient(DukeVerdictPort):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self._model = settings.duke_narrator_model
        self._timeout = settings.ollama_timeout_seconds
        # ollama_portia_response_client.py 참고 — 로컬 dev에서는 Cloudflare
        # Access 헤더가 아무 동작 안 하는 것과 같은 이유.
        access_headers = (
            {
                "CF-Access-Client-Id": settings.cf_access_client_id,
                "CF-Access-Client-Secret": settings.cf_access_client_secret,
            }
            if settings.cf_access_client_id and settings.cf_access_client_secret
            else {}
        )
        self._client = http_client or httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            headers=access_headers,
        )

    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto:
        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_message(prompt)},
                ],
                "stream": False,
                "think": False,
                "keep_alive": -1,
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"]
        return _parse_verdict(raw)
