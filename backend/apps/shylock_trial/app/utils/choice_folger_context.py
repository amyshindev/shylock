"""Folger MV RAG context for Portia reaction prompts — cached per choice_id."""

from __future__ import annotations

from shylock_trial.app.constants.curated_evidence import (
    get_curated_evidence_by_id,
    get_curated_evidence_for_choice,
)
from shylock_trial.app.constants.portia_prompt import CHOICE_BRIEFS
from shylock_trial.app.constants.scene_choices import get_choice_evidence_id
from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    ScoredPlayLine,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.domain.entities.evidence_entity import Evidence

# pgvector cosine distance: 0 = identical. Above this → treat as weak / no match.
MAX_RELEVANT_COSINE_DISTANCE = 0.42

RAG_RESULT_LIMIT = 3

# Choices grounded in historical staging, not direct Folger MV dialogue.
HISTORICAL_ONLY_CHOICES: frozenset[str] = frozenset(
    {
        "ghetto_curfew",
        "ghetto_who_guilty",
        "ghetto_look_silent",
    }
)

# Richer English retrieval queries for choices whose brief alone is too thin.
CHOICE_RAG_QUERY_OVERRIDES: dict[str, str] = {
    "coat_show_spit": (
        "Antonio spat upon Shylock's Jewish gaberdine coat; Shylock shows the stain "
        "as proof of past humiliation"
    ),
    "coat_before_dry": (
        "Antonio spat on Shylock's gaberdine; the spit stain is still wet; Shylock "
        "rebukes mercy while the insult is fresh"
    ),
    "coat_show_silent": (
        "Shylock silently displays the gaberdine coat Antonio spat upon"
    ),
    "defend_jessica": "Shylock's daughter Jessica eloped and converted; family wound",
    "letter_irrelevant": (
        "Shylock separates his daughter Jessica's elopement from the bond; a private "
        "family matter has no bearing on the contract before the court"
    ),
    "ring_leah_gift": (
        "It was my turquoise, I had it of Leah when I was a bachelor; I would not have "
        "given it for a wilderness of monkeys — Shylock grieves his dead wife Leah's ring "
        "that Jessica stole and traded for a monkey"
    ),
    "ring_loss_dignity": (
        "Shylock's grief over Leah's stolen turquoise ring; Jessica took it when she fled; "
        "his loss is dignity, not a weakness to be used against him"
    ),
    "ring_clutch_silent": (
        "Shylock silently mourns the turquoise ring of his dead wife Leah, stolen by Jessica"
    ),
    "scales_weigh": "Shylock weighs a pound of flesh on scales in the trial",
    "scales_humour": (
        "Shylock's humour speech: some cannot bear a bagpipe; I cannot master hatred"
    ),
    "blood_impossible": (
        "Portia rules the bond gives no jot of blood; Shylock protests that cutting "
        "a pound of flesh without shedding blood is impossible"
    ),
    "drop_knife": (
        "Shylock lowers the knife he whetted through the trial, unable to execute "
        "the forfeiture without shedding blood"
    ),
    "take_principal_only": (
        "Shylock retreats from the forfeiture: give me my principal, the bare three "
        "thousand ducats, and let me go"
    ),
    "wording_letter_turned": (
        "Shylock demanded the letter of his bond; Portia turns that literalism "
        "against him — the words expressly are a pound of flesh, no jot of blood"
    ),
    "wording_accept_letter": (
        "Shylock yields to the strict letter of the bond he himself invoked; "
        "the exact wording of the contract defeats him"
    ),
    "wording_reread_silent": (
        "Shylock silently rereads the bond's exact words: an equal pound of flesh, "
        "nothing more, nothing less"
    ),
}

# Short Korean gloss for the model — keyed by choice_id.
CHOICE_KOREAN_GLOSS: dict[str, str] = {
    "coat_show_spit": "안토니오가 과거 샤일록의 유대인 외투(개버딘)에 침을 뱉었음을 보여주는 고발",
    "coat_before_dry": "침 자국이 아직 마르지 않았는데 자비를 요구하는 것에 대한 반박",
    "coat_show_silent": "말 없이 외투의 침 자국을 보여주는 제스처",
    "ghetto_curfew": "해가 지면 게토 문으로 돌아가야 하는 베네치아의 유대인 통행 제한",
    "ghetto_who_guilty": "밤마다 갇히는 쪽과 밤마다 조롱하는 쪽 중 누가 가해자인가",
    "ghetto_look_silent": "게토 문을 향해 말 없이 바라보는 제스처",
    "blood_impossible": "피 없이 살을 자르라는 판결은 집행이 불가능하다는 항변",
    "drop_knife": "재판 내내 갈아온 칼을 말 없이 내려놓는 제스처",
    "take_principal_only": "복수를 포기하고 원금만 받겠다는 후퇴",
    "wording_letter_turned": (
        "문자 그대로의 계약을 요구해온 샤일록에게, 그 문자주의가 그대로 되돌아왔다는 항변"
    ),
    "wording_accept_letter": "자신이 세워온 문자의 논리를 인정하며 물러서는 선택",
    "wording_reread_silent": "말없이 계약서의 문구를 다시 들여다보는 제스처",
}

_choice_context_cache: dict[str, str] = {}


def clear_choice_folger_cache() -> None:
    _choice_context_cache.clear()


async def get_choice_folger_context(
    choice_id: str,
    evidence: EvidenceSearchUseCase,
    *,
    choice_label: str | None = None,
) -> str:
    if choice_id in _choice_context_cache:
        return _choice_context_cache[choice_id]

    if choice_id in HISTORICAL_ONLY_CHOICES:
        context = _historical_only_context(choice_id, choice_label)
        _choice_context_cache[choice_id] = context
        return context

    query = await _build_rag_query(choice_id, evidence, choice_label)
    evidence_id = get_choice_evidence_id(choice_id)
    result = await evidence.search_scored(
        EvidenceSearchInputDto(
            query=query,
            evidence_id=evidence_id,
            limit=RAG_RESULT_LIMIT,
        ),
    )
    relevant = [
        scored
        for scored in result.scored_lines
        if scored.cosine_distance <= MAX_RELEVANT_COSINE_DISTANCE
    ]

    if relevant:
        context = _format_folger_passages(choice_id, relevant)
    else:
        curated = await _resolve_curated_evidence(evidence, choice_id, evidence_id)
        if curated is not None and curated.quote.strip():
            context = _format_curated_evidence(choice_id, curated)
        else:
            context = _weak_match_context(choice_id, choice_label)

    _choice_context_cache[choice_id] = context
    return context


async def _build_rag_query(
    choice_id: str,
    evidence: EvidenceSearchUseCase,
    choice_label: str | None,
) -> str:
    parts: list[str] = []
    if choice_label:
        parts.append(choice_label)
    parts.append(CHOICE_RAG_QUERY_OVERRIDES.get(choice_id, CHOICE_BRIEFS.get(choice_id, choice_id)))

    evidence_id = get_choice_evidence_id(choice_id)
    if evidence_id:
        curated = await evidence.get_evidence(evidence_id)
        if curated is not None:
            parts.append(curated.quote)

    return " — ".join(part for part in parts if part)


async def _resolve_curated_evidence(
    evidence: EvidenceSearchUseCase,
    choice_id: str,
    evidence_id: str | None,
) -> Evidence | None:
    if evidence_id:
        found = await evidence.get_evidence(evidence_id)
        if found is not None:
            return found
        return get_curated_evidence_by_id(evidence_id)
    return get_curated_evidence_for_choice(choice_id)


def _format_curated_evidence(choice_id: str, curated: Evidence) -> str:
    gloss = CHOICE_KOREAN_GLOSS.get(choice_id, curated.description)
    lines = [
        "## 원작 맥락 (curated evidence — ground truth for Shylock's move)",
        "포샤는 아래 원작/게임 근거가 실제로 무엇을 의미하는지 정확히 이해한 뒤 반응해야 합니다.",
        f"선택지 한국어 맥락: {gloss}",
        f"1. [{curated.act_scene}] (curated evidence): \"{curated.quote}\"",
    ]
    if curated.description and curated.description not in gloss:
        lines.append(f"   Korean note: {curated.description}")
    lines.extend(_folger_understanding_principles())
    return "\n".join(lines)


def _folger_understanding_principles() -> list[str]:
    return [
        "",
        "원작 이해 원칙:",
        "- 제공된 원작 맥락이 실제로 의미하는 바(누가 누구에게 무엇을 했는지)를 정확히 파악한 뒤 반응하세요.",
        "- 반박의 의미를 곡해하거나 엉뚱하게 받아쳐서는 안 됩니다 "
        "(예: 외투의 침 자국을 단순히 '더러움' 정도로만 이해하면 안 됨).",
        "- 다만 그 사실을 인정하면서 법정·계약·절차로 재해석하거나 무력화하려는 시도는 허용됩니다 "
        "(예: '그렇다 해도 법정의 판단은 다르다').",
        "- 아예 못 알아듣는 것과, 알아듣고 교묘하게 받아치는 것은 다릅니다.",
    ]


def _historical_only_context(choice_id: str, choice_label: str | None) -> str:
    gloss = CHOICE_KOREAN_GLOSS.get(choice_id, "")
    label_line = f"선택지 라벨: {choice_label}\n" if choice_label else ""
    brief = CHOICE_BRIEFS.get(choice_id, choice_id)
    return (
        "## 원작 맥락 (Folger MV RAG)\n"
        f"{label_line}"
        "이 선택지는 원작 《베니스의 상인》 텍스트에 직접 등장하지 않는 역사적 배경 각색입니다 "
        "(베네치아 유대인 게토·통행 제한 등).\n"
        f"선택 의미: {brief}\n"
        f"한국어 맥락: {gloss or '시대적 차별 구조를 드러내는 각색'}\n"
        "원작 구절을 억지로 끼워맞추지 말고, 위 역사적 맥락을 이해한 뒤 법정 반응을 작성하세요."
    )


def _weak_match_context(choice_id: str, choice_label: str | None) -> str:
    label_line = f"선택지 라벨: {choice_label}\n" if choice_label else ""
    brief = CHOICE_BRIEFS.get(choice_id, choice_id)
    gloss = CHOICE_KOREAN_GLOSS.get(choice_id, "")
    gloss_line = f"한국어 맥락: {gloss}\n" if gloss else ""
    return (
        "## 원작 맥락 (Folger MV RAG)\n"
        f"{label_line}"
        "벡터 검색으로 직접 대응하는 원작 구절을 찾지 못했습니다. "
        "원작에 직접적 근거가 없거나 역사적 각색일 수 있습니다.\n"
        f"선택 의미: {brief}\n"
        f"{gloss_line}"
        "관련 없는 원작 인용을 억지로 끼워맞추지 말고, 위 선택 의미만 정확히 이해한 뒤 반응하세요."
    )


def _format_folger_passages(choice_id: str, passages: list[ScoredPlayLine]) -> str:
    gloss = CHOICE_KOREAN_GLOSS.get(choice_id, "")
    lines = [
        "## 원작 맥락 (Folger MV RAG — ground truth for Shylock's move)",
        "포샤는 아래 원작 구절이 실제로 무엇을 의미하는지 정확히 이해한 뒤 반응해야 합니다.",
    ]
    if gloss:
        lines.append(f"선택지 한국어 맥락: {gloss}")

    for index, scored in enumerate(passages, start=1):
        line = scored.play_line
        lines.append(
            f"{index}. [{line.act_scene}] {line.speaker}: \"{line.text}\" "
            f"(distance={scored.cosine_distance:.3f})"
        )

    lines.extend(_folger_understanding_principles())
    return "\n".join(lines)
