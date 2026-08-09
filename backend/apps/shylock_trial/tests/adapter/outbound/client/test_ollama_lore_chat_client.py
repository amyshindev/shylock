import json

import httpx
import pytest

from shylock_trial.adapter.outbound.client.ollama_lore_chat_client import OllamaLoreChatClient
from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.domain.entities.play_line_entity import PlayLine


def _client_returning(content: str, capture: dict | None = None) -> OllamaLoreChatClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        body = json.loads(request.content)
        assert body["think"] is False
        assert body["stream"] is False
        if capture is not None:
            capture["body"] = body
        return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-ollama")
    return OllamaLoreChatClient(http_client=http_client)


@pytest.mark.asyncio
async def test_answer_returns_stripped_content() -> None:
    client = _client_returning("  베니스는 상업 도시국가였습니다.  ")

    result = await client.answer("베니스는 어떤 도시였나요?", (), ())

    assert result == "베니스는 상업 도시국가였습니다."


@pytest.mark.asyncio
async def test_answer_includes_system_prompt_history_and_context() -> None:
    capture: dict = {}
    client = _client_returning("답변입니다.", capture)
    history = (
        LoreChatTurnDto(role="human", content="샤일록은 누구인가요?"),
        LoreChatTurnDto(role="ai", content="베니스의 유대인 대금업자입니다."),
    )
    passages = (PlayLine(ftln=1003120, speaker="Antonio", text="You call me misbeliever.", act_scene="1.3"),)

    await client.answer("안토니오와의 관계는요?", history, passages)

    messages = capture["body"]["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "샤일록은 누구인가요?"}
    assert messages[2] == {"role": "assistant", "content": "베니스의 유대인 대금업자입니다."}
    assert messages[-1]["role"] == "user"
    assert "FTLN 1003120" in messages[-1]["content"]
    assert "안토니오와의 관계는요?" in messages[-1]["content"]


@pytest.mark.asyncio
async def test_answer_includes_character_context_when_provided() -> None:
    capture: dict = {}
    client = _client_returning("답변입니다.", capture)

    await client.answer(
        "샤일록은 누구인가요?",
        (),
        (),
        character_context="인물 관계 정보:\n[샤일록 (Shylock)] 베니스의 유대인 대금업자.",
    )

    assert "인물 관계 정보" in capture["body"]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_answer_raises_on_server_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "model not loaded"})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test-ollama")
    client = OllamaLoreChatClient(http_client=http_client)

    with pytest.raises(httpx.HTTPStatusError):
        await client.answer("질문", (), ())
