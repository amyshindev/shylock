"""Tubal skill agent — server-side embedding search over paraphrased play
chunks (see seed_play_chunks.py), then a single Claude call that picks and
judges the best candidate.

The search query is built directly from portia_claim/portia_logical_flaw —
no LLM round-trip to invent a search phrase — and searches each chunk's
modern-English paraphrase embedding, not the archaic original, so a
modern-English query actually lands close to the right passage.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from infrastructure.config import get_settings
from shylock_trial.app.constants.portia_logical_flaws import (
    PORTIA_LOGICAL_FLAWS,
    TUBAL_SEARCH_FAILURE_COMMENT,
)
from shylock_trial.app.constants.scene_rag_query_hints import SCENE_RAG_QUERY_HINTS
from shylock_trial.app.constants.tubal_prompt import (
    TUBAL_CHARACTER,
    TUBAL_KOREAN_SPEECH_STYLE,
    sanitize_tubal_comment,
)
from shylock_trial.app.dtos.evidence_search_dto import ScoredPlayChunk
from shylock_trial.app.dtos.tubal_agent_dto import TubalAgentResult
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.utils.dialogue_text import (
    sanitize_character_direct_speech,
    sanitize_game_text,
)
from shylock_trial.domain.entities.play_chunk_entity import PlayChunk

logger = logging.getLogger(__name__)

MODEL_ID = "claude-sonnet-5"
SEARCH_LIMIT = 8
# A clean run finishes in 1 turn (present_rebuttal). The extra headroom here
# only covers the model citing an ftln range that doesn't match any of the
# candidates shown — there's no query-retry loop, since re-running the same
# server-side search would return the same candidates.
MAX_AGENT_ITERATIONS = 2

TUBAL_TOOLS: list[dict[str, Any]] = [
    {
        "name": "present_rebuttal",
        "description": (
            "Pick the candidate passage above that best exposes Portia's "
            "logical flaw and add it to the court record. The backend "
            "verifies the FTLN range matches one of the candidates before "
            "accepting it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ftln_start": {
                    "type": "integer",
                    "description": "ftln_start of the candidate passage you chose.",
                },
                "ftln_end": {
                    "type": "integer",
                    "description": "ftln_end of the candidate passage you chose.",
                },
                "portia_logical_flaw": {
                    "type": "string",
                    "description": "Which part of Portia's argument this passage exposes as wrong.",
                },
                "counter_argument": {
                    "type": "string",
                    "description": "The rebuttal logic Shylock should present in court using this passage.",
                },
                "tubal_comment": {
                    "type": "string",
                    "description": (
                        "One Korean sentence in Venice court speech (~소/~하오/~이오) "
                        "stating the counter-argument strategy — not a mere quote. "
                        "Tubal speaks as Shylock's friend, never as a servant (no 주인/상전)."
                    ),
                },
            },
            "required": ["ftln_start", "ftln_end", "portia_logical_flaw", "counter_argument", "tubal_comment"],
        },
    },
]

TUBAL_SYSTEM_PROMPT = f"""You are Tubal (투발), Shylock's friend and fellow Jewish merchant in Venice.
You are here to help your friend defend himself in court — not as his servant.

{TUBAL_CHARACTER}

You will be given a claim Portia made in court, the logical flaw in it, and a
list of candidate passages found by searching the play. Pick the one
candidate that best exposes that flaw — a real moment from the play that
undercuts Portia's argument — and call present_rebuttal with it.

{TUBAL_KOREAN_SPEECH_STYLE}

If none of the candidates genuinely expose the flaw, don't force a weak
match — say so in plain text instead of calling the tool."""


def _format_candidates(chunks: list[ScoredPlayChunk]) -> str:
    if not chunks:
        return "(no candidates found)"
    return "\n\n".join(
        f"--- Candidate (ftln_start={c.chunk.ftln_start}, ftln_end={c.chunk.ftln_end}, "
        f"{c.chunk.speaker}, {c.chunk.act_scene}) ---\n"
        f"Modern paraphrase: {c.chunk.paraphrase}\n"
        f"Original: {c.chunk.text}"
        for c in chunks
    )


class TubalAgentClient:
    def __init__(self, evidence_search: EvidenceSearchUseCase) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())
        self._evidence_search = evidence_search

    async def agentic_loop(
        self,
        portia_claim: str,
        scene_id: str,
    ) -> TubalAgentResult:
        portia_logical_flaw = PORTIA_LOGICAL_FLAWS.get(scene_id, portia_claim)

        # The hint is search-only — it never reaches the LLM prompt below, only
        # the embedding query. portia_logical_flaw stays exactly as authored so
        # the "flaw to expose" instruction the model sees is unaffected.
        search_query = f"{portia_claim}\n{portia_logical_flaw}"
        hint = SCENE_RAG_QUERY_HINTS.get(scene_id)
        if hint:
            search_query = f"{search_query}\n{hint}"
        candidates = await self._evidence_search.search_similar_chunks(search_query, limit=SEARCH_LIMIT)

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"Scene: {scene_id}\n"
                    f"Portia claims: {portia_claim}\n"
                    f"Logical flaw to expose:\n{portia_logical_flaw}\n\n"
                    f"Candidate passages:\n{_format_candidates(candidates)}"
                ),
            }
        ]

        # No cache_control here — the system prompt is short now that the full
        # play text is gone, almost certainly under Sonnet 5's 1024-token
        # cacheable-prefix minimum, so a breakpoint would just be dead weight.
        for _ in range(MAX_AGENT_ITERATIONS):
            response = await self._client.messages.create(
                model=MODEL_ID,
                max_tokens=2048,
                system=TUBAL_SYSTEM_PROMPT,
                tools=TUBAL_TOOLS,
                messages=messages,
            )

            logger.info(
                "Tubal LLM call usage: input=%s cache_write=%s cache_read=%s output=%s",
                response.usage.input_tokens,
                response.usage.cache_creation_input_tokens,
                response.usage.cache_read_input_tokens,
                response.usage.output_tokens,
            )
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            if not tool_uses:
                logger.warning("Tubal agent ended without tool_use (stop_reason=%s)", response.stop_reason)
                break

            tool_results: list[dict[str, Any]] = []
            for tool_use in tool_uses:
                result_payload, done = await self._dispatch_tool(
                    tool_name=tool_use.name,
                    tool_input=tool_use.input,
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result_payload, ensure_ascii=False),
                })
                if done is not None:
                    return done

            messages.append({"role": "user", "content": tool_results})

        return TubalAgentResult(
            success=False,
            tubal_comment=TUBAL_SEARCH_FAILURE_COMMENT,
        )

    async def _dispatch_tool(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> tuple[dict[str, Any], TubalAgentResult | None]:
        if tool_name == "present_rebuttal":
            return await self._handle_present_rebuttal(tool_input)

        return {"error": f"Unknown tool: {tool_name}"}, None

    async def _handle_present_rebuttal(
        self,
        tool_input: dict[str, Any],
    ) -> tuple[dict[str, Any], TubalAgentResult | None]:
        ftln_start = int(tool_input.get("ftln_start", 0))
        ftln_end = int(tool_input.get("ftln_end", 0))
        tubal_comment = str(tool_input.get("tubal_comment", "")).strip()

        if not ftln_start or not ftln_end:
            return {"error": "ftln_start and ftln_end are required"}, None
        if not tubal_comment:
            return {"error": "tubal_comment is required"}, None

        # Only accept an (ftln_start, ftln_end) pair that exactly matches one
        # of the candidates actually shown — this is the guard against the
        # model citing a range it misremembered rather than one it was given.
        chunk: PlayChunk | None = await self._evidence_search.get_chunk(ftln_start, ftln_end)
        if chunk is None:
            return {
                "error": (
                    f"No candidate with ftln_start={ftln_start}, ftln_end={ftln_end}. "
                    "Use the exact ftln_start/ftln_end shown for one of the candidates above."
                ),
            }, None

        return {
            "status": "added",
            "ftln_start": chunk.ftln_start,
            "ftln_end": chunk.ftln_end,
        }, TubalAgentResult(
            success=True,
            ftln=chunk.ftln_start,
            passage=chunk.text,
            speaker=chunk.speaker,
            act_scene=chunk.act_scene,
            tubal_comment=sanitize_character_direct_speech(
                sanitize_game_text(sanitize_tubal_comment(tubal_comment))
            ),
        )
