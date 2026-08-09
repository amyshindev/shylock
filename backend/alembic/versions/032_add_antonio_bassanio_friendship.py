"""Add the missing antonio<->bassanio friend_of edge pair to character_relations.

031 gave Antonio and Bassanio two edges (guarantor_for / financed_by), both
about the loan, but never an edge for the friendship itself — even though
it's one of the play's central relationships (arguably more textually
prominent than tubal<->shylock's friend_of, which 031 did include). It only
existed as prose inside bassanio's node description ("안토니오의 친구..."),
never as its own relation row, so trace_relationship()/get_relations_for()
couldn't surface it and an LLM answering "안토니오랑 바사니오는 무슨
사이인가요?" had to fall back on its own background knowledge instead of the
curated graph.

Evidence: Act 4 Scene 1 (the trial), verified against play_lines — Antonio
calls Bassanio his friend while facing execution, and Bassanio publicly
declares Antonio's life dearer to him than his own wife's.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "032_antonio_bassanio_friend_of"
down_revision: Union[str, None] = "031_character_relation_graph"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EDGES: list[tuple[str, str, str, str, int, int]] = [
    (
        "antonio", "friend_of", "bassanio",
        "안토니오가 처형을 앞두고 바사니오를 '벗'이라 부르며 그를 위해 기꺼이 목숨을 바친다.",
        4001290, 4001293,
    ),
    (
        "bassanio", "friend_of", "antonio",
        "바사니오가 재판에서 안토니오의 목숨이 아내의 목숨보다 소중하다고 선언한다.",
        4001294, 4001299,
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
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
    conn = op.get_bind()
    for from_id, relation_type, to_id, _description, _start, _end in _EDGES:
        conn.execute(
            sa.text(
                """
                DELETE FROM character_relations
                WHERE from_character_id = :from_id
                  AND to_character_id = :to_id
                  AND relation_type = :relation_type
                """
            ),
            {"from_id": from_id, "to_id": to_id, "relation_type": relation_type},
        )
