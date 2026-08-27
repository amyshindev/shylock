import json
from uuid import uuid4

import httpx
import pytest

from infrastructure.config import get_settings
from shylock_trial.adapter.outbound.client.ollama_duke_verdict_client import (
    OllamaDukeVerdictClient,
)
from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto


def _client_with_responses(responses: list[str]) -> tuple[OllamaDukeVerdictClient, list[dict]]:
    """(client, calls)를 반환 — calls는 클라이언트가 요청을 보내는 순서대로
    채워지므로, 테스트가 클라이언트 자체의 속성까지 들어가지 않고도
    스테이지별 model/think를 assert할 수 있다."""
    calls: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        body = json.loads(request.content)
        assert body["stream"] is False
        calls.append(body)
        content = responses[len(calls) - 1]
        return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-ollama")
    return OllamaDukeVerdictClient(http_client=http_client), calls


def _verdict_prompt(**overrides) -> DukeVerdictPromptDto:
    defaults = dict(
        trial_id=uuid4(),
        scene_index=1,
        choice_id="bond_signature",
        choice_brief="Both my signature and Antonio's are on this bond.",
        stimulus="logical",
        dp=55,
        portia_hp=80,
        round_number=1,
    )
    defaults.update(overrides)
    return DukeVerdictPromptDto(**defaults)


@pytest.mark.asyncio
async def test_judge_combines_judge_and_narrator_calls() -> None:
    settings = get_settings()
    client, calls = _client_with_responses(
        [
            json.dumps({"result": "win", "reasoning": "clears the bar"}),
            json.dumps({"line": "이의 없음 — 법정이 인정하오."}),
        ]
    )

    result = await client.judge(_verdict_prompt())

    assert result.result == "win"
    assert result.line == "이의 없음 — 법정이 인정하오."
    assert result.fallback_used is False

    assert len(calls) == 2
    # Judge 스테이지: DUKE_JUDGE_MODEL, reasoning 켜짐 — see
    # ollama_duke_verdict_client.py's _JUDGE_THINK_LEVEL.
    assert calls[0]["model"] == settings.duke_judge_model
    assert calls[0]["think"] == "medium"
    # Narrator 스테이지: DUKE_NARRATOR_MODEL, reasoning 꺼짐 (포샤 응답과 동일).
    assert calls[1]["model"] == settings.duke_narrator_model
    assert calls[1]["think"] is False
    # Narrator 프롬프트는 judge 본인의 결정 + reasoning에 근거하며, 자유롭게
    # 재결정하지 않는다.
    narrate_user_message = calls[1]["messages"][1]["content"]
    assert "WIN" in narrate_user_message
    assert "clears the bar" in narrate_user_message


@pytest.mark.asyncio
async def test_judge_falls_back_when_judge_stage_is_malformed() -> None:
    client, calls = _client_with_responses(["not json at all"])

    result = await client.judge(_verdict_prompt())

    assert result.fallback_used is True
    assert result.result == "win"
    # Narrator 스테이지는 아예 실행되지 않는다 — 진짜 판결 없이는 서술할 게 없다.
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_judge_falls_back_when_narrator_stage_is_malformed() -> None:
    client, calls = _client_with_responses(
        [
            json.dumps({"result": "lose", "reasoning": "tone read as contempt of court"}),
            "not json at all",
        ]
    )

    result = await client.judge(_verdict_prompt())

    # judge 스테이지는 성공했고(LOSE로 판정했음에도), narration 스테이지가
    # 고장 나면 대사를 지어내거나 judge의 실제 판결을 조용히 버리는 대신
    # 호출 전체를 fallback으로 escalate한다 — 모듈 docstring 참고.
    assert result.fallback_used is True
    assert result.result == "win"
    assert len(calls) == 2
