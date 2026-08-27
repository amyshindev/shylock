"""Ollama 기반 DukeVerdictPort 구현체 — 호출이 하나가 아니라 둘로
분리돼 있다: DUKE_JUDGE_MODEL이 승/패를 정하고, DUKE_NARRATOR_MODEL이
그 판정을 공작(Duke)이 실제로 말하는 한국어 대사로 바꾼다 (duke_prompt.py의
모듈 docstring과 infrastructure/config.py 참고). 프로덕션에서 단독으로는
쓰이지 않고 항상 FallbackDukeVerdictClient로 감싸서 쓴다 — 집/로컬
Ollama 서버는 항상 도달 가능하다고 보장할 수 없기 때문
(dependencies/duke_verdict_provider.py 및, 단일 호출 부분은 이 파일이
그대로 미러링하는 ollama_portia_response_client.py 참고).

두 단계 *중 어느 쪽*에서든 파싱이 실패하면 동일하게 fallback_used=True
판정을 반환한다 — ollama_portia_response_client.py의 _parse_reaction과
같은, best-effort 대신 엄격하게 처리하는 이유다: 쓸 만한 대사가 없는
judge 판정(혹은 그 반대)은 로컬에서 짜맞춰 쓸 만한 게 아니라,
FallbackDukeVerdictClient가 호출 전체를 Claude로 escalate하라는
신호다."""

import json
import logging
import re

import httpx
from pydantic import BaseModel, ValidationError

from infrastructure.config import get_settings
from shylock_trial.app.constants.duke_prompt import (
    JUDGE_SYSTEM_PROMPT,
    NARRATE_SYSTEM_PROMPT,
    build_judge_message,
    build_narrate_message,
)
from shylock_trial.app.dtos.duke_verdict_dto import (
    DukeVerdictPromptDto,
    DukeVerdictResult,
    DukeVerdictResultDto,
)
from shylock_trial.app.ports.output.duke_verdict_port import DukeVerdictPort
from shylock_trial.app.utils.dialogue_text import sanitize_character_direct_speech, sanitize_game_text

logger = logging.getLogger(__name__)

# DukeVerdictInteractor.FALLBACK_LINE / result와 동일 — 모듈 docstring 참고.
VERDICT_FALLBACK_LINE = "법정은 오늘 그 주장을 인정하오."

# judge 호출은 이 프로젝트에서 reasoning을 일부러 켜 두는 유일한
# 지점이다 (다른 곳은 전부 think=False — ~12.5배 지연 비용에 대해서는
# ollama_portia_response_client.py의 모듈 docstring 참고). 이 호출이
# 그냥 flavor text가 아니라 그 라운드의 dp/portia_hp를 결정하기 때문에
# 이 비용을 치를 가치가 있다; narrator 호출은 이미 내려진 결정을
# 말로 옮기는 것뿐이라 Portia의 reaction과 마찬가지로 think=False를
# 유지한다.
_JUDGE_THINK_LEVEL = "medium"

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


class _JudgeOutput(BaseModel):
    result: DukeVerdictResult
    reasoning: str


class _NarrateOutput(BaseModel):
    line: str


def _strip_json_fence(raw: str) -> str:
    match = _FENCE_RE.match(raw.strip())
    return match.group(1).strip() if match else raw.strip()


def _parse_judge(raw: str) -> _JudgeOutput | None:
    try:
        parsed = _JudgeOutput.model_validate_json(_strip_json_fence(raw))
        if parsed.reasoning.strip():
            return parsed
    except (ValidationError, json.JSONDecodeError):
        pass
    return None


def _parse_narration(raw: str) -> str | None:
    try:
        parsed = _NarrateOutput.model_validate_json(_strip_json_fence(raw))
        line = parsed.line.strip()
        if line:
            return sanitize_character_direct_speech(sanitize_game_text(line))
    except (ValidationError, json.JSONDecodeError):
        pass
    return None


class OllamaDukeVerdictClient(DukeVerdictPort):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self._judge_model = settings.duke_judge_model
        self._narrator_model = settings.duke_narrator_model
        self._narrate_timeout = settings.ollama_timeout_seconds
        self._judge_timeout = settings.duke_judge_timeout_seconds
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
        # client 레벨 timeout은 없음 — 호출마다 각자 자기 timeout을 넘긴다
        # (_chat 참고). judge 단계(muse-glimmer, think="medium")는 narrate
        # 단계(gemma, think=False)보다 평소에도 훨씬 오래 걸린다; timeout을
        # 하나로 공유해서 gemma 속도에 맞췄더니 judge 호출은 매번 그걸
        # 초과해서 조용히 Claude로 failover되고 있었다 — infrastructure/config.py의
        # duke_judge_timeout_seconds 주석 참고.
        self._client = http_client or httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            headers=access_headers,
        )

    async def _chat(self, *, model: str, system: str, user: str, think: bool | str, timeout: float) -> str:
        response = await self._client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "think": think,
                # 요청 사이에 어느 모델도 언로드하지 않는다 — Ollama의 기본 5분
                # idle 언로드 때문에 그러지 않으면 다음 요청이 가중치 로드 시간을
                # 통째로 다시 물게 된다는 내용은 ollama_portia_response_client.py의
                # _chat 참고.
                "keep_alive": -1,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto:
        judge_raw = await self._chat(
            model=self._judge_model,
            system=JUDGE_SYSTEM_PROMPT,
            user=build_judge_message(prompt),
            think=_JUDGE_THINK_LEVEL,
            timeout=self._judge_timeout,
        )
        judged = _parse_judge(judge_raw)
        if judged is None:
            return DukeVerdictResultDto(result="win", line=VERDICT_FALLBACK_LINE, fallback_used=True)

        narrate_raw = await self._chat(
            model=self._narrator_model,
            system=NARRATE_SYSTEM_PROMPT,
            user=build_narrate_message(prompt, judged.result, judged.reasoning),
            think=False,
            timeout=self._narrate_timeout,
        )
        line = _parse_narration(narrate_raw)
        if line is None:
            return DukeVerdictResultDto(result="win", line=VERDICT_FALLBACK_LINE, fallback_used=True)

        return DukeVerdictResultDto(result=judged.result, line=line)
