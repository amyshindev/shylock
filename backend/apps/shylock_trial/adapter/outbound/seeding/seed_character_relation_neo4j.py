"""character_relation 그래프를 Neo4j에 시딩한다 — 데이터 자체는
alembic/versions/031_add_character_relation_graph.py(노드 7개 + 엣지 15개)와
032_add_antonio_bassanio_friendship.py(안토니오↔바사니오 friend_of 양방향
엣지 2개 추가 — 031에는 대출 관계(guarantor_for/financed_by)만 있고 우정
자체가 관계 row로는 없었음)를 합쳐서 옮긴 것이다. 프로덕션 Postgres
character_relations 테이블의 실제 행 수(17개)와 대조 확인함(2026-08-20).
두 소스가 갈라지지 않도록 나중에 그래프 데이터를 바꾸면(새 alembic
migration 추가) 이 파일도 같이 고칠 것. Postgres 버전과 달리 스키마
마이그레이션이 필요 없다 — Neo4j는 스키마리스(schemaless)라 노드/관계를
바로 만들면 됨.

MERGE를 써서 멱등적(idempotent)으로 만들었다 — 여러 번 실행해도 중복
노드/관계가 생기지 않는다.

관계 타입은 Cypher 관례(UPPER_SNAKE)를 일부러 따르지 않고 소문자
그대로(married_to, creditor_of, ...) 유지했다 — 이 문자열이
`_PORTIA_HIDDEN_RELATION_TYPES`(portia_prompt.py) 등 프로젝트 전역에서
소문자로 비교되고 있어서, 대문자로 바꾸면 그 필터들이 조용히 깨진다.

실행 (Neo4j 서버가 떠 있어야 함, backend/에서):
    python -m shylock_trial.adapter.outbound.seeding.seed_character_relation_neo4j
"""

from __future__ import annotations

import asyncio

from infrastructure.neo4j_driver import close_neo4j_driver, get_neo4j_driver

_NODES: list[dict[str, str]] = [
    {
        "character_id": "shylock",
        "name_ko": "샤일록",
        "name_en": "Shylock",
        "description": "베니스의 유대인 대금업자. 안토니오에게 살 1파운드를 담보로 돈을 빌려준다.",
    },
    {
        "character_id": "antonio",
        "name_ko": "안토니오",
        "name_en": "Antonio",
        "description": "베니스의 상인. 바사니오를 위해 샤일록에게 돈을 빌리고 목숨을 담보로 건다.",
    },
    {
        "character_id": "bassanio",
        "name_ko": "바사니오",
        "name_en": "Bassanio",
        "description": "안토니오의 친구. 포샤에게 구혼하기 위해 안토니오의 돈이 필요하다.",
    },
    {
        "character_id": "portia",
        "name_ko": "포샤",
        "name_en": "Portia",
        "description": "벨몬트의 부유한 상속녀. 재판에서 발타자르로 변장해 판결을 내린다.",
    },
    {
        "character_id": "jessica",
        "name_ko": "제시카",
        "name_en": "Jessica",
        "description": "샤일록의 딸. 로렌조와 함께 아버지의 재산을 갖고 도망친다.",
    },
    {
        "character_id": "lorenzo",
        "name_ko": "로렌조",
        "name_en": "Lorenzo",
        "description": "제시카의 연인이자 남편. 그녀와 함께 베니스를 떠나 벨몬트로 간다.",
    },
    {
        "character_id": "tubal",
        "name_ko": "투발",
        "name_en": "Tubal",
        "description": "샤일록의 동료 유대인. 제시카의 행방과 안토니오의 소식을 전한다.",
    },
]

# (from, relation_type, to, description, ftln_start, ftln_end)
_EDGES: list[tuple[str, str, str, str, int, int]] = [
    ("portia", "married_to", "bassanio", "포샤가 바사니오에게 반지를 주며 아내가 되기로 서약한다.", 3002169, 3002175),
    ("bassanio", "married_to", "portia", "바사니오가 포샤의 반지 서약을 받아들인다.", 3002169, 3002175),
    ("antonio", "guarantor_for", "bassanio", "안토니오가 자신의 재산과 목숨을 바사니오를 위해 내놓는다.", 1001145, 1001146),
    ("bassanio", "financed_by", "antonio", "바사니오가 안토니오에게 갚아야 할 빚이 있음을 인정한다.", 1001138, 1001141),
    ("antonio", "debtor_of", "shylock", "안토니오가 살 1파운드를 담보로 샤일록에게 돈을 빌린다.", 1003158, 1003165),
    ("shylock", "creditor_of", "antonio", "샤일록이 안토니오에게 살 1파운드를 담보로 돈을 빌려준다.", 1003158, 1003165),
    ("antonio", "discriminated_against", "shylock", "안토니오가 샤일록을 '개'라 부르며 침을 뱉었다.", 1003120, 1003140),
    ("shylock", "enemy_of", "antonio", "샤일록이 자신을 모욕한 안토니오를 원수로 여긴다.", 1003120, 1003140),
    ("antonio", "enemy_of", "shylock", "안토니오가 샤일록을 모욕할 만큼 적대한다.", 1003120, 1003140),
    ("tubal", "friend_of", "shylock", "투발이 샤일록을 위해 달아난 제시카를 직접 찾아다닌다.", 3001079, 3001082),
    ("shylock", "friend_of", "tubal", "샤일록이 투발에게 제시카의 행방을 묻고 소식을 의지한다.", 3001079, 3001082),
    ("shylock", "father_of", "jessica", "샤일록이 제시카를 '내 살과 피'라 부른다.", 3001034, 3001037),
    ("jessica", "daughter_of", "shylock", "제시카가 샤일록의 딸이다.", 3001034, 3001037),
    ("lorenzo", "married_to", "jessica", "로렌조가 벨몬트에서 제시카와 함께 밤을 노래한다.", 5001066, 5001067),
    ("jessica", "married_to", "lorenzo", "제시카가 로렌조와 함께 벨몬트에 정착해 있다.", 5001066, 5001067),
    # 032_add_antonio_bassanio_friendship.py — 031에는 안토니오-바사니오 사이에
    # 대출 관계(guarantor_for/financed_by)만 있고 우정 자체는 관계 row로
    # 없었음(바사니오 노드 설명 안에 산문으로만 존재).
    ("antonio", "friend_of", "bassanio", "안토니오가 처형을 앞두고 바사니오를 '벗'이라 부르며 그를 위해 기꺼이 목숨을 바친다.", 4001290, 4001293),
    ("bassanio", "friend_of", "antonio", "바사니오가 재판에서 안토니오의 목숨이 아내의 목숨보다 소중하다고 선언한다.", 4001294, 4001299),
]


async def seed() -> None:
    driver = get_neo4j_driver()
    async with driver.session() as session:
        for node in _NODES:
            await session.run(
                """
                MERGE (c:Character {character_id: $character_id})
                SET c.name_ko = $name_ko, c.name_en = $name_en, c.description = $description
                """,
                **node,
            )
        print(f"노드 {len(_NODES)}개 시딩 완료.")

        for from_id, relation_type, to_id, description, ftln_start, ftln_end in _EDGES:
            # 관계 타입은 파라미터화할 수 없다(Cypher 제약) — 다만 _EDGES가
            # 코드에 고정된 리터럴이지 외부 입력이 아니므로 인젝션 위험은 없다.
            await session.run(
                f"""
                MATCH (a:Character {{character_id: $from_id}})
                MATCH (b:Character {{character_id: $to_id}})
                MERGE (a)-[r:{relation_type}]->(b)
                SET r.description = $description,
                    r.evidence_ftln_start = $ftln_start,
                    r.evidence_ftln_end = $ftln_end
                """,
                from_id=from_id,
                to_id=to_id,
                description=description,
                ftln_start=ftln_start,
                ftln_end=ftln_end,
            )
        print(f"관계 {len(_EDGES)}개 시딩 완료.")


async def main() -> None:
    try:
        await seed()
    finally:
        await close_neo4j_driver()


if __name__ == "__main__":
    asyncio.run(main())
