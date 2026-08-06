"""Ad-hoc script: how reliable is Ollama's function calling for Tubal's
*actual* tool schema (TUBAL_TOOLS / present_rebuttal from tubal_agent_client.py
— imported directly, not reimplemented)?

Tubal's real architecture (see tubal_agent_client.py) already does retrieval
server-side (search_similar_chunks) before any LLM call, and the LLM has
exactly ONE tool to call: present_rebuttal. So "tool selection accuracy" here
isn't "did it pick the right tool among several" — there's only one — it's
"did it pick a good candidate and cite a valid ftln range for it." The one
place genuine multi-step behavior exists at all is recovering from a citation
that doesn't match any real candidate (_handle_present_rebuttal's guard);
MAX_AGENT_ITERATIONS=2 exists *only* for that, per the source comment. This
script tests that recovery path directly rather than hoping the model
stumbles into a real mis-citation on its own.

Reuses TUBAL_TOOLS / the prompt building blocks / TubalAgentClient's own
_handle_present_rebuttal for validation — not reimplemented — and real
server-side search (search_similar_chunks against play_chunks, Cohere
embeddings, same as production) for candidates, so scenarios see the same
inputs the real agent would.

Supports the 4-way ablation from 투발_로컬모델_개선실험.md via --variant:
  baseline    no few-shot, no confidence field (the original failing config —
              this is exactly TUBAL_TOOLS/TUBAL_SYSTEM_PROMPT as imported,
              unmodified)
  fewshot     + few-shot examples (defined in this file only, below)
  confidence  + confidence field (defined in this file only, below)
  both        both improvements together
--variant defaults to running all three NEW variants (baseline numbers are
already on record from the first feasibility test and aren't worth
re-spending Ollama time to reproduce — see the report at the bottom of the
md for why).

The few-shot/confidence additions below are experimental and were tried as a
real (temporary) edit to production tubal_agent_client.py during this
experiment, then reverted once the measurement below came back negative —
see the md's conclusion. They live only here now, not in production, so this
script no longer needs anything beyond TUBAL_TOOLS/TUBAL_SYSTEM_PROMPT/
TubalAgentClient/_format_candidates from the real module.

Thinking mode is off throughout (see try_portia_prompt_with_ollama.py for why).

Run from backend/ (needs DATABASE_URL + COHERE_API_KEY, real Ollama server):
    python -m shylock_trial.evals.test_tubal_tool_use_ollama [--repeats 12] [--variant fewshot]
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import logging
from collections import Counter
from dataclasses import dataclass, field

import httpx

from infrastructure.database import get_session_factory
from shylock_trial.adapter.outbound.client.tubal_agent_client import (
    TUBAL_SYSTEM_PROMPT,
    TUBAL_TOOLS,
    TubalAgentClient,
    _format_candidates,
)
from shylock_trial.adapter.outbound.pg.evidence_search_repository import (
    EvidenceSearchPgRepository,
)
from shylock_trial.app.constants.portia_logical_flaws import PORTIA_LOGICAL_FLAWS
from shylock_trial.app.constants.scene_rag_query_hints import SCENE_RAG_QUERY_HINTS
from shylock_trial.app.dtos.evidence_search_dto import ScoredPlayChunk
from shylock_trial.app.use_cases.evidence_search_interactor import EvidenceSearchInteractor

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:26b-mlx"
SEARCH_LIMIT = 8

VARIANTS = {
    "baseline": {"fewshot": False, "confidence": False},
    "fewshot": {"fewshot": True, "confidence": False},
    "confidence": {"fewshot": False, "confidence": True},
    "both": {"fewshot": True, "confidence": True},
}

# --- Experimental additions (개선안 1/2). Not in production — see module
# docstring. Kept here only so this script can reproduce the measurement. ---

CONFIDENCE_LEVELS = ("low", "medium", "high")
_CONFIDENCE_ORDER = {level: rank for rank, level in enumerate(CONFIDENCE_LEVELS)}
CONFIDENCE_FALLBACK_THRESHOLD = "medium"


def is_confidence_acceptable(confidence: str | None) -> bool:
    if confidence not in _CONFIDENCE_ORDER:
        return False
    return _CONFIDENCE_ORDER[confidence] >= _CONFIDENCE_ORDER[CONFIDENCE_FALLBACK_THRESHOLD]


TUBAL_CONFIDENCE_INSTRUCTIONS = (
    "For every present_rebuttal call, also set confidence to \"high\", \"medium\", "
    "or \"low\" — how sure you are that the passage you picked genuinely exposes "
    "the flaw, not how persuasive your writing is. Honesty here is not penalized: "
    "rating your own pick \"low\" when you're unsure is the correct behavior. Do "
    "not use a high confidence value to compensate for a weak match — if nothing "
    "fits well, the correct move is not calling the tool at all (see Example 2 below)."
)

# Real ftln_start/ftln_end/text below, pulled from an actual
# search_similar_chunks("Hath not a Jew eyes...") query against play_chunks.
# Deliberately uses scenes the scenarios below don't test (hath_not_moment /
# a fabricated dowry claim), so this stays a fair generalization measurement.
TUBAL_FEWSHOT_EXAMPLES = """Two examples of correct behavior:

Example 1 — a candidate genuinely fits, so present_rebuttal IS called:
Scene: hath_not_moment
Portia claims: "샤일록, 당신에게 인간다운 감정이 있기는 한 거요?"
Logical flaw to expose: Portia questions whether Shylock has human feeling, but he already
answered that at length himself, yet the court has systematically denied him the human
dignity she demands he show.
One candidate is Shylock's own earlier speech (ftln_start=3001052, ftln_end=3001072):
"Hath not a Jew eyes? Hath not a Jew hands, organs, dimensions, senses, affections,
passions? ... If you prick us, do we not bleed? If you tickle us, do we not laugh?"
-> Correct response: call present_rebuttal with
{"ftln_start": 3001052, "ftln_end": 3001072,
 "portia_logical_flaw": "Portia questions whether Shylock has human feeling, but he already
  answered that at length himself.",
 "counter_argument": "Shylock already proved his humanity in his own words earlier in the
  play — Portia is demanding he re-answer a question he's already answered.",
 "tubal_comment": "포샤 님, 그 물음엔 이미 답이 나와 있소. 이 사람 스스로 사람임을 증명하지 않았소.",
 "confidence": "high"}

Example 2 — no candidate genuinely fits, so present_rebuttal is NOT called:
Scene: (fabricated) — Portia questions whether Shylock filed the correct dowry paperwork
for Jessica's marriage.
The candidate passages found are about the bond, courtroom procedure, and Jessica's
elopement itself — none of them actually addresses dowry paperwork.
-> Correct response: do NOT call present_rebuttal. Reply in plain text instead, e.g.:
"이 중엔 지참금 서류 얘기를 뒷받침할 대목이 없소. 억지로 갖다 붙이느니 이 건 짚지 않는 게 낫겠소."
"""


def build_system_prompt(*, fewshot: bool, confidence: bool) -> str:
    # Starts from the real, unmodified production prompt and appends the
    # experimental blocks — baseline (both False) is byte-for-byte what
    # production actually sends.
    parts = [TUBAL_SYSTEM_PROMPT]
    if confidence:
        parts.append(TUBAL_CONFIDENCE_INSTRUCTIONS)
    if fewshot:
        parts.append(TUBAL_FEWSHOT_EXAMPLES)
    return "\n\n".join(parts)


def build_tools(*, confidence: bool) -> list[dict]:
    # Starts from the real, unmodified production tool schema (TUBAL_TOOLS)
    # and adds the confidence property only for the variants that test it.
    tools = copy.deepcopy(TUBAL_TOOLS)
    if confidence:
        schema = tools[0]["input_schema"]
        schema["properties"]["confidence"] = {
            "type": "string",
            "enum": list(CONFIDENCE_LEVELS),
            "description": (
                "How confident you are that the passage you picked genuinely "
                "exposes the flaw above — not how well-argued your counter_argument "
                "is. Rate this honestly; \"low\" is not a worse answer than \"high\", "
                "a wrong \"high\" is worse than an honest \"low\"."
            ),
        }
        schema["required"] = [*schema["required"], "confidence"]
    return tools


def to_ollama_tools(tools: list[dict]) -> list[dict]:
    """Anthropic {name, description, input_schema} -> Ollama/OpenAI-style
    {type: function, function: {name, description, parameters}}. Same
    name/description/schema content — just the wrapper shape differs."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


async def ollama_chat(client: httpx.AsyncClient, messages: list[dict], tools: list[dict] | None = None) -> dict:
    payload = {"model": MODEL, "messages": messages, "stream": False, "think": False}
    if tools:
        payload["tools"] = tools
    response = await client.post(OLLAMA_CHAT_URL, json=payload, timeout=60.0)
    response.raise_for_status()
    return response.json()["message"]


@dataclass
class ScenarioResult:
    called_tool: bool
    tool_name: str | None = None
    args: dict | None = None
    missing_required: list[str] = field(default_factory=list)
    valid_ftln: bool | None = None  # None if tool wasn't called
    confidence: str | None = None  # only set when the variant's schema has the field
    text: str = ""

    @property
    def accepted_raw(self) -> bool:
        """Would the backend accept this call, ignoring confidence entirely
        (i.e. the pre-improvement acceptance rule)."""
        return self.called_tool and not self.missing_required and bool(self.valid_ftln)

    @property
    def accepted_gated(self) -> bool:
        """Would a caller that gates on CONFIDENCE_FALLBACK_THRESHOLD actually
        accept this locally, or would it escalate to Claude instead. When the
        variant has no confidence field at all this is identical to
        accepted_raw — there's nothing to gate on."""
        if not self.accepted_raw:
            return False
        if self.confidence is None:
            return True
        return is_confidence_acceptable(self.confidence)


async def run_present_rebuttal_turn(
    http_client: httpx.AsyncClient,
    agent: TubalAgentClient,
    system_prompt: str,
    tools: list[dict],
    required_args: list[str],
    has_confidence: bool,
    scene_id: str,
    portia_claim: str,
    candidates: list[ScoredPlayChunk],
) -> ScenarioResult:
    portia_logical_flaw = PORTIA_LOGICAL_FLAWS.get(scene_id, portia_claim)
    user_content = (
        f"Scene: {scene_id}\n"
        f"Portia claims: {portia_claim}\n"
        f"Logical flaw to expose:\n{portia_logical_flaw}\n\n"
        f"Candidate passages:\n{_format_candidates(candidates)}"
    )
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]

    message = await ollama_chat(http_client, messages, to_ollama_tools(tools))
    tool_calls = message.get("tool_calls") or []

    if not tool_calls:
        return ScenarioResult(called_tool=False, text=message.get("content", ""))

    call = tool_calls[0]
    name = call["function"]["name"]
    args = call["function"]["arguments"]
    if isinstance(args, str):  # some models emit a JSON string instead of an object
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    missing = [f for f in required_args if f not in args or args[f] in (None, "")]
    confidence = str(args.get("confidence")) if has_confidence and args.get("confidence") else None
    valid_ftln = None
    if not missing:
        # _handle_present_rebuttal only looks at ftln_start/ftln_end/tubal_comment —
        # an extra "confidence" key in args (experimental, not production) is
        # harmless to pass through unchanged.
        _, done = await agent._handle_present_rebuttal(args)  # reuse real validation
        valid_ftln = done is not None

    return ScenarioResult(
        called_tool=True, tool_name=name, args=args, missing_required=missing,
        valid_ftln=valid_ftln, confidence=confidence,
    )


async def run_recovery_scenario(
    http_client: httpx.AsyncClient,
    agent: TubalAgentClient,
    system_prompt: str,
    tools: list[dict],
    required_args: list[str],
    has_confidence: bool,
    scene_id: str,
    portia_claim: str,
    candidates: list[ScoredPlayChunk],
) -> bool:
    """Turn 1 is a *synthetic* assistant tool_call citing an ftln range that
    matches none of the real candidates (the only way MAX_AGENT_ITERATIONS>1
    ever actually gets used in production — see module docstring). Turn 2 is
    a real Ollama call given the real error tool_result. Returns whether it
    self-corrected to a valid, (if applicable) confidence-gated citation."""
    portia_logical_flaw = PORTIA_LOGICAL_FLAWS.get(scene_id, portia_claim)
    user_content = (
        f"Scene: {scene_id}\n"
        f"Portia claims: {portia_claim}\n"
        f"Logical flaw to expose:\n{portia_logical_flaw}\n\n"
        f"Candidate passages:\n{_format_candidates(candidates)}"
    )
    bad_args = {
        "ftln_start": 9999001,
        "ftln_end": 9999002,
        "portia_logical_flaw": portia_logical_flaw,
        "counter_argument": "placeholder",
        "tubal_comment": "placeholder",
    }
    if has_confidence:
        bad_args["confidence"] = "high"  # a valid value — only the ftln should be invalid
    error_payload, done = await agent._handle_present_rebuttal(bad_args)
    assert done is None  # confirms this really is an invalid citation

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"id": "call_synthetic_bad_cite", "function": {"name": "present_rebuttal", "arguments": bad_args}}],
        },
        {"role": "tool", "content": json.dumps(error_payload, ensure_ascii=False)},
    ]

    message = await ollama_chat(http_client, messages, to_ollama_tools(tools))
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        return False
    args = tool_calls[0]["function"]["arguments"]
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return False
    missing = [f for f in required_args if f not in args or args[f] in (None, "")]
    if missing:
        return False
    _, done2 = await agent._handle_present_rebuttal(args)
    if done2 is None:
        return False
    if has_confidence:
        return is_confidence_acceptable(str(args.get("confidence")))
    return True


def summarize(label: str, results: list[ScenarioResult], expect_call: bool, has_confidence: bool) -> None:
    n = len(results)
    called = sum(r.called_tool for r in results)
    print(f"\n-- {label} (n={n}) --")
    print(f"called tool: {called}/{n}")
    if expect_call:
        raw = sum(1 for r in results if r.accepted_raw)
        malformed = sum(1 for r in results if r.called_tool and r.missing_required)
        invalid_ftln = sum(1 for r in results if r.called_tool and not r.missing_required and not r.valid_ftln)
        declined = n - called
        print(f"  accepted (raw, ignoring confidence): {raw}/{n}")
        print(f"  called but missing required field(s): {malformed}/{n}")
        print(f"  called with well-formed args but ftln matched no candidate: {invalid_ftln}/{n}")
        print(f"  declined to call (should have called): {declined}/{n}")
    else:
        raw_wrong = sum(1 for r in results if r.accepted_raw)
        print(f"  correctly declined (no tool call at all): {n - called}/{n}")
        print(f"  incorrectly accepted (raw, ignoring confidence): {raw_wrong}/{n}")

    if has_confidence:
        gated = sum(1 for r in results if r.accepted_gated)
        dist = Counter(r.confidence for r in results if r.confidence is not None)
        print(f"  accepted AFTER confidence>={CONFIDENCE_FALLBACK_THRESHOLD} gating: {gated}/{n}")
        print(f"  confidence distribution among calls made: {dict(dist)}")


async def run_variant(
    http_client: httpx.AsyncClient,
    agent: TubalAgentClient,
    evidence_search: EvidenceSearchInteractor,
    variant_name: str,
    repeats: int,
) -> None:
    cfg = VARIANTS[variant_name]
    fewshot, confidence = cfg["fewshot"], cfg["confidence"]
    system_prompt = build_system_prompt(fewshot=fewshot, confidence=confidence)
    tools = build_tools(confidence=confidence)
    required_args = tools[0]["input_schema"]["required"]

    async def search(scene_id: str, portia_claim: str) -> list[ScoredPlayChunk]:
        flaw = PORTIA_LOGICAL_FLAWS.get(scene_id, portia_claim)
        hint = SCENE_RAG_QUERY_HINTS.get(scene_id)
        query = f"{portia_claim}\n{flaw}" + (f"\n{hint}" if hint else "")
        return await evidence_search.search_similar_chunks(query, limit=SEARCH_LIMIT)

    a1_claim = "제시카가 아버지를 버리고 떠났다는 사실 자체가, 당신이 딸에게조차 신뢰받지 못했다는 증거요."
    a2_claim = "이 증서는 피를 언급하지 않으니, 살은 취하되 피는 한 방울도 흘리지 말라는 것이 나의 판결이오."
    b_claim = "포샤는 샤일록에게 베네치아의 세금 신고 절차를 제대로 숙지했는지 캐묻는다."

    a1_candidates = await search("jessica_attack", a1_claim)
    a2_candidates = await search("blood_reveal", a2_claim)
    b_candidates = await search("portia_opens", b_claim)

    print(f"\n{'=' * 70}\nVARIANT: {variant_name} (fewshot={fewshot}, confidence={confidence})\n{'=' * 70}")
    print(f"Candidates found — A1={len(a1_candidates)} A2={len(a2_candidates)} B={len(b_candidates)}")

    a1_results, a2_results, b_results, c_results = [], [], [], []

    for i in range(repeats):
        a1_results.append(
            await run_present_rebuttal_turn(
                http_client, agent, system_prompt, tools, required_args, confidence,
                "jessica_attack", a1_claim, a1_candidates,
            )
        )
        a2_results.append(
            await run_present_rebuttal_turn(
                http_client, agent, system_prompt, tools, required_args, confidence,
                "blood_reveal", a2_claim, a2_candidates,
            )
        )
        b_results.append(
            await run_present_rebuttal_turn(
                http_client, agent, system_prompt, tools, required_args, confidence,
                "portia_opens", b_claim, b_candidates,
            )
        )
        c_results.append(
            await run_recovery_scenario(
                http_client, agent, system_prompt, tools, required_args, confidence,
                "jessica_attack", a1_claim, a1_candidates,
            )
        )
        print(f"  rep {i + 1}/{repeats} done")

    summarize("A1: jessica_attack (should call)", a1_results, expect_call=True, has_confidence=confidence)
    summarize("A2: blood_reveal (should call)", a2_results, expect_call=True, has_confidence=confidence)
    summarize("B: fabricated claim (should NOT call)", b_results, expect_call=False, has_confidence=confidence)

    c_success = sum(c_results)
    print(f"\n-- C: multi-step recovery after invalid citation (n={repeats}) --")
    print(f"  self-corrected to an accepted citation: {c_success}/{repeats}")


async def main(repeats: int, variants: list[str]) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        port = EvidenceSearchPgRepository(session)
        evidence_search = EvidenceSearchInteractor(port=port)
        agent = TubalAgentClient(evidence_search=evidence_search)
        http_client = httpx.AsyncClient()

        for variant_name in variants:
            await run_variant(http_client, agent, evidence_search, variant_name, repeats)

        await http_client.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument(
        "--variant", choices=list(VARIANTS), action="append", dest="variants",
        help="repeatable; defaults to fewshot, confidence, both (baseline already measured separately)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.repeats, args.variants or ["fewshot", "confidence", "both"]))
