"""Folger MV RAG context for Portia reaction prompts — cached per choice_id."""

from __future__ import annotations

from shylock_trial.app.constants.portia_prompt import CHOICE_BRIEFS
from shylock_trial.app.constants.scene_choices import get_choice_evidence_id
from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    ScoredPlayLine,
)
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase

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
    "hath_not_speech": (
        "Hath not a Jew eyes? If you prick us do we not bleed? Shylock's humanity speech"
    ),
    "defend_jessica": "Shylock's daughter Jessica eloped and converted; family wound",
    "scales_weigh": "Shylock weighs a pound of flesh on scales in the trial",
    "scales_humour": (
        "Shylock's humour speech: some cannot bear a bagpipe; I cannot master hatred"
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
    result = await evidence.search_scored(
        EvidenceSearchInputDto(query=query, limit=RAG_RESULT_LIMIT),
    )
    relevant = [
        scored
        for scored in result.scored_lines
        if scored.cosine_distance <= MAX_RELEVANT_COSINE_DISTANCE
    ]

    if not relevant:
        context = _weak_match_context(choice_id, choice_label)
    else:
        context = _format_folger_passages(choice_id, relevant)

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

    lines.extend(
        [
            "",
            "원작 이해 원칙:",
            "- 제공된 원작 맥락이 실제로 의미하는 바(누가 누구에게 무엇을 했는지)를 정확히 파악한 뒤 반응하세요.",
            "- 반박의 의미를 곡해하거나 엉뚱하게 받아쳐서는 안 됩니다 "
            "(예: 외투의 침 자국을 단순히 '더러움' 정도로만 이해하면 안 됨).",
            "- 다만 그 사실을 인정하면서 법정·계약·절차로 재해석하거나 무력화하려는 시도는 허용됩니다 "
            "(예: '그렇다 해도 법정의 판단은 다르다').",
            "- 아예 못 알아듣는 것과, 알아듣고 교묘하게 받아치는 것은 다릅니다.",
        ]
    )
    return "\n".join(lines)
