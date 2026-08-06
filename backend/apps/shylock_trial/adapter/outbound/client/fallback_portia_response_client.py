"""Wraps a primary PortiaResponsePort (Ollama) with a fallback (Claude).
Domain code depends on PortiaResponsePort only and never knows this wrapping
exists — see dependencies/portia_response_provider.py for where it's assembled.

Falls back to `fallback` when:
1. `primary` raises anything (connection refused, timeout, HTTP error, an
   unhandled parse exception) — the local server can't be assumed to always
   be up.
2. `primary` returns successfully but with `fallback_used=True` — the local
   model produced something its own adapter couldn't trust (see
   ollama_portia_response_client._parse_reaction). A network failure isn't
   the only way "local" can fail a request.

If `fallback` *also* fails (observed for real during manual verification —
Anthropic returned a billing error), this does not let that exception
propagate either: a broken trial write would be worse for the player than a
generic line. Both tiers failing returns the same last-resort text
PortiaResponseClient itself falls back to, so the behavior a player sees when
everything is down is identical regardless of which provider is configured.
"""

import logging

from shylock_trial.app.constants.scene_catalog import fallback_scene_dialogue
from shylock_trial.app.dtos.portia_response_dto import (
    PortiaResponsePromptDto,
    PortiaResponseResultDto,
)
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialoguePromptDto,
    SceneDialogueResultDto,
)
from shylock_trial.app.ports.output.portia_response_port import PortiaResponsePort

logger = logging.getLogger(__name__)

# Matches PortiaResponseClient.REACTION_FALLBACK_TEXT — a player should see the
# same last-resort line no matter which provider chain produced it.
REACTION_FALLBACK_TEXT = "법정은 그대의 말을 기록에 남기겠소. 다음 절차로 나아가시오."


class FallbackPortiaResponseClient(PortiaResponsePort):
    def __init__(self, primary: PortiaResponsePort, fallback: PortiaResponsePort) -> None:
        self._primary = primary
        self._fallback = fallback

    async def generate(self, prompt: PortiaResponsePromptDto) -> PortiaResponseResultDto:
        try:
            result = await self._primary.generate(prompt)
            if not result.fallback_used:
                return result
            logger.warning(
                "Primary LLM provider returned a fallback-quality result on generate() "
                "(context=%s) — escalating to Claude",
                prompt.context,
            )
        except Exception:
            logger.exception(
                "Primary LLM provider failed on generate() (context=%s) — falling back to Claude",
                prompt.context,
            )

        try:
            return await self._fallback.generate(prompt)
        except Exception:
            logger.critical(
                "Fallback LLM provider ALSO failed on generate() (context=%s) — "
                "both providers down, serving last-resort text",
                prompt.context,
                exc_info=True,
            )
            return PortiaResponseResultDto(text=REACTION_FALLBACK_TEXT, fallback_used=True)

    async def generate_scene_dialogue(
        self,
        prompt: SceneDialoguePromptDto,
    ) -> SceneDialogueResultDto:
        try:
            result = await self._primary.generate_scene_dialogue(prompt)
            if not result.fallback_used:
                return result
            logger.warning(
                "Primary LLM provider returned a fallback-quality result on "
                "generate_scene_dialogue() (scene_index=%s) — escalating to Claude",
                prompt.scene_index,
            )
        except Exception:
            logger.exception(
                "Primary LLM provider failed on generate_scene_dialogue() (scene_index=%s) — "
                "falling back to Claude",
                prompt.scene_index,
            )

        try:
            return await self._fallback.generate_scene_dialogue(prompt)
        except Exception:
            logger.critical(
                "Fallback LLM provider ALSO failed on generate_scene_dialogue() "
                "(scene_index=%s) — both providers down, serving canonical script",
                prompt.scene_index,
                exc_info=True,
            )
            return SceneDialogueResultDto(
                content=fallback_scene_dialogue(prompt.scene_index),
                fallback_used=True,
            )
