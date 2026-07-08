import asyncio

import pytest

from shylock_trial.app.dtos.evidence_search_dto import (
    EvidenceSearchInputDto,
    EvidenceSearchResultDto,
    EvidenceSearchScoredResultDto,
    ScoredPlayLine,
)
from shylock_trial.app.utils.choice_folger_context import (
    clear_choice_folger_cache,
    get_choice_folger_context,
)
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine


class FakeEvidenceUseCase:
    def __init__(
        self,
        *,
        scored_lines: tuple[ScoredPlayLine, ...] = (),
        evidence_by_id: dict[str, Evidence] | None = None,
    ) -> None:
        self.scored_lines = scored_lines
        self.evidence_by_id = evidence_by_id or {}
        self.search_calls = 0

    async def search(self, input_dto: EvidenceSearchInputDto) -> EvidenceSearchResultDto:
        return EvidenceSearchResultDto(
            play_lines=tuple(item.play_line for item in self.scored_lines[: input_dto.limit]),
        )

    async def search_scored(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> EvidenceSearchScoredResultDto:
        self.search_calls += 1
        return EvidenceSearchScoredResultDto(
            scored_lines=tuple(self.scored_lines[: input_dto.limit]),
        )

    async def list_curated_evidence(self) -> list[Evidence]:
        return list(self.evidence_by_id.values())

    async def get_evidence(self, evidence_id: str) -> Evidence | None:
        return self.evidence_by_id.get(evidence_id)


GABERDINE_EVIDENCE = Evidence(
    evidence_id="gaberdine",
    quote="You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
    act_scene="1.3",
    icon="gaberdine",
    description="안토니오가 '개'라 부르며 침을 뱉었던 외투.",
    source_ftln_range=(100, 120),
)

GABERDINE_LINE = PlayLine(
    ftln=1003120,
    speaker="ANTONIO",
    text="You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
    act_scene="1.3",
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_choice_folger_cache()


def test_coat_choice_includes_folger_passage() -> None:
    evidence = FakeEvidenceUseCase(
        scored_lines=(ScoredPlayLine(play_line=GABERDINE_LINE, cosine_distance=0.18),),
        evidence_by_id={"gaberdine": GABERDINE_EVIDENCE},
    )

    context = asyncio.run(
        get_choice_folger_context(
            "coat_show_spit",
            evidence,
            choice_label="보시오. 당신들이 뱉은 것이, 아직도 이 옷에 남아 있소",
        )
    )

    assert "spit upon my Jewish gaberdine" in context
    assert "안토니오가 과거" in context
    assert "곡해하거나 엉뚱하게" in context
    assert evidence.search_calls == 1


def test_coat_choice_uses_cache_on_second_call() -> None:
    evidence = FakeEvidenceUseCase(
        scored_lines=(ScoredPlayLine(play_line=GABERDINE_LINE, cosine_distance=0.18),),
        evidence_by_id={"gaberdine": GABERDINE_EVIDENCE},
    )

    asyncio.run(get_choice_folger_context("coat_show_spit", evidence))
    asyncio.run(get_choice_folger_context("coat_show_spit", evidence))

    assert evidence.search_calls == 1


def test_ghetto_choice_skips_vector_search() -> None:
    evidence = FakeEvidenceUseCase()

    context = asyncio.run(get_choice_folger_context("ghetto_curfew", evidence))

    assert "역사적 배경 각색" in context
    assert "억지로 끼워맞추지" in context
    assert evidence.search_calls == 0


def test_weak_match_falls_back_to_curated_not_unrelated_passage() -> None:
    evidence = FakeEvidenceUseCase(
        scored_lines=(ScoredPlayLine(play_line=GABERDINE_LINE, cosine_distance=0.91),),
    )

    context = asyncio.run(get_choice_folger_context("bond_signature", evidence))

    assert "curated evidence" in context
    assert "pound of your fair flesh" in context
    assert "spit upon my Jewish gaberdine" not in context


def test_weak_match_without_curated_evidence_reports_no_passage() -> None:
    evidence = FakeEvidenceUseCase(
        scored_lines=(ScoredPlayLine(play_line=GABERDINE_LINE, cosine_distance=0.91),),
    )

    context = asyncio.run(get_choice_folger_context("bow_accept", evidence))

    assert "직접 대응하는 원작 구절을 찾지 못했습니다" in context
    assert "spit upon my Jewish gaberdine" not in context


def test_coat_choice_falls_back_to_curated_when_search_empty() -> None:
    evidence = FakeEvidenceUseCase(
        scored_lines=(),
        evidence_by_id={"gaberdine": GABERDINE_EVIDENCE},
    )

    context = asyncio.run(get_choice_folger_context("coat_show_spit", evidence))

    assert "spit upon my Jewish gaberdine" in context
    assert "curated evidence" in context
