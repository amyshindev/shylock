"""Correct jessica evidence: it's Jessica's elopement letter to Lorenzo, not a note found by Shylock."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "021_fix_jessica_letter_evidence"
down_revision: Union[str, None] = "020_drop_portia_stances_json"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_ROW: dict[str, object] = {
    "evidence_id": "jessica",
    "quote": (
        "I must needs tell thee all. She hath directed / "
        "How I shall take her from her father's house, / "
        "What gold and jewels she is furnished with, / "
        "What page's suit she hath in readiness."
    ),
    "act_scene": "2.4",
    "icon": "jessica",
    "description": "로렌조에게 보낸 편지. 아버지 집을 빠져나올 방법과, 챙겨 나올 금과 보석, 준비해 둔 시동 옷차림까지 적어놓았다.",
    "source_ftln_start": 2004033,
    "source_ftln_end": 2004036,
}

_OLD_ROW: dict[str, object] = {
    "evidence_id": "jessica",
    "quote": "I would my daughter were dead at my foot, and the jewels in her ear.",
    "act_scene": "3.1",
    "icon": "jessica",
    "description": "딸이 도망치며 남긴 흔적. 돈과 보석을 훔쳐갔다.",
    "source_ftln_start": 3001400,
    "source_ftln_end": 3001420,
}

_UPDATE_SQL = sa.text(
    """
    UPDATE evidence SET
        quote = :quote,
        act_scene = :act_scene,
        icon = :icon,
        description = :description,
        source_ftln_start = :source_ftln_start,
        source_ftln_end = :source_ftln_end
    WHERE evidence_id = :evidence_id
    """
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(_UPDATE_SQL, _NEW_ROW)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(_UPDATE_SQL, _OLD_ROW)
