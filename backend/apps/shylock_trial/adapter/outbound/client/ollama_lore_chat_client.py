"""Ollama-backed LoreChatLlmPort implementation — same prompt/context-building
as LoreChatClient (Claude), different transport underneath. Never used on its
own in production; always wrapped by FallbackLoreChatClient, since a
home/local Ollama server can't be relied on to always be reachable (see
dependencies/lore_chat_provider.py).

Deliberately raw httpx here, not LangChain, even though LoreChatClient's own
docstring argues LangChain is the right tool for this slice — that reasoning
was about Claude's structured LCEL pipe, not about the local-serving story.
For talking to Ollama specifically, matching ollama_portia_response_client.py's
established shape (same OLLAMA_BASE_URL/OLLAMA_MODEL/CF Access settings —
this is the *same* Ollama server portia_response already calls, just a
different conversation) is more consistent than introducing a second way to
reach the same tunnel through a LangChain Ollama integration.
"""

from __future__ import annotations

import httpx

from infrastructure.config import get_settings
from shylock_trial.app.constants.lore_chat_prompt import (
    LORE_CHAT_SYSTEM_PROMPT,
    build_context_block,
    format_passage,
)
from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort
from shylock_trial.domain.entities.play_line_entity import PlayLine


class OllamaLoreChatClient(LoreChatLlmPort):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self._model = settings.ollama_model
        # Same Cloudflare Access Service Token as portia_response's Ollama
        # client — no-ops (empty dict) in local dev. See
        # ollama_portia_response_client.py for the full reasoning.
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
            timeout=settings.ollama_timeout_seconds,
            headers=access_headers,
        )

    async def answer(
        self,
        question: str,
        history: tuple[LoreChatTurnDto, ...],
        passages: tuple[PlayLine, ...],
        character_context: str = "",
    ) -> str:
        context = build_context_block([format_passage(line) for line in passages])
        messages = [{"role": "system", "content": LORE_CHAT_SYSTEM_PROMPT}]
        messages.extend(
            {"role": "user" if turn.role == "human" else "assistant", "content": turn.content}
            for turn in history
        )
        messages.append(
            {"role": "user", "content": f"{character_context}\n\n{context}\n\n질문: {question}"}
        )

        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": messages,
                "stream": False,
                "think": False,
                # Never unload the model between requests — Ollama's default
                # 5-minute idle timeout means the first request after any gap
                # pays full weight-load time on top of generation (measured:
                # ~19GB model, negligible load_duration once warm vs several
                # seconds cold). Same reasoning applies to
                # ollama_portia_response_client.py's _chat().
                "keep_alive": -1,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
