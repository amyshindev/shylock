"""Tubal skill agent — Claude tool_use loop over Folger corpus search."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic
from pydantic import BaseModel, Field, ValidationError

from infrastructure.config import get_settings
from shylock_trial.app.constants.portia_logical_flaws import (
    PORTIA_LOGICAL_FLAWS,
    TUBAL_SEARCH_FAILURE_COMMENT,
)
from shylock_trial.app.constants.tubal_prompt import (
    TUBAL_CHARACTER,
    TUBAL_KOREAN_SPEECH_STYLE,
    sanitize_tubal_comment,
)
from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.dtos.tubal_agent_dto import TubalAgentResult
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.utils.dialogue_text import (
    sanitize_character_direct_speech,
    sanitize_game_text,
)
from shylock_trial.domain.entities.play_line_entity import PlayLine

logger = logging.getLogger(__name__)

MODEL_ID = "claude-sonnet-5"
MAX_AGENT_ITERATIONS = 5

TUBAL_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_folger",
        "description": (
            "Search the Folger Shakespeare corpus for passages "
            "related to the given claim or topic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms capturing the claim in 3–5 words.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of passages to return.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "evaluate_contradiction",
        "description": (
            "Evaluate whether a given passage from the play "
            "contradicts or undermines a legal claim made by Portia, "
            "and articulate the logical flaw and counter-argument."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "passage": {
                    "type": "string",
                    "description": "Full text of one search_folger result.",
                },
                "ftln": {
                    "type": "integer",
                    "description": "Folger throughline number for the passage.",
                },
                "portia_claim": {
                    "type": "string",
                    "description": "Summary of Portia's claim to rebut.",
                },
                "portia_logical_flaw": {
                    "type": "string",
                    "description": (
                        "Which part of Portia's argument is logically wrong "
                        "in light of this passage."
                    ),
                },
                "counter_argument": {
                    "type": "string",
                    "description": (
                        "The rebuttal logic Shylock should present in court "
                        "using this passage."
                    ),
                },
            },
            "required": [
                "passage",
                "ftln",
                "portia_claim",
                "portia_logical_flaw",
                "counter_argument",
            ],
        },
    },
    {
        "name": "add_to_court_record",
        "description": (
            "Add the selected passage to the court record "
            "as new evidence presented by Tubal."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ftln": {"type": "integer"},
                "passage": {"type": "string"},
                "speaker": {"type": "string"},
                "act_scene": {"type": "string"},
                "tubal_comment": {
                    "type": "string",
                    "description": (
                        "One Korean sentence in Venice court speech (~소/~하오/~이오) "
                        "stating the counter-argument strategy — not a mere quote. "
                        "Tubal speaks as Shylock's friend, never as a servant (no 주인/상전)."
                    ),
                },
            },
            "required": ["ftln", "passage", "speaker", "act_scene", "tubal_comment"],
        },
    },
]


class ContradictionEvaluation(BaseModel):
    contradicts: bool
    reasoning: str = Field(default="")
    portia_logical_flaw: str = Field(default="")
    counter_argument: str = Field(default="")


def build_tubal_system_prompt(scene_id: str, portia_claim: str) -> str:
    flaw = PORTIA_LOGICAL_FLAWS.get(scene_id, portia_claim)
    return f"""You are Tubal (투발), Shylock's friend and fellow Jewish merchant in Venice.
You are here to help your friend defend himself in court — not as his servant.

{TUBAL_CHARACTER}

Your task is to find evidence in the Folger Shakespeare corpus
that exposes the following flaw in Portia's legal argument:

{flaw}

{TUBAL_KOREAN_SPEECH_STYLE}

Use tools in order: search_folger → evaluate_contradiction → add_to_court_record.
In evaluate_contradiction, explicitly identify how the found passage
exposes this logical flaw. Fill portia_logical_flaw with which part of Portia's
argument is logically wrong, and counter_argument with the rebuttal Shylock should make.
In add_to_court_record, tubal_comment must be one Korean sentence in the court speech
style above — a counter-argument strategy, not a mere quotation of the passage.
Only add a passage that evaluate_contradiction marked as contradicts=true.
Stop after add_to_court_record succeeds."""


def _strip_json_fence(raw: str) -> str:
    trimmed = raw.strip()
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", trimmed, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else trimmed


def _play_lines_to_json(play_lines: tuple[PlayLine, ...]) -> str:
    payload = [
        {
            "ftln": line.ftln,
            "speaker": line.speaker,
            "text": line.text,
            "act_scene": line.act_scene,
        }
        for line in play_lines
    ]
    return json.dumps(payload, ensure_ascii=False)


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
        system_prompt = build_tubal_system_prompt(scene_id, portia_claim)
        approved_ftlns: set[int] = set()
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"Scene: {scene_id}\n"
                    f"Portia claims: {portia_claim}\n"
                    f"Logical flaw to expose:\n{portia_logical_flaw}\n"
                    "Find evidence that exposes this flaw."
                ),
            }
        ]

        for _ in range(MAX_AGENT_ITERATIONS):
            response = await self._client.messages.create(
                model=MODEL_ID,
                max_tokens=1024,
                system=system_prompt,
                tools=TUBAL_TOOLS,
                messages=messages,
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
                    portia_claim=portia_claim,
                    portia_logical_flaw=portia_logical_flaw,
                    approved_ftlns=approved_ftlns,
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
        portia_claim: str,
        portia_logical_flaw: str,
        approved_ftlns: set[int],
    ) -> tuple[dict[str, Any], TubalAgentResult | None]:
        if tool_name == "search_folger":
            return await self._handle_search_folger(tool_input), None

        if tool_name == "evaluate_contradiction":
            return await self._handle_evaluate_contradiction(
                tool_input,
                portia_claim,
                portia_logical_flaw,
                approved_ftlns,
            ), None

        if tool_name == "add_to_court_record":
            return self._handle_add_to_court_record(tool_input, approved_ftlns)

        return {"error": f"Unknown tool: {tool_name}"}, None

    async def _handle_search_folger(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        query = str(tool_input.get("query", "")).strip()
        limit = int(tool_input.get("limit", 5))
        if not query:
            return {"error": "query is required", "passages": []}

        result = await self._evidence_search.search(
            EvidenceSearchInputDto(query=query, limit=limit)
        )
        return {
            "passages": json.loads(_play_lines_to_json(result.play_lines)),
            "count": len(result.play_lines),
        }

    async def _handle_evaluate_contradiction(
        self,
        tool_input: dict[str, Any],
        portia_claim: str,
        portia_logical_flaw: str,
        approved_ftlns: set[int],
    ) -> dict[str, Any]:
        passage = str(tool_input.get("passage", "")).strip()
        ftln = int(tool_input.get("ftln", 0))
        claim = str(tool_input.get("portia_claim", portia_claim)).strip() or portia_claim
        agent_flaw = str(tool_input.get("portia_logical_flaw", "")).strip()
        agent_counter = str(tool_input.get("counter_argument", "")).strip()

        if not passage or not ftln:
            return {"error": "passage and ftln are required"}
        if not agent_flaw or not agent_counter:
            return {"error": "portia_logical_flaw and counter_argument are required"}

        evaluation = await self._run_contradiction_evaluation(
            passage=passage,
            ftln=ftln,
            portia_claim=claim,
            portia_logical_flaw=portia_logical_flaw,
            agent_logical_flaw=agent_flaw,
            agent_counter_argument=agent_counter,
        )
        if evaluation.contradicts:
            approved_ftlns.add(ftln)

        return {
            "contradicts": evaluation.contradicts,
            "reasoning": evaluation.reasoning,
            "portia_logical_flaw": evaluation.portia_logical_flaw or agent_flaw,
            "counter_argument": evaluation.counter_argument or agent_counter,
            "ftln": ftln,
        }

    async def _run_contradiction_evaluation(
        self,
        passage: str,
        ftln: int,
        portia_claim: str,
        portia_logical_flaw: str,
        agent_logical_flaw: str,
        agent_counter_argument: str,
    ) -> ContradictionEvaluation:
        response = await self._client.messages.create(
            model=MODEL_ID,
            max_tokens=768,
            system=(
                "You are a Shakespeare legal scholar assisting Tubal in court. "
                "Respond with JSON only."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Portia's claim:\n{portia_claim}\n\n"
                        f"Target logical flaw:\n{portia_logical_flaw}\n\n"
                        f"Passage (ftln {ftln}):\n{passage}\n\n"
                        f"Agent's identified flaw:\n{agent_logical_flaw}\n\n"
                        f"Agent's counter-argument:\n{agent_counter_argument}\n\n"
                        "Does this passage expose the logical flaw and support the counter-argument?\n"
                        "Reply with JSON:\n"
                        '{"contradicts": true|false, "reasoning": "...", '
                        '"portia_logical_flaw": "...", "counter_argument": "..."}'
                    ),
                }
            ],
        )

        raw = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        payload = _strip_json_fence(raw)

        try:
            return ContradictionEvaluation.model_validate_json(payload)
        except (ValidationError, json.JSONDecodeError):
            logger.exception("Failed to parse evaluate_contradiction JSON: %s", raw[:200])
            return ContradictionEvaluation(
                contradicts=False,
                reasoning="Could not parse evaluation response.",
                portia_logical_flaw=agent_logical_flaw,
                counter_argument=agent_counter_argument,
            )

    def _handle_add_to_court_record(
        self,
        tool_input: dict[str, Any],
        approved_ftlns: set[int],
    ) -> tuple[dict[str, Any], TubalAgentResult | None]:
        ftln = int(tool_input.get("ftln", 0))
        passage = str(tool_input.get("passage", "")).strip()
        speaker = str(tool_input.get("speaker", "")).strip()
        act_scene = str(tool_input.get("act_scene", "")).strip()
        tubal_comment = str(tool_input.get("tubal_comment", "")).strip()

        if ftln not in approved_ftlns:
            return {
                "error": (
                    "You must call evaluate_contradiction for this passage first "
                    "and receive contradicts=true before adding to the court record."
                ),
            }, None

        if not all([ftln, passage, speaker, act_scene, tubal_comment]):
            return {"error": "ftln, passage, speaker, act_scene, tubal_comment are required"}, None

        return {
            "status": "added",
            "ftln": ftln,
        }, TubalAgentResult(
            success=True,
            ftln=ftln,
            passage=passage,
            speaker=speaker,
            act_scene=act_scene,
            tubal_comment=sanitize_character_direct_speech(
                sanitize_game_text(sanitize_tubal_comment(tubal_comment))
            ),
        )
