"""Wraps a primary DukeVerdictPort with a fallback — which provider plays
each role is decided by the caller (see dependencies/duke_verdict_provider.py;
currently primary=OllamaDukeVerdictClient (muse-glimmer), fallback=
GemmaDukeVerdictClient, not Claude — Claude was dropped after a real outage
made the "always available" assumption behind using it as a fallback false).
Mirrors fallback_portia_response_client.py's escalation reasoning (primary
exception OR fallback_used=True both escalate; if the fallback also fails,
serve the same last-resort verdict regardless of which provider chain
produced it)."""

import logging

from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto, DukeVerdictResultDto
from shylock_trial.app.ports.output.duke_verdict_port import DukeVerdictPort

logger = logging.getLogger(__name__)

VERDICT_FALLBACK_LINE = "법정은 오늘 그 주장을 인정하오."


class FallbackDukeVerdictClient(DukeVerdictPort):
    def __init__(self, primary: DukeVerdictPort, fallback: DukeVerdictPort) -> None:
        self._primary = primary
        self._fallback = fallback

    async def judge(self, prompt: DukeVerdictPromptDto) -> DukeVerdictResultDto:
        try:
            result = await self._primary.judge(prompt)
            if not result.fallback_used:
                return result
            logger.warning(
                "Primary LLM provider returned a fallback-quality verdict "
                "(choice_id=%s) — escalating to the fallback provider",
                prompt.choice_id,
            )
        except Exception:
            logger.exception(
                "Primary LLM provider failed on judge() (choice_id=%s) — "
                "escalating to the fallback provider",
                prompt.choice_id,
            )

        try:
            return await self._fallback.judge(prompt)
        except Exception:
            logger.critical(
                "Fallback LLM provider ALSO failed on judge() (choice_id=%s) — "
                "both providers down, defaulting to WIN",
                prompt.choice_id,
                exc_info=True,
            )
            return DukeVerdictResultDto(result="win", line=VERDICT_FALLBACK_LINE, fallback_used=True)
