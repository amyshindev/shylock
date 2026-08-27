"""character_relation 그래프의 Neo4j 버전 — CharacterRelationPgRepository와
정확히 같은 CharacterRelationPort를 구현한다. 위쪽 레이어
(CharacterRelationInteractor, 그리고 그걸 쓰는 trial_progression/lore_chat/
tubal_skill 인터랙터들)는 이 파일의 존재 자체를 모른다 — 어느 쪽을 쓸지는
dependencies/character_relation_provider.py의 CHARACTER_RELATION_BACKEND
스위치 하나로 정해진다.

find_path는 PG 버전의 recursive CTE(character_relation_repository.py의
_FIND_PATH_SQL)가 하던 일을 Cypher의 내장 shortestPath()로 대체한다 —
PG 쪽이 이 프로젝트에서 유일하게 raw SQL(text())을 써야 했던 지점이었던
것과 대조적으로, 여기서는 그래프 순회가 질의어 자체의 1급 기능이라 별도
재귀 로직이 없다. PG 버전과 동일하게 방향성 있는 순회만 따라간다
(-[*..max_hops]-> , 양방향이 아님) — 대칭 관계(married_to 등)는 시딩
스크립트가 이미 양방향 row/relationship을 만들어 두므로 이걸로 충분하다.
"""

from neo4j import AsyncDriver

from shylock_trial.adapter.outbound.mappers.character_relation_neo4j_mapper import (
    character_node_from_record,
    character_relation_from_record,
)
from shylock_trial.app.ports.output.character_relation_port import CharacterRelationPort
from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)

_NODE_RETURN = (
    "c.character_id AS character_id, c.name_ko AS name_ko, "
    "c.name_en AS name_en, c.description AS description"
)
_RELATION_RETURN = (
    "startNode(r).character_id AS from_character_id, type(r) AS relation_type, "
    "endNode(r).character_id AS to_character_id, r.description AS description, "
    "r.evidence_ftln_start AS evidence_ftln_start, r.evidence_ftln_end AS evidence_ftln_end"
)


class CharacterRelationNeo4jRepository(CharacterRelationPort):
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def get_node(self, character_id: str) -> CharacterNode | None:
        async with self._driver.session() as session:
            result = await session.run(
                f"MATCH (c:Character {{character_id: $id}}) RETURN {_NODE_RETURN}",
                id=character_id,
            )
            record = await result.single()
            return character_node_from_record(record) if record else None

    async def list_nodes(self) -> list[CharacterNode]:
        async with self._driver.session() as session:
            result = await session.run(f"MATCH (c:Character) RETURN {_NODE_RETURN}")
            return [character_node_from_record(r) async for r in result]

    async def list_relations_for(self, character_id: str) -> list[CharacterRelation]:
        # PG의 list_relations_for(OR from_id/to_id 매치)와 동일 — 방향 무관하게
        # 이 캐릭터를 건드리는 모든 관계. 대칭 관계는 시딩 시 양방향
        # relationship이 이미 존재하므로 무방향 패턴(-[r]-)으로 한 번만
        # 순회해도 두 방향 다 잡힌다.
        async with self._driver.session() as session:
            result = await session.run(
                f"MATCH (c:Character {{character_id: $id}})-[r]-() RETURN {_RELATION_RETURN}",
                id=character_id,
            )
            return [character_relation_from_record(r) async for r in result]

    async def find_path(
        self,
        from_character_id: str,
        to_character_id: str,
        max_hops: int = 4,
    ) -> list[CharacterRelation]:
        if from_character_id == to_character_id:
            return []

        # 가변 길이 관계 패턴의 상한(*..N)은 Cypher에서 파라미터로 못 받고
        # 리터럴이어야 한다 — max_hops가 항상 코드에서 오는 int라 인젝션
        # 위험은 없지만, 방어적으로 int()를 한 번 더 강제한다.
        bound = int(max_hops)
        async with self._driver.session() as session:
            # relationships(path)로 관계 객체를 그대로 돌려받아
            # rel.start_node["character_id"]로 읽으려 했더니 None만 나옴 —
            # 이 결과에는 시작/끝 Node의 속성이 같이 하이드레이션되지 않는
            # 것으로 보임(관계만 RETURN했지 노드 자체를 explicit하게 같이
            # 돌려받은 적이 없어서). UNWIND로 관계를 행 단위로 풀고,
            # list_relations_for와 동일하게 startNode()/endNode()의
            # character_id를 Cypher 안에서 직접 뽑아 RETURN하는 쪽이 안전함.
            result = await session.run(
                f"""
                MATCH path = shortestPath(
                    (a:Character {{character_id: $from_id}})-[*..{bound}]->(b:Character {{character_id: $to_id}})
                )
                UNWIND relationships(path) AS r
                RETURN {_RELATION_RETURN}
                """,
                from_id=from_character_id,
                to_id=to_character_id,
            )
            return [character_relation_from_record(r) async for r in result]
