import pytest

from shylock_trial.app.utils.character_context import build_character_context
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


class FakeCharacterRelationUseCase:
    def __init__(
        self,
        nodes: dict[str, object] | None = None,
        relations_by_character: dict[str, list] | None = None,
    ) -> None:
        self._nodes = nodes or {}
        self._relations_by_character = relations_by_character or {}

    async def get_character(self, character_id: str):
        return self._nodes.get(character_id)

    async def list_characters(self):
        return list(self._nodes.values())

    async def get_relations_for(self, character_id: str):
        return list(self._relations_by_character.get(character_id, []))

    async def trace_relationship(self, from_character_id, to_character_id, max_hops=4):
        return []


@pytest.mark.asyncio
async def test_portia_character_context_withholds_her_own_disguise_secret() -> None:
    # 원래는 trial_progression_interactor.submit_choice(request_type=reaction,
    # reactor=PORTIA) 경로로 이 필터링을 검증했는데, reaction의 기본 화자가
    # 공작으로 바뀌면서(trial_progression_interactor._resolve_reactor 참고)
    # 포샤가 reaction의 reactor가 되는 경우가 더는 없다 — request_type=ending도
    # character_context 자체를 안 채운다(_build_portia_prompt 참고). 그래서
    # 여기서는 오케스트레이션을 거치지 않고 build_character_context를 직접
    # 검증한다 — 이게 실제로 지키려는 불변조건(포샤 자신의 married_to 관계는
    # 절대 그녀 자신의 프롬프트에 노출되면 안 됨)과 더 가깝기도 하다.
    portia_node = CharacterNode(
        character_id="portia",
        name_ko="포샤",
        name_en="Portia",
        description="벨몬트의 부유한 상속녀. 재판에서 발타자르로 변장해 판결을 내린다.",
    )
    secret_marriage = CharacterRelation(
        from_character_id="portia",
        relation_type="married_to",
        to_character_id="bassanio",
        description="포샤가 바사니오에게 반지를 주며 아내가 되기로 서약한다.",
        evidence_ftln_start=3002169,
        evidence_ftln_end=3002175,
    )
    safe_fact = CharacterRelation(
        from_character_id="portia",
        relation_type="presides_over",
        to_character_id="shylock",
        description="포샤가 이 재판을 주재한다.",
        evidence_ftln_start=1,
        evidence_ftln_end=2,
    )
    characters = FakeCharacterRelationUseCase(
        nodes={"portia": portia_node},
        relations_by_character={"portia": [secret_marriage, safe_fact]},
    )

    context = await build_character_context(characters, "PORTIA")

    assert "발타자르로 변장" not in context
    assert "married_to" not in context
    assert "아내가 되기로 서약" not in context
    assert "포샤가 이 재판을 주재한다" in context
