import json
from uuid import uuid4

import httpx
import pytest

from shylock_trial.adapter.outbound.client.ollama_portia_response_client import (
    OllamaPortiaResponseClient,
)
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto
from shylock_trial.domain.entities.trial_entity import TrialPhase


def _client_returning(content: str) -> OllamaPortiaResponseClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        body = json.loads(request.content)
        assert body["think"] is False  # thinking mode must stay off — see module docstring
        assert body["stream"] is False
        return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-ollama")
    return OllamaPortiaResponseClient(http_client=http_client)


def _reaction_prompt(**overrides) -> PortiaResponsePromptDto:
    defaults = dict(
        trial_id=uuid4(),
        scene_index=1,
        dp=55,
        phase=TrialPhase.IN_PROGRESS,
        choice_history=("bond_signature",),
        context="choice:bond_signature",
        request_type="reaction",
        portia_hp=80,
        choice_id="bond_signature",
        previous_portia_reactions=(),
    )
    defaults.update(overrides)
    return PortiaResponsePromptDto(**defaults)


@pytest.mark.asyncio
async def test_generate_parses_clean_fenced_json() -> None:
    client = _client_returning('```json\n{"text": "법정은 문서 위에 서 있노라."}\n```')

    result = await client.generate(_reaction_prompt())

    assert result.text == "법정은 문서 위에 서 있노라."
    assert result.fallback_used is False


@pytest.mark.asyncio
async def test_generate_parses_unfenced_json() -> None:
    client = _client_returning('{"text": "법정은 문서 위에 서 있노라."}')

    result = await client.generate(_reaction_prompt())

    assert result.text == "법정은 문서 위에 서 있노라."
    assert result.fallback_used is False


@pytest.mark.asyncio
async def test_generate_treats_malformed_fence_as_fallback_worthy() -> None:
    # Reproduces the real quirk observed manually: a stray token glued right
    # after the ```json fence marker breaks the strict fence regex.
    client = _client_returning('```json certain_path\n{"text": "some text"}\n```')

    result = await client.generate(_reaction_prompt())

    assert result.fallback_used is True
    assert result.text == "법정은 그대의 말을 기록에 남기겠소. 다음 절차로 나아가시오."


@pytest.mark.asyncio
async def test_generate_scene_dialogue_parses_clean_json() -> None:
    payload = json.dumps(
        {
            "lines": [
                {"text": "샤일록, 당신은 안토니오의 살 1파운드를 요구하오.", "kind": "speech"},
                {"text": "법정이 조용해진다.", "kind": "narration"},
            ],
            "challenge_header": "",
            "challenge_text": "자비를 베풀라고?",
            "choice_texts": {},
        },
        ensure_ascii=False,
    )
    client = _client_returning(payload)

    result = await client.generate_scene_dialogue(
        SceneDialoguePromptDto(trial_id=uuid4(), scene_index=1, dp=50, choice_history=())
    )

    assert result.fallback_used is False
    assert len(result.content.lines) == 2
    assert result.content.lines[0].text == "샤일록, 당신은 안토니오의 살 1파운드를 요구하오."


@pytest.mark.asyncio
async def test_generate_scene_dialogue_falls_back_on_malformed_json() -> None:
    client = _client_returning("not json at all")

    result = await client.generate_scene_dialogue(
        SceneDialoguePromptDto(trial_id=uuid4(), scene_index=1, dp=50, choice_history=())
    )

    assert result.fallback_used is True
    assert len(result.content.lines) > 0  # fallback_scene_dialogue still returns canonical lines
