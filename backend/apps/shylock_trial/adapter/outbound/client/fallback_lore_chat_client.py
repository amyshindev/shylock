"""Wraps a primary LoreChatLlmPort (Ollama) with a fallback (Claude).
Domain code depends on LoreChatLlmPort only and never knows this wrapping
exists — see dependencies/lore_chat_provider.py for where it's assembled.
Mirrors FallbackPortiaResponseClient's shape.

Simpler than FallbackPortiaResponseClient: LoreChatLlmPort.answer() returns a
plain str, not a DTO with a fallback_used quality flag, so there's no
"succeeded but low-quality" escalation path to check — only exceptions
trigger the fallback.
"""

import logging

from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.app.ports.output.lore_chat_llm_port import LoreChatLlmPort
from shylock_trial.domain.entities.play_line_entity import PlayLine

logger = logging.getLogger(__name__)

LAST_RESORT_TEXT = "답변을 준비하지 못했어요. 잠시 후 다시 시도해 주세요."


class FallbackLoreChatClient(LoreChatLlmPort):
    def __init__(self, primary: LoreChatLlmPort, fallback: LoreChatLlmPort) -> None:
        self._primary = primary
        self._fallback = fallback

    async def answer(
        self,
        question: str,
        history: tuple[LoreChatTurnDto, ...],
        passages: tuple[PlayLine, ...],
    ) -> str:
        try:
            return await self._primary.answer(question, history, passages)
        except Exception:
            logger.exception(
                "Primary lore chat provider failed — falling back to Claude (question=%r)",
                question,
            )

        try:
            return await self._fallback.answer(question, history, passages)
        except Exception:
            logger.critical(
                "Fallback lore chat provider ALSO failed — both providers down, "
                "serving last-resort text (question=%r)",
                question,
                exc_info=True,
            )
            return LAST_RESORT_TEXT
