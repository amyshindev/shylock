import pytest

from shylock_trial.adapter.outbound.client.fallback_lore_chat_client import (
    LAST_RESORT_TEXT,
    FallbackLoreChatClient,
)
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort


class FakeLoreChatLlmPort(LoreChatLlmPort):
    def __init__(self, *, result: str | None = None, raises: Exception | None = None) -> None:
        self._result = result
        self._raises = raises
        self.answer_calls = 0

    async def answer(self, question, history, passages) -> str:
        self.answer_calls += 1
        if self._raises is not None:
            raise self._raises
        return self._result


@pytest.mark.asyncio
async def test_answer_uses_primary_when_it_succeeds() -> None:
    primary = FakeLoreChatLlmPort(result="from primary")
    fallback = FakeLoreChatLlmPort(result="from fallback")
    client = FallbackLoreChatClient(primary=primary, fallback=fallback)

    result = await client.answer("질문", (), ())

    assert result == "from primary"
    assert fallback.answer_calls == 0


@pytest.mark.asyncio
async def test_answer_falls_back_when_primary_raises() -> None:
    primary = FakeLoreChatLlmPort(raises=TimeoutError("ollama unreachable"))
    fallback = FakeLoreChatLlmPort(result="from fallback")
    client = FallbackLoreChatClient(primary=primary, fallback=fallback)

    result = await client.answer("질문", (), ())

    assert result == "from fallback"
    assert primary.answer_calls == 1
    assert fallback.answer_calls == 1


@pytest.mark.asyncio
async def test_answer_returns_last_resort_text_when_both_providers_fail() -> None:
    primary = FakeLoreChatLlmPort(raises=ConnectionError("ollama unreachable"))
    fallback = FakeLoreChatLlmPort(raises=RuntimeError("anthropic billing error"))
    client = FallbackLoreChatClient(primary=primary, fallback=fallback)

    result = await client.answer("질문", (), ())

    assert result == LAST_RESORT_TEXT
    assert primary.answer_calls == 1
    assert fallback.answer_calls == 1
