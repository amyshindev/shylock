"""Seed blood_reveal item evidence (whetted_knife, bond_wording)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_seed_blood_reveal_items"
down_revision: Union[str, None] = "018_add_portia_stances_json"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UPSERT_SQL = sa.text(
    """
    INSERT INTO evidence (
        evidence_id, quote, act_scene, icon, description, source_ftln_start, source_ftln_end
    ) VALUES (
        :evidence_id, :quote, :act_scene, :icon, :description, :source_ftln_start, :source_ftln_end
    )
    ON CONFLICT (evidence_id) DO UPDATE SET
        quote = EXCLUDED.quote,
        act_scene = EXCLUDED.act_scene,
        icon = EXCLUDED.icon,
        description = EXCLUDED.description,
        source_ftln_start = EXCLUDED.source_ftln_start,
        source_ftln_end = EXCLUDED.source_ftln_end
    """
)

_EVIDENCE_ROWS: tuple[dict[str, object], ...] = (
    {
        "evidence_id": "whetted_knife",
        "quote": (
            "Why dost thou whet thy knife so earnestly? — "
            "To cut the forfeiture from that bankrupt there."
        ),
        "act_scene": "4.1",
        "icon": "whetted_knife",
        "description": (
            "재판 내내 조용히 갈아온 칼. 포샤의 선언과 함께, "
            "정의를 집행할 도구는 휘두를 수 없는 물건이 되었다."
        ),
        "source_ftln_start": 4001300,
        "source_ftln_end": 4001320,
    },
    {
        "evidence_id": "bond_wording",
        "quote": (
            "This bond doth give thee here no jot of blood; "
            "the words expressly are 'a pound of flesh.'"
        ),
        "act_scene": "4.1",
        "icon": "bond_wording",
        "description": "'살 1파운드.' 문구에는 정확히 그렇게만 쓰여 있다. 더도, 덜도 아니게.",
        "source_ftln_start": 4001850,
        "source_ftln_end": 4001870,
    },
)


def upgrade() -> None:
    conn = op.get_bind()
    for row in _EVIDENCE_ROWS:
        conn.execute(_UPSERT_SQL, row)


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM evidence WHERE evidence_id IN ('whetted_knife','bond_wording')"
        )
    )
