"""character_relation 그래프 컨텍스트(character_context)가 실제 생성 품질에
얼마나 기여하는지 측정하는 ablation eval — 그래프를 넣은 조건(ON)과 뺀
조건(OFF)으로 프로덕션 어댑터를 그대로 호출해서, 미리 정의한 룰 기반
채점 기준으로 사실관계 오류 발생률을 비교한다.

Claude를 LLM-judge로 쓰지 않는다 — 지금 ANTHROPIC_API_KEY 크레딧이 소진된
상태라(2026-08-12부터, dependencies/duke_verdict_provider.py 참고) 그 경로
자체가 막혀 있고, 설령 있었더라도 생성에 쓴 것과 같은 계열의 로컬 모델을
판정에도 쓰면 self-preference bias가 끼어든다. 대신 이 세 케이스 각각에서
"어떤 문구가 나오면 사실관계가 틀렸다고 볼 수 있는가"를 그래프의 실제
데이터(character_relations 테이블)에 근거해 직접 정의해서 키워드 기반으로
채점한다 — compare_embedding_models.py가 LLM-judge 대신 정답 FTLN 매치
여부로 채점하는 것과 같은 철학.

측정 대상 3가지 (모두 프로덕션 어댑터를 직접 호출):
1. 바사니오 반응 (OllamaPortiaResponseClient.generate, reactor_speaker=BASSANIO)
   — character_context 없이도 "구체적 이유"를 요구받으니, 그래프 없이는
   그 이유를 지어내거나 생략하지 않는지를 본다.
2. 샤일록 선택지 대사 (OllamaPortiaResponseClient.generate_scene_dialogue,
   scene_index=1 portia_opens) — 이번 세션에 실측된 "생사가 걸린 신성한
   약속" 버그의 회귀 테스트. 증서의 생사 이해관계는 안토니오 쪽이지
   샤일록이 아니다.
3. lore_chat (OllamaLoreChatClient.answer) — lore_chat_interactor.py의
   docstring에 이미 문서화된 실패 사례(포샤-안토니오 간 멀티홉 연결을
   그래프 없이는 모델이 스스로 못 이음)의 회귀 테스트 + 그래프가 굳이
   필요 없는 단일홉 질문을 대조군으로 같이 돌려서, 그래프의 효과가
   "전반적 품질 향상"이 아니라 "멀티홉 추론"에 국한된다는 것도 같이 보여준다.

backend/에서 실행 (로컬 Ollama 서버 + DATABASE_URL 모두 필요):
    python -m shylock_trial.evals.character_context_ablation_eval [--repeats 3]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from infrastructure.config import get_settings
from shylock_trial.adapter.outbound.client.ollama_lore_chat_client import OllamaLoreChatClient
from shylock_trial.adapter.outbound.client.ollama_portia_response_client import (
    OllamaPortiaResponseClient,
)
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import SceneDialoguePromptDto
from shylock_trial.app.use_cases.character_relation_interactor import CharacterRelationInteractor
from shylock_trial.app.utils.character_context import build_character_context
from shylock_trial.dependencies.character_relation_provider import (
    get_character_relation_repository,
)
from shylock_trial.domain.entities.trial_entity import TrialPhase

# 대량 반복 호출 동안 httpx/sqlalchemy의 INFO 로그가 결과 출력을 덮지 않도록.
for _noisy_logger in ("httpx", "sqlalchemy.engine"):
    logging.getLogger(_noisy_logger).setLevel(logging.WARNING)


def build_eval_session_factory() -> async_sessionmaker[AsyncSession]:
    """test_tubal_tool_use_ollama.py의 build_eval_session_factory와 동일한
    이유로 NullPool 전용 엔진을 씀 — 이 스크립트도 짧은 세션을 여러 번
    여닫는데, 공유 프로덕션 엔진 풀에는 pool_pre_ping이 없어서 Neon이
    이미 닫은 커넥션을 다시 내주는 문제가 재현된다."""
    engine = create_async_engine(
        get_settings().database_url,
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
    )
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@dataclass
class CaseResult:
    condition: str  # "ON" | "OFF"
    passed: bool
    text: str
    reason: str = ""


@dataclass
class SurfaceReport:
    name: str
    case_label: str
    on_results: list[CaseResult] = field(default_factory=list)
    off_results: list[CaseResult] = field(default_factory=list)

    def on_pass_rate(self) -> str:
        n = len(self.on_results)
        p = sum(r.passed for r in self.on_results)
        return f"{p}/{n}"

    def off_pass_rate(self) -> str:
        n = len(self.off_results)
        p = sum(r.passed for r in self.off_results)
        return f"{p}/{n}"


# --- 1. 바사니오 반응 -------------------------------------------------------

# 판정 기준: "감정적 호소 + 인물 관계에 근거한 구체적 이유" 두 문장을 쓰라는
# 지시(portia_prompt._non_portia_reaction_instruction)를 실제로 지켰는지 —
# 안토니오와의 관계(빚/재산/목숨을 건 보증)를 구체적으로 언급했는가.
# 그래프 없이는 이걸 지어내거나(사실과 다른 디테일) 아예 생략하고 막연한
# 감정 호소로만 채울 가능성이 높다는 게 가설.
# 첫 실행(2026-08-18)에서 "목숨을"이 조사 변형("목숨만큼은", "목숨은" 등)을
# 놓쳐서 오탐(false negative)을 냈던 걸 발견 — 어간만 남긴 substring으로
# 교정 (한국어는 교착어라 조사가 계속 바뀌므로, 특정 조사가 붙은 형태
# 그대로를 키워드로 쓰면 실제로는 grounded된 응답도 놓친다).
_BASSANIO_GROUNDING_KEYWORDS = ("빚", "갚", "재산", "목숨", "보증", "돈을 빌")


def _score_bassanio_reaction(text: str) -> tuple[bool, str]:
    hit = [kw for kw in _BASSANIO_GROUNDING_KEYWORDS if kw in text]
    if hit:
        return True, f"grounded (matched: {hit})"
    return False, "no concrete Antonio-relationship detail found — likely vague or fabricated"


async def run_bassanio_reaction_case(
    portia_client: OllamaPortiaResponseClient,
    characters,
    choice_id: str,
    choice_brief: str,
    repeats: int,
) -> SurfaceReport:
    report = SurfaceReport(name="바사니오 반응", case_label=f"choice={choice_id}")
    graph_context = await build_character_context(characters, "BASSANIO")

    for condition, ctx in (("ON", graph_context), ("OFF", "")):
        for _ in range(repeats):
            prompt = PortiaResponsePromptDto(
                trial_id=uuid4(),
                scene_index=2,
                dp=50,
                phase=TrialPhase.IN_PROGRESS,
                choice_history=(choice_id,),
                context=f"choice:{choice_id}",
                request_type="reaction",
                portia_hp=70,
                choice_id=choice_id,
                choice_label=choice_brief,
                reactor_speaker="BASSANIO",
                reactor_speaker_label="바사니오",
                character_context=ctx,
            )
            result = await portia_client.generate(prompt)
            passed, reason = _score_bassanio_reaction(result.text)
            bucket = report.on_results if condition == "ON" else report.off_results
            bucket.append(CaseResult(condition=condition, passed=passed, text=result.text, reason=reason))
    return report


# --- 2. 샤일록 선택지 대사 (증서 생사 이해관계 회귀 테스트) -------------------

_BOND_CHOICE_IDS = ("bond_signature", "bond_double_standard", "bond_lay_down")
_LIFE_DEATH_PATTERN = re.compile(r"생사|목숨")


def _score_bond_choice_texts(choice_texts: dict[str, str]) -> tuple[bool, str]:
    offenders = [
        cid for cid in _BOND_CHOICE_IDS
        if cid in choice_texts and _LIFE_DEATH_PATTERN.search(choice_texts[cid])
    ]
    if offenders:
        return False, f"life/death framing leaked into: {offenders}"
    return True, "no life/death framing in bond choice_texts"


async def run_shylock_choice_case(
    portia_client: OllamaPortiaResponseClient,
    characters,
    repeats: int,
) -> SurfaceReport:
    report = SurfaceReport(name="샤일록 선택지 대사", case_label="scene_index=1 (portia_opens), bond_* choices")
    graph_context = await build_character_context(characters, "SHYLOCK")

    for condition, ctx in (("ON", graph_context), ("OFF", "")):
        for _ in range(repeats):
            prompt = SceneDialoguePromptDto(
                trial_id=uuid4(),
                scene_index=1,
                dp=50,
                choice_history=(),
                character_context=ctx,
            )
            result = await portia_client.generate_scene_dialogue(prompt)
            choice_texts = result.content.choice_text_map()
            passed, reason = _score_bond_choice_texts(choice_texts)
            joined = " | ".join(f"{cid}: {choice_texts.get(cid, '')}" for cid in _BOND_CHOICE_IDS)
            bucket = report.on_results if condition == "ON" else report.off_results
            bucket.append(CaseResult(condition=condition, passed=passed, text=joined, reason=reason))
    return report


# --- 3. lore_chat ------------------------------------------------------------

_MULTIHOP_QUESTION = "포샤와 안토니오는 무슨 관계인가요?"
_SINGLEHOP_QUESTION = "샤일록과 안토니오는 어떤 사이인가요?"


def _score_multihop_answer(text: str) -> tuple[bool, str]:
    if "바사니오" in text:
        return True, "connects via 바사니오 (correct multi-hop chain)"
    return False, "no mention of the connecting character (바사니오) — likely 'no direct link found'"


def _score_singlehop_answer(text: str) -> tuple[bool, str]:
    keywords = ("원수", "빚", "채권", "적대", "빌려", "담보")
    hit = [kw for kw in keywords if kw in text]
    if hit:
        return True, f"correctly frames the adversarial/creditor relationship (matched: {hit})"
    return False, "missing the adversarial/creditor framing"


async def run_lore_chat_case(
    lore_client: OllamaLoreChatClient,
    characters,
    question: str,
    scorer,
    repeats: int,
) -> SurfaceReport:
    report = SurfaceReport(name="lore_chat", case_label=question)

    for condition in ("ON", "OFF"):
        for _ in range(repeats):
            ctx = await _lore_chat_character_context(characters, question) if condition == "ON" else ""
            answer = await lore_client.answer(question=question, history=(), passages=(), character_context=ctx)
            passed, reason = scorer(answer)
            bucket = report.on_results if condition == "ON" else report.off_results
            bucket.append(CaseResult(condition=condition, passed=passed, text=answer, reason=reason))
    return report


async def _lore_chat_character_context(characters, question: str) -> str:
    """lore_chat_interactor._build_character_context를 이 스크립트 안에서
    재현 — 그 메서드가 인터랙터 바깥에서 재사용하기 쉬운 형태로 뽑혀있지
    않아서, 여기서는 같은 로직(질문에 등장한 캐릭터 이름을 키워드
    매칭 + 2명 이상이면 최단 경로도 추가)을 그대로 다시 구현한다."""
    from itertools import combinations

    from shylock_trial.app.constants.character_relation_prompt import (
        build_character_context_block,
        build_relationship_path_block,
        format_character,
        format_relationship_path,
    )

    nodes = await characters.list_characters()
    lowered = question.lower()
    mentioned = [n for n in nodes if n.name_ko in question or n.name_en.lower() in lowered]
    if not mentioned:
        return ""

    blocks = []
    for node in mentioned:
        relations = await characters.get_relations_for(node.character_id)
        blocks.append(format_character(node, relations))
    context = build_character_context_block(blocks)

    if len(mentioned) >= 2:
        name_by_id = {n.character_id: n.name_ko for n in nodes}
        path_lines = []
        for a, b in combinations(mentioned, 2):
            path = await characters.trace_relationship(a.character_id, b.character_id)
            if not path:
                path = await characters.trace_relationship(b.character_id, a.character_id)
            if path:
                path_lines.append(format_relationship_path(path, name_by_id))
        path_block = build_relationship_path_block(path_lines)
        if path_block:
            context = f"{context}\n\n{path_block}"
    return context


def _print_report(report: SurfaceReport) -> None:
    print(f"\n{'=' * 78}\n{report.name} — {report.case_label}\n{'=' * 78}")
    print(f"  OFF (그래프 없음): {report.off_pass_rate()} pass")
    print(f"  ON  (그래프 있음): {report.on_pass_rate()} pass")
    for condition, results in (("OFF", report.off_results), ("ON", report.on_results)):
        for i, r in enumerate(results, start=1):
            mark = "OK " if r.passed else "FAIL"
            print(f"  [{condition} {i}] {mark} — {r.reason}")
            print(f"      {r.text[:200]}")


async def main(repeats: int, out_path: str) -> None:
    session_factory = build_eval_session_factory()
    portia_client = OllamaPortiaResponseClient()
    lore_client = OllamaLoreChatClient()

    reports: list[SurfaceReport] = []

    # CharacterRelationPgRepository를 직접 하드코딩하는 대신
    # get_character_relation_repository()(dependencies/character_relation_
    # provider.py)를 통해 얻는다 — CHARACTER_RELATION_BACKEND 스위치("pg"
    # 또는 "neo4j")를 이 eval도 그대로 따라가게 하기 위함. 이걸 하드코딩해
    # 두면 .env에서 백엔드를 바꿔도 이 eval만 조용히 예전 백엔드로 계속
    # 도는 버그가 생긴다(2026-08-20에 실제로 이 상태였음).
    print(f"character_relation_backend = {get_settings().character_relation_backend}")
    async with session_factory() as session:
        port = get_character_relation_repository(session=session)
        print(f"실제 게이트웨이: {type(port).__name__}")
        characters = CharacterRelationInteractor(port=port)

        reports.append(
            await run_bassanio_reaction_case(
                portia_client, characters, "gold_refuse_direct",
                "The sum is not the point — I want this bond.", repeats,
            )
        )
        reports.append(
            await run_bassanio_reaction_case(
                portia_client, characters, "scales_no_reason",
                "You ask my reason? There is none — it is simply my will.", repeats,
            )
        )
        reports.append(await run_shylock_choice_case(portia_client, characters, repeats))
        reports.append(
            await run_lore_chat_case(
                lore_client, characters, _MULTIHOP_QUESTION, _score_multihop_answer, repeats,
            )
        )
        reports.append(
            await run_lore_chat_case(
                lore_client, characters, _SINGLEHOP_QUESTION, _score_singlehop_answer, repeats,
            )
        )

    for report in reports:
        _print_report(report)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repeats": repeats,
        "reports": [
            {
                "name": r.name,
                "case_label": r.case_label,
                "on_pass_rate": r.on_pass_rate(),
                "off_pass_rate": r.off_pass_rate(),
                "on_results": [vars(x) for x in r.on_results],
                "off_results": [vars(x) for x in r.off_results],
            }
            for r in reports
        ],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\nSaved raw results to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=str, default="character_context_ablation_results.json")
    args = parser.parse_args()
    asyncio.run(main(args.repeats, args.out))
