"""Add character_nodes/character_relations: a small hand-curated relationship
graph over the play's dramatis personae, for multi-hop reasoning pgvector
search can't do on its own (e.g. "Portia is married to Bassanio, who is
financed by Antonio, who is Shylock's debtor -> Portia has a conflict of
interest presiding over this trial" — a chain across three separate lines
that never sit close enough in embedding space to surface together).

Scope deliberately kept to ~7 nodes / ~15 edges, hand-authored rather than
LLM-extracted — same reasoning as CURATED_EVIDENCE (curated_evidence.py):
this is small, game-mechanic-adjacent data where precision matters more than
automation, not a corpus-scale extraction problem. Duke, Launcelot, and Crowd
are deliberately excluded — Duke barely appears in this adaptation (see
todo-list.md), Launcelot never actually appears despite being a skill ID, and
Crowd is a collective, not an individual with 1:1 relationships.

Every edge carries an evidence_ftln_start/end range in the same encoding as
Evidence.source_ftln_range (act*1_000_000 + scene*1_000 + line) — verified
against the live play_lines corpus before writing this migration, not
invented. Symmetric relationships (married_to, friend_of, father_of/
daughter_of) are stored as two directional rows rather than one undirected
row, so a recursive CTE walking from_character_id -> to_character_id never
needs special-cased reverse-direction logic.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "031_character_relation_graph"
down_revision: Union[str, None] = "030_local_embed_hnsw"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

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

# (from, relation_type, to, description, ftln_start, ftln_end) — ftln ranges
# verified against play_lines before this migration was written, see module
# docstring.
_EDGES: list[tuple[str, str, str, str, int, int]] = [
    (
        "portia", "married_to", "bassanio",
        "포샤가 바사니오에게 반지를 주며 아내가 되기로 서약한다.",
        3002169, 3002175,
    ),
    (
        "bassanio", "married_to", "portia",
        "바사니오가 포샤의 반지 서약을 받아들인다.",
        3002169, 3002175,
    ),
    (
        "antonio", "guarantor_for", "bassanio",
        "안토니오가 자신의 재산과 목숨을 바사니오를 위해 내놓는다.",
        1001145, 1001146,
    ),
    (
        "bassanio", "financed_by", "antonio",
        "바사니오가 안토니오에게 갚아야 할 빚이 있음을 인정한다.",
        1001138, 1001141,
    ),
    (
        "antonio", "debtor_of", "shylock",
        "안토니오가 살 1파운드를 담보로 샤일록에게 돈을 빌린다.",
        1003158, 1003165,
    ),
    (
        "shylock", "creditor_of", "antonio",
        "샤일록이 안토니오에게 살 1파운드를 담보로 돈을 빌려준다.",
        1003158, 1003165,
    ),
    (
        "antonio", "discriminated_against", "shylock",
        "안토니오가 샤일록을 '개'라 부르며 침을 뱉었다.",
        1003120, 1003140,
    ),
    (
        "shylock", "enemy_of", "antonio",
        "샤일록이 자신을 모욕한 안토니오를 원수로 여긴다.",
        1003120, 1003140,
    ),
    (
        "antonio", "enemy_of", "shylock",
        "안토니오가 샤일록을 모욕할 만큼 적대한다.",
        1003120, 1003140,
    ),
    (
        "tubal", "friend_of", "shylock",
        "투발이 샤일록을 위해 달아난 제시카를 직접 찾아다닌다.",
        3001079, 3001082,
    ),
    (
        "shylock", "friend_of", "tubal",
        "샤일록이 투발에게 제시카의 행방을 묻고 소식을 의지한다.",
        3001079, 3001082,
    ),
    (
        "shylock", "father_of", "jessica",
        "샤일록이 제시카를 '내 살과 피'라 부른다.",
        3001034, 3001037,
    ),
    (
        "jessica", "daughter_of", "shylock",
        "제시카가 샤일록의 딸이다.",
        3001034, 3001037,
    ),
    (
        "lorenzo", "married_to", "jessica",
        "로렌조가 벨몬트에서 제시카와 함께 밤을 노래한다.",
        5001066, 5001067,
    ),
    (
        "jessica", "married_to", "lorenzo",
        "제시카가 로렌조와 함께 벨몬트에 정착해 있다.",
        5001066, 5001067,
    ),
]


def upgrade() -> None:
    conn = op.get_bind()

    op.create_table(
        "character_nodes",
        sa.Column("character_id", sa.String(32), primary_key=True),
        sa.Column("name_ko", sa.String(32), nullable=False),
        sa.Column("name_en", sa.String(32), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
    )
    op.create_table(
        "character_relations",
        sa.Column("relation_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "from_character_id", sa.String(32),
            sa.ForeignKey("character_nodes.character_id"), nullable=False,
        ),
        sa.Column(
            "to_character_id", sa.String(32),
            sa.ForeignKey("character_nodes.character_id"), nullable=False,
        ),
        sa.Column("relation_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("evidence_ftln_start", sa.Integer, nullable=False),
        sa.Column("evidence_ftln_end", sa.Integer, nullable=False),
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO character_nodes (character_id, name_ko, name_en, description)
            VALUES (:character_id, :name_ko, :name_en, :description)
            """
        ),
        _NODES,
    )

    for from_id, relation_type, to_id, description, ftln_start, ftln_end in _EDGES:
        conn.execute(
            sa.text(
                """
                INSERT INTO character_relations
                    (from_character_id, relation_type, to_character_id, description,
                     evidence_ftln_start, evidence_ftln_end)
                VALUES (:from_id, :relation_type, :to_id, :description, :start, :end)
                """
            ),
            {
                "from_id": from_id,
                "relation_type": relation_type,
                "to_id": to_id,
                "description": description,
                "start": ftln_start,
                "end": ftln_end,
            },
        )


def downgrade() -> None:
    op.drop_table("character_relations")
    op.drop_table("character_nodes")
