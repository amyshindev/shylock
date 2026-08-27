"""character_relation_mapper.py의 Neo4j 버전 — ORM row 대신 neo4j 드라이버가
돌려주는 Record 객체를 같은 도메인 엔티티(CharacterNode/CharacterRelation)로
변환한다. 노드/관계 속성 이름을 도메인 엔티티 필드 이름과 그대로 맞춰뒀기
때문에(seed_character_relation_neo4j.py 참고) 여기는 그냥 옮겨 담기만 한다.

관계는 항상 Cypher RETURN 절에서 startNode()/endNode()의 character_id를
직접 뽑아 받는다 — relationships(path)로 Relationship 객체 자체를 돌려받아
rel.start_node["character_id"]로 읽으려던 첫 시도는 노드 속성이 하이드레이션
안 돼서 None만 나왔다(character_relation_repository.py의 find_path 주석
참고). 그래서 Relationship 객체를 직접 다루는 매퍼는 없다 — 모든 조회가
_RELATION_RETURN 하나의 형태로 통일됨."""

from shylock_trial.domain.entities.character_relation_entity import (
    CharacterNode,
    CharacterRelation,
)


def character_node_from_record(record) -> CharacterNode:
    return CharacterNode(
        character_id=record["character_id"],
        name_ko=record["name_ko"],
        name_en=record["name_en"],
        description=record["description"],
    )


def character_relation_from_record(record) -> CharacterRelation:
    return CharacterRelation(
        from_character_id=record["from_character_id"],
        relation_type=record["relation_type"],
        to_character_id=record["to_character_id"],
        description=record["description"],
        evidence_ftln_start=record["evidence_ftln_start"],
        evidence_ftln_end=record["evidence_ftln_end"],
    )
