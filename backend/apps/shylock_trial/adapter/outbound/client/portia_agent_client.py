"""Portia agent — evaluates whether presented evidence contradicts crowd testimony."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic
from pydantic import BaseModel, Field, ValidationError

from infrastructure.config import get_settings
from shylock_trial.app.constants.press_present_config import PRESS_PRESENT_BY_SCENE_ID
from shylock_trial.app.dtos.portia_agent_dto import PortiaPresentAgentResult
from shylock_trial.app.utils.dialogue_text import sanitize_character_direct_speech, sanitize_game_text

logger = logging.getLogger(__name__)

MODEL_ID = "claude-sonnet-5"
MAX_AGENT_ITERATIONS = 3

PORTIA_AGENT_SYSTEM = """\
You are Portia (Balthazar) presiding over the Venice trial in The Merchant of Venice.
A witness statement was made in court. The defendant presents evidence to contradict it.
Use evaluate_contradiction to judge whether the evidence undermines the statement.
If it clearly contradicts dehumanizing claims with Shylock's humanity speech, call finalize_ruling.
Respond to the player in Korean for portia_response fields.
portia_response must be Portia's direct courtroom speech only — no third-person narration
(e.g. never "라고 그녀는 말하였다" or "바사니오가 … 말한다"; write what the character says).
"""

PORTIA_AGENT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "evaluate_contradiction",
        "description": (
            "Judge whether the presented evidence contradicts or undermines "
            "the witness statement in this trial context."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "statement_text": {"type": "string"},
                "evidence_id": {"type": "string"},
                "evidence_text": {"type": "string"},
            },
            "required": ["statement_text", "evidence_id", "evidence_text"],
        },
    },
    {
        "name": "finalize_ruling",
        "description": (
            "Record the court's reaction after contradiction evaluation. "
            "Only call when evaluate_contradiction returned contradicts=true."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contradiction_valid": {"type": "boolean"},
                "portia_response": {
                    "type": "string",
                    "description": "Portia's Korean reaction in court, 1-3 sentences.",
                },
                "reasoning": {"type": "string"},
            },
            "required": ["contradiction_valid", "portia_response"],
        },
    },
]


class ContradictionEvaluation(BaseModel):
    contradicts: bool
    reasoning: str = Field(default="")


class FinalizeRuling(BaseModel):
    contradiction_valid: bool
    portia_response: str
    reasoning: str = Field(default="")


def _strip_json_fence(raw: str) -> str:
    trimmed = raw.strip()
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", trimmed, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else trimmed


class PortiaAgentClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key_plain())

    async def agentic_loop(
        self,
        scene_id: str,
        statement_id: str,
        statement_text: str,
        evidence_id: str,
        evidence_text: str,
    ) -> PortiaPresentAgentResult:
        config = PRESS_PRESENT_BY_SCENE_ID.get(scene_id)
        if config is None:
            return self._fallback_fail("이 씬에서는 증거 제시 판정을 할 수 없습니다.")

        if (
            statement_id != config.contradiction.statement_id
            or evidence_id != config.contradiction.evidence_id
        ):
            return self._fallback_fail("그 증거로는 이 발언을 반박할 수 없소.")

        approved_contradiction = False
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"Scene: {scene_id}\n"
                    f"Statement ({statement_id}): {statement_text}\n"
                    f"Evidence ({evidence_id}):\n{evidence_text}\n"
                    "Determine if this evidence contradicts the statement."
                ),
            }
        ]

        for _ in range(MAX_AGENT_ITERATIONS):
            response = await self._client.messages.create(
                model=MODEL_ID,
                max_tokens=1024,
                system=PORTIA_AGENT_SYSTEM,
                tools=PORTIA_AGENT_TOOLS,
                messages=messages,
            )

            tool_uses = [block for block in response.content if block.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            if not tool_uses:
                break

            tool_results: list[dict[str, Any]] = []
            for tool_use in tool_uses:
                payload, done = await self._dispatch_tool(
                    tool_name=tool_use.name,
                    tool_input=tool_use.input,
                    statement_text=statement_text,
                    evidence_id=evidence_id,
                    evidence_text=evidence_text,
                    approved_contradiction=approved_contradiction,
                )
                if tool_use.name == "evaluate_contradiction" and payload.get("contradicts"):
                    approved_contradiction = True
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(payload, ensure_ascii=False),
                })
                if done is not None:
                    return done

            messages.append({"role": "user", "content": tool_results})

        if approved_contradiction:
            return PortiaPresentAgentResult(
                contradiction_valid=True,
                portia_response=sanitize_character_direct_speech(
                    "군중의 말은 증거에 맞서 설 수 없소. 법정은 조용해진다."
                ),
            )
        return self._fallback_fail("그 증거로는 군중의 말을 꺾지 못했소.")

    async def _dispatch_tool(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        statement_text: str,
        evidence_id: str,
        evidence_text: str,
        approved_contradiction: bool,
    ) -> tuple[dict[str, Any], PortiaPresentAgentResult | None]:
        if tool_name == "evaluate_contradiction":
            evaluation = await self._run_contradiction_evaluation(
                statement_text=statement_text,
                evidence_id=evidence_id,
                evidence_text=evidence_text,
            )
            return {
                "contradicts": evaluation.contradicts,
                "reasoning": evaluation.reasoning,
            }, None

        if tool_name == "finalize_ruling":
            if not approved_contradiction:
                return {
                    "error": "Call evaluate_contradiction first and receive contradicts=true.",
                }, None
            try:
                ruling = FinalizeRuling.model_validate(tool_input)
            except ValidationError:
                return {"error": "Invalid finalize_ruling payload."}, None

            if ruling.contradiction_valid:
                return {"status": "recorded"}, PortiaPresentAgentResult(
                    contradiction_valid=True,
                    portia_response=sanitize_character_direct_speech(ruling.portia_response),
                    reasoning=ruling.reasoning,
                )
            return {"status": "recorded"}, self._fallback_fail(
                sanitize_character_direct_speech(ruling.portia_response) or "반박이 성립하지 않았소."
            )

        return {"error": f"Unknown tool: {tool_name}"}, None

    async def _run_contradiction_evaluation(
        self,
        statement_text: str,
        evidence_id: str,
        evidence_text: str,
    ) -> ContradictionEvaluation:
        response = await self._client.messages.create(
            model=MODEL_ID,
            max_tokens=512,
            system=(
                "You are a Shakespeare legal scholar assisting Portia's court. "
                "Respond with JSON only."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Witness statement:\n{statement_text}\n\n"
                        f"Evidence ({evidence_id}):\n{evidence_text}\n\n"
                        "Does this evidence contradict the dehumanizing claim "
                        "by asserting Shylock's shared humanity?\n"
                        'Reply with JSON: {"contradicts": true|false, "reasoning": "..."}'
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
            logger.exception("Failed to parse Portia evaluate_contradiction JSON: %s", raw[:200])
            return ContradictionEvaluation(
                contradicts=False,
                reasoning="Could not parse evaluation response.",
            )

    def _fallback_fail(self, message: str) -> PortiaPresentAgentResult:
        return PortiaPresentAgentResult(
            contradiction_valid=False,
            portia_response=sanitize_character_direct_speech(message),
        )
